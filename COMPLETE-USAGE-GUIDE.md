# Complete Usage Guide - DevOps Pipeline

## 🎯 **What This Pipeline Does**

Automatically builds and deploys your applications (Java, React, Node.js) to AWS EC2 with:
- ✅ **Build on every push** (any branch)
- ✅ **Manual approval for deployment** (main/master only)
- ✅ **Auto-scaling infrastructure** (Load Balancer + EC2)
- ✅ **Zero manual setup** (everything automated)

---

## 🚀 **How to Use in Your Projects**

### **Option 1: Manual Approval Deployment (Recommended)**

#### **Step 1: Add Dockerfile to Your Project**

**For Java Spring Boot:**
```dockerfile
FROM openjdk:17-jre-slim
WORKDIR /app
COPY target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

**For React Frontend:**
```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**For Node.js Backend:**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 8080
CMD ["npm", "start"]
```

#### **Step 2: Add GitHub Workflow**

Create `.github/workflows/deploy.yml` in your project:

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
      project_name: "my-app-name"           # Change this
      app_type: "java-spring-boot"          # Change this: java-spring-boot, react-frontend, node-backend
      aws_region: "us-east-1"
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      EC2_SSH_KEY: ${{ secrets.EC2_SSH_KEY }}
```

#### **Step 3: Setup GitHub Environment Protection**

1. **Go to your project repo** → **Settings** → **Environments**
2. **Click "New environment"**
3. **Name**: `production-approval`
4. **Check "Required reviewers"** → Add yourself or team members
5. **Click "Save protection rules"**

#### **Step 4: Add GitHub Secrets**

1. **Go to your project repo** → **Settings** → **Secrets and variables** → **Actions**
2. **Click "New repository secret"** and add:
   - **Name**: `AWS_ACCESS_KEY_ID` **Value**: Your AWS access key
   - **Name**: `AWS_SECRET_ACCESS_KEY` **Value**: Your AWS secret key
   - **Name**: `EC2_SSH_KEY` **Value**: Your EC2 private key content (entire .pem file)

#### **Step 5: Push and Deploy**

```bash
# Push to any branch - builds automatically
git add .
git commit -m "Add deployment pipeline"
git push origin feature/my-feature  # Builds only

# Push to main - builds + shows approval button
git push origin main  # Builds + waits for approval
```

#### **Step 6: Approve Deployment**

1. **Go to GitHub** → Your repo → **Actions tab**
2. **Click on the workflow run** (you'll see a yellow dot)
3. **Click "Review deployments"** button
4. **Select "production-approval"** environment
5. **Click "Approve and deploy"**
6. **Watch deployment happen** automatically
7. **Get your app URL** from the workflow logs

---

### **Option 2: Automatic Deployment (No Approval)**

If you want automatic deployment without approval:

```yaml
name: Auto Deploy

on:
  push:
    branches: [main, master]

jobs:
  deploy:
    uses: YOUR_USERNAME/DevOpsPipeline/.github/workflows/setup-project.yml@main
    with:
      project_name: "my-app-name"
      app_type: "java-spring-boot"
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      EC2_SSH_KEY: ${{ secrets.EC2_SSH_KEY }}
```

---

## 📋 **What Happens When You Push**

### **Any Branch (develop, feature/*):**
```
Push Code → Build Docker Image → Push to ECR → ✅ Done
```

### **Main/Master Branch (Manual Approval):**
```
Push Code → Build Docker Image → 🔘 Approval Button → Click → Deploy to EC2 → ✅ Live App
```

### **Main/Master Branch (Auto Deploy):**
```
Push Code → Build Docker Image → Deploy to EC2 → ✅ Live App
```

---

## 🔧 **Customization Options**

### **Change Project Settings:**
```yaml
with:
  project_name: "my-custom-app"      # Your app name
  app_type: "react-frontend"         # java-spring-boot, react-frontend, node-backend
  aws_region: "eu-west-1"           # Any AWS region
```

### **Change Trigger Branches:**
```yaml
on:
  push:
    branches: [main, develop]        # Only these branches trigger builds
```

### **Add Manual Trigger:**
```yaml
on:
  push:
    branches: [main, master]
  workflow_dispatch:                 # Adds "Run workflow" button
```

---

## 🎯 **Different Use Cases**

### **For Development Teams:**
- Use **Manual Approval** option
- Build on feature branches for testing
- Deploy to production only after approval

### **For Personal Projects:**
- Use **Automatic Deployment** option
- Deploy immediately on main branch push

### **For Enterprise:**
- Use **Manual Approval** with multiple reviewers
- Add compliance and security checks

---

## 🔍 **Monitoring Your Deployment**

### **Check Build Status:**
1. **GitHub** → Your repo → **Actions tab**
2. **Green checkmark** = Build successful
3. **Red X** = Build failed (check logs)

### **Check Deployment Status:**
1. **Yellow dot** = Waiting for approval
2. **Green checkmark** = Deployed successfully
3. **Red X** = Deployment failed

### **Get Your App URL:**
1. **Click on successful deployment**
2. **Scroll to bottom** of logs
3. **Look for Load Balancer URL**
4. **Visit URL** to see your live app

---

## 🚨 **Troubleshooting**

### **Build Fails:**
- Check your Dockerfile syntax
- Ensure your app builds locally first
- Check GitHub Actions logs for errors

### **Deployment Fails:**
- Verify AWS credentials in GitHub secrets
- Check if EC2 SSH key is correct
- Ensure your app has health check endpoint

### **No Approval Button:**
- Make sure you're on main/master branch
- Check environment protection is set up
- Verify environment name is `production-approval`

### **App Not Accessible:**
- Wait 5-10 minutes for infrastructure setup
- Check AWS Console for Load Balancer status
- Verify security groups allow traffic

---

## 💡 **Best Practices**

### **Branch Strategy:**
- **feature/** branches → Build only (fast feedback)
- **develop** branch → Build only (integration testing)
- **main/master** → Build + Deploy (production)

### **Project Naming:**
- Use lowercase with hyphens: `my-app-backend`
- Keep names short and descriptive
- Avoid special characters

### **Security:**
- Never commit AWS credentials to code
- Use GitHub secrets for sensitive data
- Regularly rotate AWS access keys

### **Testing:**
- Test builds on feature branches first
- Use staging environment for testing
- Always test locally before pushing

---

## 🎉 **You're Ready!**

With this setup, you get:
- ✅ **Professional CI/CD pipeline**
- ✅ **AWS production infrastructure**
- ✅ **Automatic scaling and load balancing**
- ✅ **Manual deployment control**
- ✅ **Zero maintenance overhead**

Just add 2 files to any project and you're ready to deploy to AWS!