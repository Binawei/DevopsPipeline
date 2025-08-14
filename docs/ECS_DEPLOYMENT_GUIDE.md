# ECS Fargate Deployment Guide

## Overview

This guide explains how the DevOps pipeline uses Amazon ECS Fargate for serverless container deployment, replacing the traditional EC2 + Ansible approach.

## Architecture Benefits

### ECS Fargate vs EC2 Comparison

| Feature | EC2 + Ansible | ECS Fargate |
|---------|---------------|-------------|
| **Server Management** | Manual (SSH, patching, scaling) | Fully managed by AWS |
| **Deployment Time** | 15-20 minutes | 5-8 minutes |
| **Scaling Speed** | 3-4 minutes (new instances) | 30 seconds (new tasks) |
| **Configuration** | Ansible playbooks + SSH | Task definitions only |
| **Security** | SSH keys, server access | No server access needed |
| **Cost** | Always-on instances | Pay per running task |

## ECS Components

### 1. ECS Cluster
- **Purpose**: Logical grouping of compute resources
- **Type**: Fargate (serverless)
- **Naming**: `{project-name}-cluster`

### 2. Task Definition
- **Purpose**: Blueprint for containers
- **Contains**: Image URI, CPU/memory, environment variables, secrets
- **Versioning**: New revision for each deployment

### 3. ECS Service
- **Purpose**: Maintains desired number of running tasks
- **Features**: Load balancer integration, health checks, rolling deployments
- **Scaling**: Automatic based on CPU/memory metrics

## Deployment Process

### Step 1: Build and Push Image
```bash
# GitHub Actions builds and pushes to ECR
docker build -t $ECR_REGISTRY/$PROJECT_NAME:$COMMIT_SHA .
docker push $ECR_REGISTRY/$PROJECT_NAME:$COMMIT_SHA
```

### Step 2: Infrastructure Provisioning (Terraform)
```hcl
# Creates ECS cluster, service, task definition
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"
}

resource "aws_ecs_service" "app" {
  name            = "${var.project_name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 2
  launch_type     = "FARGATE"
}
```

### Step 3: Service Update (GitHub Actions)
```bash
# Update task definition with new image
NEW_TASK_DEF_ARN=$(aws ecs register-task-definition \
  --family $PROJECT_NAME \
  --container-definitions '[{
    "name": "'$PROJECT_NAME'",
    "image": "'$ECR_REGISTRY/$PROJECT_NAME:$IMAGE_TAG'",
    "portMappings": [{"containerPort": 8080}]
  }]' \
  --query 'taskDefinition.taskDefinitionArn' \
  --output text)

# Update ECS service
aws ecs update-service \
  --cluster $PROJECT_NAME-cluster \
  --service $PROJECT_NAME-service \
  --task-definition $NEW_TASK_DEF_ARN
```

### Step 4: Rolling Deployment
- ECS automatically starts new tasks with updated image
- Health checks validate new tasks before routing traffic
- Old tasks are terminated after new ones are healthy
- Zero downtime achieved through load balancer integration

## Configuration Management

### Environment Variables
```json
{
  "environment": [
    {
      "name": "SPRING_PROFILES_ACTIVE",
      "value": "production"
    }
  ]
}
```

### Secrets Management (Parameter Store)
```json
{
  "secrets": [
    {
      "name": "SPRING_DATASOURCE_USERNAME",
      "valueFrom": "/myapp/database/username"
    },
    {
      "name": "SPRING_DATASOURCE_PASSWORD",
      "valueFrom": "/myapp/database/password"
    }
  ]
}
```

## Health Checks

### Application Health Check
```json
{
  "healthCheck": {
    "command": [
      "CMD-SHELL",
      "curl -f http://localhost:8080/actuator/health || exit 1"
    ],
    "interval": 30,
    "timeout": 5,
    "retries": 3,
    "startPeriod": 60
  }
}
```

### Load Balancer Health Check
```hcl
resource "aws_lb_target_group" "app" {
  health_check {
    path                = "/actuator/health"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }
}
```

