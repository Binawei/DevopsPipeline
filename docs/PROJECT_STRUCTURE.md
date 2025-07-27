# DevOps Pipeline Project Structure & Internal Implementation

## 🏗️ **Active Project Structure**

```
DevOpsPipeline/
├── .github/workflows/          # GitHub Actions workflows (THE CORE ENGINE)
│   ├── build-and-deploy.yml   # ✅ Manual approval workflow
│   ├── deploy-backend.yml     # ✅ Backend deployment workflow  
│   ├── deploy-frontend.yml    # ✅ Frontend deployment workflow
│   ├── setup-infrastructure.yml # ✅ Infrastructure creation
│   ├── setup-project.yml      # ✅ All-in-one deployment
│   └── publish-pipeline.yml   # ✅ Pipeline publishing
├── templates/                  # Template files for projects
│   ├── common/                # ✅ Shared infrastructure templates
│   │   ├── terraform/main.tf  # ✅ AWS infrastructure definition
│   │   └── ansible/deploy.yml # ✅ Deployment automation
│   ├── java-spring-boot/      # ✅ Java-specific templates
│   │   └── docker/Dockerfile  # ✅ Java containerization
│   ├── react-frontend/        # ✅ React-specific templates
│   │   ├── docker/Dockerfile  # ✅ React build & nginx setup
│   │   └── docker/nginx.conf  # ✅ Nginx configuration
│   ├── github-workflows/      # ✅ Workflow templates for projects
│   │   ├── backend-deploy.yml # ✅ Backend workflow template
│   │   └── frontend-deploy.yml # ✅ Frontend workflow template
│   ├── simple-deploy.yml      # ✅ Simple deployment template
│   └── manual-approval-deploy.yml # ✅ Manual approval template
├── docs/                      # Documentation
│   ├── BEGINNER_GUIDE.md     # ✅ Pipeline setup guide
│   └── PROJECT_STRUCTURE.md  # ✅ This file
├── pipeline-config.yml        # ✅ Default configurations
├── setup.py                   # ✅ Legacy setup script
├── COMPLETE-USAGE-GUIDE.md   # ✅ Usage instructions
├── MANUAL-APPROVAL-USAGE.md  # ✅ Manual approval guide
├── SIMPLE-USAGE.md           # ✅ Simple usage guide
└── README.md                  # ✅ Main documentation
```

---

## 🔧 **Core Workflow Files - Internal Implementation**

### **1. `build-and-deploy.yml` - Manual Approval Workflow**

**Purpose**: Main workflow with manual approval gate between build and deploy

**Internal Flow**:
```yaml
# STEP 1: Build Stage (Always Runs)
build:
  - Checkout project code
  - Login to AWS ECR
  - Build Docker image from project's Dockerfile
  - Push image to ECR with git SHA tag
  - Output image tag for next stage

# STEP 2: Approval Gate (Only on main/master)
deploy-approval:
  - Requires manual approval via GitHub environment
  - Shows "Review deployments" button
  - Waits for user to click approve

# STEP 3: Deploy Stage (After Approval)
deploy:
  - Check if AWS infrastructure exists
  - Create infrastructure if first deployment
  - Get EC2 instance IPs from Auto Scaling Group
  - Deploy Docker container using Ansible
  - Verify deployment with health checks
```

**Key Implementation Details**:
- Uses `workflow_call` to be reusable by other repos
- `environment: production-approval` creates approval gate
- `needs: [build, deploy-approval]` ensures proper sequence
- `if: github.ref == 'refs/heads/main'` restricts deployment to main branch

### **2. `setup-infrastructure.yml` - Infrastructure Creation**

**Purpose**: Creates AWS infrastructure automatically on first deployment

**Internal Flow**:
```yaml
# STEP 1: Get Pipeline Templates
- Checkout DevOpsPipeline repo to access Terraform templates

# STEP 2: Generate Configuration
- Copy terraform templates to temporary directory
- Generate terraform.tfvars with project-specific values
- Configure AWS credentials

# STEP 3: Deploy Infrastructure
- terraform init (download providers)
- terraform plan (show what will be created)
- terraform apply -auto-approve (create resources)

# STEP 4: Create Ansible Inventory
- Query AWS for EC2 instance IPs from Auto Scaling Group
- Generate inventory files for staging/production
- Commit files back to project repo
```

