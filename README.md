# Universal DevOps Pipeline

A reusable DevOps pipeline that can be applied to any project (Java Spring Boot, React, Node.js, etc.).

## 🚀 Quick Start

### 1. Setup Pipeline for Your Project
```bash
python3 setup.py /path/to/your/project <app-type> <project-name>
```

**Supported app types:**
- `java-spring-boot` - For Spring Boot applications
- `react-frontend` - For React applications  
- `node-backend` - For Node.js applications

**Example:**
```bash
# For backend
python3 setup.py ../MyApp java-spring-boot myapp-backend

# For frontend  
python3 setup.py ../MyAppFrontend react-frontend myapp-frontend
```

### 2. What Gets Created
```
your-project/
├── devops/
│   ├── terraform/          # Infrastructure as code
│   ├── ansible/           # Deployment automation
│   ├── docker/           # Container configuration
│   └── scripts/          # Deployment scripts
├── Dockerfile            # Container definition
├── Jenkinsfile          # CI/CD pipeline
└── .github/workflows/   # GitHub Actions
```

## 🏗️ Architecture Overview

```mermaid
flowchart TD
    %% Developer Section
    DEV[👨‍💻 Developer<br/>Code Changes] --> GIT[📤 Git Push]
    
    %% CI/CD Pipeline
    GIT --> BUILD[🔨 Build<br/>Maven/npm]
    BUILD --> TEST[🧪 Test<br/>JUnit/Jest]
    TEST --> DOCKER[🐳 Docker Build<br/>Container Image]
    DOCKER --> APPROVAL{🔐 Manual Approval<br/>Production Gate}
    
    %% Infrastructure Layer
    APPROVAL -->|Approved| ECR[📦 Amazon ECR<br/>Container Registry]
    ECR --> TERRAFORM[🏗️ Terraform<br/>Infrastructure as Code]
    
    %% AWS Infrastructure
    TERRAFORM --> VPC[🌐 AWS VPC<br/>Network Isolation]
    VPC --> ALB[⚖️ Application<br/>Load Balancer]
    VPC --> EC2[💻 EC2 Auto Scaling<br/>2-6 Instances]
    VPC --> RDS[🗄️ RDS Database<br/>PostgreSQL/MySQL]
    
    %% Configuration Management
    TERRAFORM --> ANSIBLE[⚙️ Ansible<br/>Configuration Management]
    ANSIBLE --> CLOUDWATCH[📊 CloudWatch<br/>Monitoring]
    ANSIBLE --> PARAMS[🔑 Parameter Store<br/>Secrets Management]
    ANSIBLE --> SECURITY[🛡️ Security Groups<br/>Network Rules]
    
    %% Deployment Flow
    ANSIBLE --> DEPLOY[🚀 Application<br/>Deployment]
    DEPLOY --> HEALTH[❤️ Health Check<br/>Validation]
    HEALTH --> ROLLBACK[🔄 Rollback<br/>Manual Trigger]
    
    %% Styling
    classDef devOps fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef aws fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef cicd fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef security fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    
    class DEV,GIT devOps
    class BUILD,TEST,DOCKER,APPROVAL cicd
    class ECR,VPC,ALB,EC2,RDS,CLOUDWATCH,PARAMS aws
    class TERRAFORM,ANSIBLE,DEPLOY,HEALTH,ROLLBACK devOps
    class SECURITY security
```

### 🔄 Deployment Flow Diagram

```mermaid
sequenceDiagram
    participant Dev as 👨‍💻 Developer
    participant GH as 🐙 GitHub Actions
    participant ECR as 📦 Amazon ECR
    participant TF as 🏗️ Terraform
    participant ANS as ⚙️ Ansible
    participant AWS as ☁️ AWS Infrastructure
    participant APP as 🚀 Application
    
    Dev->>GH: git push
    GH->>GH: Build & Test
    GH->>ECR: Push Docker Image
    GH->>GH: Wait for Approval
    Note over GH: Manual Production Gate
    GH->>TF: Apply Infrastructure
    TF->>AWS: Create/Update Resources
    AWS-->>TF: Resources Ready
    TF->>ANS: Trigger Deployment
    ANS->>ECR: Pull Docker Image
    ANS->>AWS: Deploy to EC2 Instances
    AWS->>APP: Start Application
    APP-->>ANS: Health Check Response
    ANS-->>GH: Deployment Complete
    
    Note over Dev,APP: Zero-downtime deployment with rollback capability
```

### 🛠️ Technology Stack

```mermaid
mindmap
  root((DevOps Pipeline))
    CI/CD
      GitHub Actions
      Git Version Control
      Manual Approvals
    Infrastructure
      Terraform
      Ansible
      AWS CloudFormation
    Containerization
      Docker
      Amazon ECR
      Container Runtime
    AWS Services
      EC2 Auto Scaling
      VPC Networking
      Application Load Balancer
      RDS Database
      CloudWatch Monitoring
      Parameter Store
      Security Groups
    Applications
      Java Spring Boot
        Maven
        JUnit Testing
      React Frontend
        npm
        Jest Testing
      Node.js Backend
        npm
        Jest Testing
```

**CI/CD & Version Control:**
- GitHub Actions (Workflow automation)
- Git (Version control)

**Infrastructure as Code:**
- Terraform (AWS resource provisioning)
- Ansible (Configuration management)

**Containerization:**
- Docker (Application containerization)
- Amazon ECR (Container registry)

**AWS Services:**
- EC2 (Compute instances)
- VPC (Network isolation)
- Application Load Balancer (Traffic distribution)
- Auto Scaling Groups (Dynamic scaling)
- RDS (Managed databases)
- CloudWatch (Monitoring & logging)
- Parameter Store (Secrets management)
- Security Groups (Network security)

**Application Support:**
- Java Spring Boot (Maven, JUnit)
- React (npm, Jest)
- Node.js (npm, Jest)

## 📖 Documentation
- [Complete Beginner Guide](docs/BEGINNER_GUIDE.md) - Step-by-step setup
- [Advanced Configuration](docs/ADVANCED.md) - Customization options

## 🎯 Features
- ✅ Multi-environment support (staging/production)
- ✅ Auto-scaling infrastructure
- ✅ Zero-downtime deployments
- ✅ Health checks and monitoring
- ✅ Easy rollback
- ✅ Security best practices

## 🔧 Requirements
- AWS Account
- GitHub Account
- Terraform installed
- Ansible installed
- Docker installed

## 🌟 Benefits of Reusable Pipeline
1. **Consistency** - Same deployment process across all projects
2. **Time Saving** - No need to recreate DevOps setup for each project
3. **Best Practices** - Built-in security and reliability features
4. **Easy Updates** - Update pipeline once, apply to all projects
5. **Team Collaboration** - Standardized process for entire team