# Complete Beginner's Guide: Setup DevOps Pipeline

## 🎯 What This Guide Does
Shows you step-by-step how to:
1. **Setup AWS account and credentials**
2. **Deploy this reusable pipeline to GitHub**
3. **Configure everything so other projects can use it**
4. **Test with a sample project**

## 📋 What You Need
- GitHub account
- AWS account (free tier works)
- Basic command line knowledge

---

# PART A: AWS Account Setup (Do Once)

## Step 1: Create AWS Account

### 1.1 Sign Up for AWS
1. **Go to**: https://aws.amazon.com/
2. **Click "Create an AWS Account"**
3. **Enter email, password, account name**
4. **Choose "Personal" account type**
5. **Enter payment information** (free tier available)
6. **Verify phone number**
7. **Choose "Basic support" (free)**
8. **Sign in to AWS Console**

### 1.2 Create IAM User for Pipeline
1. **In AWS Console, search "IAM"** and click it
2. **Click "Users"** in left sidebar
3. **Click "Create user"** button
4. **User name**: `devops-pipeline-user`
5. **Click "Next"**
6. **Select "Attach policies directly"**
7. **Search and check these policies**:
   - `AmazonEC2FullAccess`
   - `AmazonECRFullAccess`
   - `ElasticLoadBalancingFullAccess`
   - `AutoScalingFullAccess`
   - `AmazonVPCFullAccess`
8. **Click "Next"** then **"Create user"**

### 1.3 Create Access Keys
1. **Click on the user** you just created
2. **Click "Security credentials" tab**
3. **Scroll down to "Access keys"**
4. **Click "Create access key"**
5. **Select "Command Line Interface (CLI)"**
6. **Check the confirmation box**
7. **Click "Next"** then **"Create access key"**
8. **🚨 IMPORTANT: Copy and save both**:
   - **Access Key ID** (starts with AKIA...)
   - **Secret Access Key** (long random string)
9. **Click "Done"**

### 1.4 Create EC2 Key Pair
1. **In AWS Console, search "EC2"** and click it
2. **Click "Key Pairs"** in left sidebar
3. **Click "Create key pair"**
4. **Name**: `devops-pipeline-key`
5. **Key pair type**: RSA
6. **Private key file format**: .pem
7. **Click "Create key pair"**
8. **🚨 IMPORTANT: Save the downloaded .pem file safely**

### 1.5 Note Your AWS Region
1. **Look at top-right corner** of AWS Console
2. **Note the region** (e.g., "US East (N. Virginia)" = us-east-1)
3. **Remember this** - you'll need it later

---

# PART B: Deploy Pipeline to GitHub

## Step 2: Setup GitHub Repository

### 2.1 Create Repository
1. **Go to GitHub.com** and sign in
2. **Click "+" icon** → **"New repository"**
3. **Repository name**: `DevOpsPipeline`
4. **Description**: `Reusable DevOps Pipeline for AWS Deployment`
5. **Make it Public** (so other repos can reference it)
6. **Don't add README, .gitignore, or license** (we have files already)
7. **Click "Create repository"**

### 2.2 Push Pipeline Code
```bash
# In your DevOpsPipeline folder (where this guide is)
git init
git add .
git commit -m "Initial DevOps Pipeline setup"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/DevOpsPipeline.git
git push -u origin main
```

### 2.3 Verify Pipeline is Published
1. **Go to your GitHub repo**
2. **Click "Actions" tab**
3. **Should see "Publish Reusable Pipeline" workflow**
4. **Wait for it to complete** (green checkmark)

### 2.4 Create Release Tag
```bash
git tag v1.0.0
git push origin v1.0.0
```

**✅ Your pipeline is now live and ready to use!**

---

# PART C: Test with Sample Project

## Step 3: Create Test Project

### 3.1 Create New Repository
1. **GitHub** → **New repository**
2. **Name**: `test-java-app`
3. **Make it Public**
4. **Add README** (check the box)
5. **Click "Create repository"**

### 3.2 Clone and Setup Test Project
```bash
# Clone the test repo
git clone https://github.com/YOUR_USERNAME/test-java-app.git
cd test-java-app

# Create a simple Java app structure
mkdir -p src/main/java/com/example
mkdir target

# Create a simple JAR file (mock)
echo "Mock JAR content" > target/app.jar
```

### 3.3 Add Dockerfile
Create `Dockerfile`:
```dockerfile
FROM openjdk:17-jre-slim
WORKDIR /app
COPY target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

### 3.4 Add GitHub Workflow
Create `.github/workflows/deploy.yml`:
```yaml
name: Build and Deploy with Manual Approval