**Key Implementation Details**:
- Uses `repository: ${{ github.repository_owner }}/DevOpsPipeline` to access templates
- Dynamically generates `terraform.tfvars` with input parameters
- Queries AWS API to get actual EC2 IPs after infrastructure creation
- Commits generated files back to project repo for future deployments

### **3. `deploy-backend.yml` & `deploy-frontend.yml` - App-Specific Deployment**

**Purpose**: Specialized workflows for different application types

**Internal Flow**:
```yaml
# STEP 1: Setup Infrastructure (if staging environment)
setup-infrastructure:
  - Calls setup-infrastructure.yml workflow
  - Only runs on first staging deployment

# STEP 2: Deploy Application
deploy:
  - Build and push Docker image
  - Setup SSH keys for server access
  - Install Ansible for deployment automation
  - Run Ansible playbook to deploy containers
  - Perform health checks
```

**Key Implementation Details**:
- `if: ${{ inputs.environment == 'staging' }}` ensures infrastructure setup only on first deployment
- `needs: [setup-infrastructure]` with `if: always()` continues even if infrastructure setup is skipped
- Uses different ports and health check paths based on `app_type` input

### **4. `setup-project.yml` - All-in-One Deployment**

**Purpose**: Single workflow that handles everything (infrastructure + deployment)

**Internal Flow**:
```yaml
# STEP 1: Check Infrastructure
- Query AWS to see if ECR repository exists
- Set flag for infrastructure creation

# STEP 2: Create Infrastructure (if needed)
- Copy Terraform templates
- Generate configuration
- Deploy infrastructure

# STEP 3: Build and Deploy
- Build Docker image
- Get EC2 instance IPs
- Deploy using Ansible
```

**Key Implementation Details**:
- `aws ecr describe-repositories` checks if infrastructure exists
- Combines infrastructure setup and deployment in single job
- Creates temporary Ansible inventory on-the-fly

---

## 📁 **Template Files - Internal Implementation**

### **1. `templates/common/terraform/main.tf` - Infrastructure Definition**

**Purpose**: Defines AWS infrastructure using Infrastructure as Code

**What It Creates**:
```hcl
# Core Infrastructure
- VPC with public subnets across 2 availability zones
- Internet Gateway and routing tables
- Security Groups (firewall rules)

# Container Registry
- ECR repository for Docker images
- Image scanning enabled

# Load Balancing
- Application Load Balancer (ALB)
- Target Group for health checks
- Listener rules for traffic routing

# Auto Scaling
- Launch Template with user data script
- Auto Scaling Group (2-6 instances)
- Health checks and scaling policies
```

**Key Implementation Details**:
- Uses `dynamic` blocks to configure different ports based on app type
- `data.aws_availability_zones.available` ensures multi-AZ deployment
- `templatefile()` function injects variables into user data script
- Outputs ECR URL and Load Balancer DNS for other workflows

### **2. `templates/common/ansible/deploy.yml` - Deployment Automation**

**Purpose**: Automates application deployment to EC2 instances

**Internal Flow**:
```yaml
# STEP 1: Container Management
- Login to ECR using AWS credentials
- Pull latest Docker image
- Stop and remove existing container

# STEP 2: Deploy New Version
- Start new container with updated image
- Configure port mapping based on app type
- Set environment variables

# STEP 3: Health Verification
- Wait for application to start
- Perform health check requests
- Retry up to 30 times with 10-second delays
```

**Key Implementation Details**:
- Uses `docker_container` module for container lifecycle management
- `ignore_errors: yes` prevents deployment failure if no existing container
- Dynamic port mapping: `'80:80' if app_type == 'react-frontend' else '8080:8080'`
- Health check URLs vary by app type (`/health` vs `/actuator/health`)

### **3. `templates/*/docker/Dockerfile` - Containerization**

