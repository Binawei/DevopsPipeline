# How to Use the Reusable DevOps Pipeline

## 1. Deploy This Pipeline to GitHub

1. Push this repository to GitHub (e.g., `your-org/DevOpsPipeline`)
2. The pipeline will auto-publish via GitHub Actions
3. Create a release tag: `git tag v1.0.0 && git push origin v1.0.0`

## 2. Use in Your Projects

### For Backend Applications (Java Spring Boot, Node.js)

In your project's `.github/workflows/deploy.yml`:

```yaml
name: Deploy Backend

on:
  push:
    branches: [main, master]
  workflow_dispatch:

jobs:
  deploy-staging:
    uses: your-org/DevOpsPipeline/.github/workflows/deploy-backend.yml@main
    with:
      project_name: "my-backend-app"
      app_type: "java-spring-boot"
      environment: "staging"
      aws_region: "us-east-1"
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      EC2_SSH_KEY: ${{ secrets.EC2_SSH_KEY }}

  deploy-production:
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    uses: your-org/DevOpsPipeline/.github/workflows/deploy-backend.yml@main
    with:
      project_name: "my-backend-app"
      app_type: "java-spring-boot"
      environment: "production"
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      EC2_SSH_KEY: ${{ secrets.EC2_SSH_KEY }}
```

### For Frontend Applications (React)

```yaml
name: Deploy Frontend

on:
  push:
    branches: [main, master]

jobs:
  deploy-staging:
    uses: your-org/DevOpsPipeline/.github/workflows/deploy-frontend.yml@main
    with:
      project_name: "my-frontend-app"
      app_type: "react-frontend"
      environment: "staging"
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      EC2_SSH_KEY: ${{ secrets.EC2_SSH_KEY }}
```

## 3. Required Secrets

Add these secrets to your project repository:

- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key  
- `EC2_SSH_KEY` - Private SSH key for EC2 access

## 4. Infrastructure Setup

Run once per project to create AWS infrastructure:

```bash
# Clone the pipeline repo
git clone https://github.com/your-org/DevOpsPipeline.git
cd DevOpsPipeline

# Setup infrastructure for your project
python3 setup.py /path/to/your/project java-spring-boot my-app

# Deploy infrastructure
cd /path/to/your/project/devops/terraform
terraform init
terraform plan
terraform apply
```

## 5. What Happens When You Push Code

1. **Build** - Docker image is built from your Dockerfile
2. **Push** - Image pushed to AWS ECR
3. **Deploy** - Ansible deploys to EC2 instances
4. **Health Check** - Verifies deployment success
5. **Rollback** - Auto-rollback if health checks fail

## Benefits

- ✅ **One-time setup** - Reuse across all projects
- ✅ **Consistent deployments** - Same process everywhere
- ✅ **Auto-scaling** - EC2 Auto Scaling Groups
- ✅ **Zero-downtime** - Rolling deployments
- ✅ **Health monitoring** - Built-in health checks
- ✅ **Easy rollbacks** - Automated failure recovery