on:
  push:
    branches: [main, master, develop, feature/*]
  workflow_dispatch:

jobs:
  build-and-deploy:
    uses: YOUR_USERNAME/DevOpsPipeline/.github/workflows/build-and-deploy.yml@main
    with:
      project_name: "test-java-app"
      app_type: "java-spring-boot"
      aws_region: "us-east-1"
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      EC2_SSH_KEY: ${{ secrets.EC2_SSH_KEY }}
```

### 3.5 Setup GitHub Environment
1. **Go to test repo** → **Settings** → **Environments**
2. **Click "New environment"**
3. **Name**: `production-approval`
4. **Check "Required reviewers"** → Add yourself
5. **Click "Save protection rules"**

### 3.6 Add GitHub Secrets
1. **Settings** → **Secrets and variables** → **Actions**
2. **Add these secrets**:
   - **Name**: `AWS_ACCESS_KEY_ID` **Value**: Your AWS access key from Step 1.3
   - **Name**: `AWS_SECRET_ACCESS_KEY` **Value**: Your AWS secret key from Step 1.3
   - **Name**: `EC2_SSH_KEY` **Value**: Content of your .pem file (open with text editor, copy all)

### 3.7 Test the Pipeline
```bash
# Push to trigger the pipeline
git add .
git commit -m "Add deployment pipeline"
git push origin main
```

### 3.8 Approve Deployment
1. **Go to Actions tab** in your test repo
2. **Click on the running workflow**
3. **Wait for build to complete**
4. **Click "Review deployments"** button
5. **Select "production-approval"**
6. **Click "Approve and deploy"**
7. **Wait for deployment to complete**

### 3.9 Check Your Live App
1. **Scroll to bottom** of deployment logs
2. **Look for Load Balancer URL**
3. **Visit the URL** → Your app should be running!

---

# PART D: Share with Your Team

## Step 4: Documentation for Team

### 4.1 Update Repository README
Add this to your DevOpsPipeline README.md:

```markdown
# DevOps Pipeline

Reusable CI/CD pipeline for deploying applications to AWS EC2.

## Quick Start for Projects

1. Add Dockerfile to your project
2. Add .github/workflows/deploy.yml (see COMPLETE-USAGE-GUIDE.md)
3. Add GitHub secrets (AWS credentials)
4. Push to main branch and approve deployment

## Documentation
- [Complete Usage Guide](COMPLETE-USAGE-GUIDE.md) - How to use in projects
- [Beginner Setup Guide](docs/BEGINNER_GUIDE.md) - Initial setup (this file)
```

### 4.2 Share Repository URL
Give your team this URL: `https://github.com/YOUR_USERNAME/DevOpsPipeline`

They can now use it in their projects by following the [Complete Usage Guide](COMPLETE-USAGE-GUIDE.md).

---

# 🎉 You're Done!

## What You Now Have:

### ✅ **AWS Infrastructure Ready**
- IAM user with proper permissions
- EC2 key pair for server access
- All credentials saved securely

### ✅ **Pipeline Published on GitHub**
- Reusable workflows available
- Automatic infrastructure creation
- Manual approval process

### ✅ **Tested and Working**
- Sample project deployed successfully
- Team can now use the pipeline
- Documentation ready for sharing

## Next Steps:

### **For Your Team:**
1. **Share the pipeline repo URL**
2. **Point them to [COMPLETE-USAGE-GUIDE.md](../COMPLETE-USAGE-GUIDE.md)**
3. **Help them add the 2 required files** to their projects
4. **They can start deploying immediately!**

### **For You:**
1. **Monitor AWS costs** (should be minimal with free tier)
2. **Update pipeline** as needed (team gets updates automatically)
3. **Add more app types** if needed (Python, .NET, etc.)

## 🚨 Important Security Notes:

- **Never commit AWS credentials** to any repository
- **Use GitHub secrets** for all sensitive data
- **Regularly rotate AWS access keys** (every 90 days)
- **Monitor AWS billing** to avoid unexpected charges
- **Review team access** to the pipeline repository

## 💡 Troubleshooting:

### **If builds fail:**
- Check AWS credentials in GitHub secrets
- Verify EC2 key pair is correct
- Ensure Dockerfile builds locally first

### **If deployment fails:**
- Check AWS Console for error messages
- Verify security groups allow traffic
- Wait 10 minutes for infrastructure to fully initialize

### **If app not accessible:**
- Check Load Balancer status in AWS Console
- Verify health check endpoint exists
- Check application logs on EC2 instances

---

**🎯 Your team now has enterprise-grade CI/CD with just 2 files per project!**