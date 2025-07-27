# Manual Approval Deployment

## 🎯 **How It Works**

1. **Any push** → Builds Docker image automatically
2. **Only on main/master** → Shows approval button
3. **Click button** → Deploys to production
4. **Other branches** → Build only, no deployment

## 🚀 **Setup for Your Project**

### **Step 1: Add Dockerfile**
```dockerfile
# For Java Spring Boot
FROM openjdk:17-jre-slim
WORKDIR /app
COPY target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

### **Step 2: Add Workflow File**
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
      project_name: "my-app"
      app_type: "java-spring-boot"  # or "react-frontend"
      aws_region: "us-east-1"
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      EC2_SSH_KEY: ${{ secrets.EC2_SSH_KEY }}
```

### **Step 3: Setup GitHub Environment**
1. Go to your repo → **Settings** → **Environments**
2. Create environment: `production-approval`
3. Add **Required reviewers** (yourself or team members)
4. **Save protection rules**

### **Step 4: Add GitHub Secrets**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY` 
- `EC2_SSH_KEY`

## 📋 **What Happens When You Push**

### **Any Branch (develop, feature/*):**
```
Push Code → Build Image → ✅ Done
```

### **Main/Master Branch:**
```
Push Code → Build Image → 🔘 Approval Button → Click → Deploy → ✅ Live
```

## 🔘 **How to Approve Deployment**

1. **Push to main/master**
2. **Go to Actions tab** in your repo
3. **See yellow dot** next to workflow run
4. **Click "Review deployments"** button
5. **Select environment** and click **"Approve and deploy"**
6. **Deployment starts** automatically

## ✅ **Benefits**

- ✅ **Build on every push** (fast feedback)
- ✅ **Deploy only on approval** (controlled releases)
- ✅ **Main/master only** (production safety)
- ✅ **Manual control** (no accidental deployments)
- ✅ **Team approvals** (multiple reviewers possible)

## 🎯 **Perfect For**

- Production deployments that need approval
- Teams that want manual control over releases
- Compliance requirements for deployment approvals
- Preventing accidental production deployments