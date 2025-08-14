#!/bin/bash

# ECS Rollback Script
# Usage: ./ecs-rollback.sh <project-name> <target-commit-sha> <aws-region>

PROJECT_NAME=$1
TARGET_COMMIT=$2
AWS_REGION=${3:-us-east-1}

if [ -z "$PROJECT_NAME" ]; then
    echo "Error: Project name is required"
    echo "Usage: $0 <project-name> [target-commit-sha] [aws-region]"
    exit 1
fi

CLUSTER_NAME="${PROJECT_NAME}-cluster"
SERVICE_NAME="${PROJECT_NAME}-service"

echo "🔄 Starting ECS rollback for project: $PROJECT_NAME"

# Get target image tag
if [ -n "$TARGET_COMMIT" ]; then
    TARGET_TAG="$TARGET_COMMIT"
else
    echo "Getting previous image from ECR..."
    TARGET_TAG=$(aws ecr describe-images --repository-name $PROJECT_NAME \
        --region $AWS_REGION \
        --query 'sort_by(imageDetails,&imagePushedAt)[-2].imageTags[0]' \
        --output text)
fi

if [ -z "$TARGET_TAG" ] || [ "$TARGET_TAG" = "None" ]; then
    echo "❌ No previous image found for rollback"
    exit 1
fi

echo "Rolling back to image tag: $TARGET_TAG"

# Get ECR registry URL
ECR_REGISTRY=$(aws ecr describe-registry --region $AWS_REGION --query 'registryId' --output text).dkr.ecr.$AWS_REGION.amazonaws.com

# Get current task definition
CURRENT_TASK_DEF=$(aws ecs describe-services \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $AWS_REGION \
    --query 'services[0].taskDefinition' \
    --output text)

echo "Current task definition: $CURRENT_TASK_DEF"

# Get task definition details
TASK_DEFINITION=$(aws ecs describe-task-definition \
    --task-definition $CURRENT_TASK_DEF \
    --region $AWS_REGION \
    --query 'taskDefinition' \
    --output json)

# Update image URI in task definition
NEW_TASK_DEFINITION=$(echo $TASK_DEFINITION | jq --arg IMAGE "$ECR_REGISTRY/$PROJECT_NAME:$TARGET_TAG" \
    '.containerDefinitions[0].image = $IMAGE | del(.taskDefinitionArn) | del(.revision) | del(.status) | del(.requiresAttributes) | del(.placementConstraints) | del(.compatibilities) | del(.registeredAt) | del(.registeredBy)')

# Register new task definition
NEW_TASK_DEF_ARN=$(echo $NEW_TASK_DEFINITION | aws ecs register-task-definition \
    --region $AWS_REGION \
    --cli-input-json file:///dev/stdin \
    --query 'taskDefinition.taskDefinitionArn' \
    --output text)

echo "New rollback task definition: $NEW_TASK_DEF_ARN"

# Update ECS service with rollback task definition
aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service $SERVICE_NAME \
    --task-definition $NEW_TASK_DEF_ARN \
    --region $AWS_REGION

# Wait for rollback deployment to complete
echo "Waiting for ECS service rollback to stabilize..."
aws ecs wait services-stable \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $AWS_REGION

echo "✅ ECS rollback completed successfully!"

# Get load balancer DNS for verification
LB_DNS=$(aws elbv2 describe-load-balancers \
    --names ${PROJECT_NAME}-alb \
    --region $AWS_REGION \
    --query 'LoadBalancers[0].DNSName' \
    --output text 2>/dev/null || echo "")

if [ -n "$LB_DNS" ]; then
    echo "🌐 Application URL: http://$LB_DNS"
fi

echo "🚀 ECS Cluster: $CLUSTER_NAME"
echo "⚙️ ECS Service: $SERVICE_NAME"