# Complete Usage Guide - DevOps Pipeline

## 🎯 **What This Pipeline Does**

Automatically builds and deploys your backend applications (Java Spring Boot, Node.js) to AWS ECS Fargate with:
- ✅ **Build on every push** (any branch)
- ✅ **Manual approval for deployment** (main/master only)
- ✅ **Serverless container infrastructure** (ECS Fargate + ALB)
- ✅ **Managed RDS database** (PostgreSQL/MySQL)
- ✅ **Zero server management** (everything automated)

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
    uses: YOUR_USERNAME/DevOpsPipeline/.github/workflows/setup-project.yml@main
    with:
      project_name: "my-app-name"           # Change this
      app_type: "java-spring-boot"          # Change this: java-spring-boot or node-backend
      aws_region: "us-east-1"
      enable_database: true                  # Add this for database support
      database_type: "postgres"             # Add this: postgres or mysql
      database_instance_class: "db.t3.micro" # Add this: db.t3.micro (free tier)
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
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
```

---

## 📊 **Database Support (Optional)**

### **Enable Managed RDS Database**

Add these parameters to enable automatic database creation:

```yaml
with:
  project_name: "my-app"
  app_type: "java-spring-boot"
  enable_database: true              # Enables RDS
  database_type: "postgres"          # postgres or mysql
  database_instance_class: "db.t3.micro"  # Free tier
```

### **What You Get**
- ✅ **PostgreSQL or MySQL** RDS instance
- ✅ **Encrypted storage** and backups
- ✅ **Private database subnets**
- ✅ **Automatic credentials** injection
- ✅ **Free tier eligible** (db.t3.micro)

### **Application Configuration**

**Spring Boot** (`application.yml`):
```yaml
spring:
  datasource:
    url: ${SPRING_DATASOURCE_URL:jdbc:h2:mem:testdb}
    username: ${SPRING_DATASOURCE_USERNAME:sa}
    password: ${SPRING_DATASOURCE_PASSWORD:}
  jpa:
    hibernate:
      ddl-auto: update
```

**Node.js**:
```javascript
const dbConfig = {
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  username: process.env.DB_USERNAME,
  password: process.env.DB_PASSWORD
};
```

**See [DATABASE_GUIDE.md](docs/DATABASE_GUIDE.md) for complete details.**

---

## 📋 **What Happens When You Push**

### **Any Branch (develop, feature/*):**
```
Push Code → Build Docker Image → Push to ECR → ✅ Done
```

### **Main/Master Branch (Manual Approval):**
```
Push Code → Build Docker Image → 🔘 Approval Button → Click → Deploy to ECS Fargate → ✅ Live App
```

### **Main/Master Branch (Auto Deploy):**
```
Push Code → Build Docker Image → Deploy to ECS Fargate → ✅ Live App
```

---

## 🔧 **Customization Options**

### **Change Project Settings:**
```yaml
with:
  project_name: "my-custom-app"      # Your app name
  app_type: "node-backend"           # java-spring-boot or node-backend
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
- Check ECS task logs in AWS Console
- Ensure your app runs on port 8080

### **App Not Accessible:**
- Wait 5-10 minutes for ECS tasks to start
- Check AWS Console for Load Balancer status
- Verify ECS tasks are running and healthy

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
- ✅ **Serverless container infrastructure**
- ✅ **Automatic scaling and load balancing**
- ✅ **Manual deployment control**
- ✅ **Zero server management**

## 🔄 **Manual Rollback**

Add rollback capability to your project:

```yaml
# .github/workflows/rollback.yml
name: Manual Rollback
on:
  workflow_dispatch:
    inputs:
      rollback_to_tag:
        description: 'Git SHA to rollback to'
        required: true

jobs:
  rollback:
    uses: YOUR_USERNAME/DevOpsPipeline/.github/workflows/rollback.yml@main
    with:
      project_name: "your-app"
      rollback_to_tag: ${{ inputs.rollback_to_tag }}
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```