## Auto Scaling

### CPU-based Scaling
```hcl
resource "aws_appautoscaling_target" "ecs_target" {
  max_capacity       = 6
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.app.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "scale_up" {
  name               = "${var.project_name}-scale-up"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}
```

## Monitoring and Logging

### CloudWatch Logs
```json
{
  "logConfiguration": {
    "logDriver": "awslogs",
    "options": {
      "awslogs-group": "/ecs/myapp",
      "awslogs-region": "us-east-1",
      "awslogs-stream-prefix": "ecs"
    }
  }
}
```

### CloudWatch Metrics
- **CPU Utilization**: Average across all tasks
- **Memory Utilization**: Memory usage per task
- **Task Count**: Number of running/pending/stopped tasks
- **Service Events**: Deployment and scaling events

## Rollback Process

### Automatic Rollback
```bash
# Get previous task definition
PREVIOUS_TASK_DEF=$(aws ecs describe-services \
  --cluster $CLUSTER_NAME \
  --services $SERVICE_NAME \
  --query 'services[0].deployments[1].taskDefinition' \
  --output text)

# Rollback to previous version
aws ecs update-service \
  --cluster $CLUSTER_NAME \
  --service $SERVICE_NAME \
  --task-definition $PREVIOUS_TASK_DEF
```

### Manual Rollback Script
```bash
# Use the provided rollback script
./templates/common/scripts/ecs-rollback.sh myapp abc123 us-east-1
```

## Troubleshooting

### Common Issues

1. **Task Fails to Start**
   - Check CloudWatch logs: `/ecs/{project-name}`
   - Verify image exists in ECR
   - Check IAM permissions for task role

2. **Health Check Failures**
   - Verify health endpoint is accessible
   - Check application startup time
   - Review security group rules

3. **Service Not Scaling**
   - Check auto-scaling policies
   - Verify CloudWatch metrics
   - Review service events in ECS console

### Debugging Commands
```bash
# Check service status
aws ecs describe-services --cluster myapp-cluster --services myapp-service

# View task details
aws ecs describe-tasks --cluster myapp-cluster --tasks <task-arn>

# Check service events
aws ecs describe-services --cluster myapp-cluster --services myapp-service \
  --query 'services[0].events[0:10]'

# View logs
aws logs get-log-events --log-group-name /ecs/myapp \
  --log-stream-name ecs/myapp/<task-id>
```

## Cost Optimization

### Right-sizing Resources
- **CPU**: Start with 256 CPU units (0.25 vCPU)
- **Memory**: Start with 512 MB
- **Monitor**: Use CloudWatch to optimize based on actual usage

### Scaling Configuration
- **Min Tasks**: 2 (for high availability)
- **Max Tasks**: 6 (adjust based on expected load)
- **Scale-out**: 70% CPU utilization
- **Scale-in**: 30% CPU utilization

## Security Best Practices

### Task Role Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter",
        "ssm:GetParameters"
      ],
      "Resource": "arn:aws:ssm:*:*:parameter/myapp/*"
    }
  ]
}
```

### Network Security
- Tasks run in private subnets (when configured)
- Security groups restrict access to necessary ports only
- Load balancer provides public access point
- No direct SSH access to containers

## Frontend Deployment (React)

For React applications, the pipeline uses S3 + CloudFront instead of ECS:

### S3 Static Hosting
```bash
# Deploy build files to S3
aws s3 sync build/ s3://myapp-frontend-bucket/ --delete
```

### CloudFront Distribution
- Global CDN for fast content delivery
- HTTPS termination
- Cache invalidation on deployments
- Custom domain support (optional)

## Next Steps

1. **Monitor Performance**: Use CloudWatch dashboards
2. **Optimize Costs**: Adjust task sizing based on metrics
3. **Enhance Security**: Implement private subnets and NAT gateways
4. **Add Features**: Implement blue/green deployments
5. **Scale Globally**: Add multi-region support