**Java Spring Boot Implementation**:
```dockerfile
# Multi-stage build not needed (JAR already built)
FROM openjdk:17-jre-slim    # Minimal JRE image
WORKDIR /app
COPY target/*.jar app.jar   # Copy pre-built JAR
EXPOSE 8080                 # Standard Spring Boot port
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

**React Frontend Implementation**:
```dockerfile
# STAGE 1: Build React app
FROM node:18-alpine as build
COPY package*.json ./       # Copy dependency files first (Docker layer caching)
RUN npm install           # Install dependencies
COPY . .                  # Copy source code
RUN npm run build         # Build production bundle

# STAGE 2: Serve with Nginx
FROM nginx:alpine         # Lightweight web server
COPY --from=build /app/build /usr/share/nginx/html  # Copy built files
COPY nginx.conf /etc/nginx/nginx.conf               # Custom config
EXPOSE 80
```

**Key Implementation Details**:
- Multi-stage builds reduce final image size
- Layer caching optimization (dependencies before source code)
- Security: runs as non-root user where possible
- Health check endpoints configured for monitoring

---

## ⚙️ **Configuration Files - Internal Implementation**

### **1. `pipeline-config.yml` - Default Settings**

**Purpose**: Centralized configuration for pipeline defaults

**Internal Structure**:
```yaml
# Pipeline Metadata
pipeline:
  name: "Universal DevOps Pipeline"
  version: "1.0.0"

# Supported Application Types
app_types:
  - java-spring-boot    # Spring Boot applications
  - react-frontend      # React single-page applications
  - node-backend        # Node.js backend services

# AWS Infrastructure Defaults
defaults:
  aws_region: "us-east-1"      # Default AWS region
  instance_type: "t3.medium"   # EC2 instance size
  min_instances: 2             # Minimum servers
  max_instances: 6             # Maximum servers for auto-scaling

# Environment-Specific Overrides
environments:
  staging:
    instance_count: 2          # Smaller staging environment
    instance_type: "t3.small"
  production:
    instance_count: 3          # Larger production environment
    instance_type: "t3.medium"
```

### **2. `setup.py` - Legacy Setup Script**

**Purpose**: Python script for local project setup (mostly replaced by automated workflows)

**Internal Implementation**:
```python
class PipelineSetup:
    def copy_templates(self, app_type, target_dir):
        # Copy app-specific templates (Dockerfile, etc.)
        template_dir = Path("templates") / app_type
        shutil.copytree(template_dir, target_dir, dirs_exist_ok=True)
        
        # Copy common templates (Terraform, Ansible)
        common_dir = Path("templates/common")
        shutil.copytree(common_dir, target_dir, dirs_exist_ok=True)
    
    def generate_configs(self, app_type, project_name, target_dir):
        # Generate terraform.tfvars with project-specific values
        # Generate Ansible inventory templates
        # Generate GitHub workflow files
```

**Key Implementation Details**:
- Uses `shutil.copytree()` for recursive file copying
- Template variable replacement with f-strings
- Graceful handling of existing directories with `dirs_exist_ok=True`
- Generates both infrastructure and workflow files

---

## 🔄 **Workflow Execution Flow**

### **Complete Deployment Sequence**:

```
1. Developer pushes code to main branch
   ↓
2. GitHub triggers build-and-deploy.yml
   ↓
3. BUILD STAGE:
   - Checkout project code
   - Build Docker image from Dockerfile
   - Push to AWS ECR with git SHA tag
   ↓
4. APPROVAL STAGE (main/master only):
   - Show "Review deployments" button
   - Wait for manual approval
   ↓
5. DEPLOY STAGE:
   - Check if infrastructure exists (ECR repository check)
   - If not exists: Run setup-infrastructure.yml
     • Copy Terraform templates
     • Generate terraform.tfvars
     • Deploy AWS infrastructure (VPC, ALB, ASG, etc.)
     • Get EC2 instance IPs
   - Deploy application:
     • Setup SSH keys
     • Install Ansible
     • Run deployment playbook
     • Perform health checks
   ↓
6. Application is live on Load Balancer URL
```

### **Error Handling & Recovery**:
- Infrastructure creation is idempotent (can run multiple times safely)
- Container deployment includes rollback on health check failure
- SSH key setup includes proper permissions (chmod 600)
- Ansible retries health checks up to 30 times
- All AWS API calls include error handling

This implementation provides enterprise-grade CI/CD with minimal configuration required from project teams - just a Dockerfile and workflow file!