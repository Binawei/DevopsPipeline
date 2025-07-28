# Manual Rollback Guide

## 🎯 **Manual Rollback Only**

Your pipeline supports **manual rollback** - you control when and what to rollback to.

---

## 🚀 **Setup Manual Rollback**

### **Step 1: Add Rollback Workflow to Your Project**

Create `.github/workflows/rollback.yml` in your project:

```yaml
name: Manual Rollback

on:
  workflow_dispatch:
    inputs:
      rollback_to_tag:
        description: 'Git SHA or image tag to rollback to'
        required: true
        type: string

jobs:
  rollback:
    uses: YOUR_USERNAME/DevOpsPipeline/.github/workflows/rollback.yml@main
    with:
      project_name: "your-app-name"
      rollback_to_tag: ${{ inputs.rollback_to_tag }}
      aws_region: "us-east-1"
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      EC2_SSH_KEY: ${{ secrets.EC2_SSH_KEY }}
```

### **Step 2: Execute Rollback**

1. **Go to GitHub** → Your repo → **Actions tab**
2. **Click "Manual Rollback"** workflow
3. **Click "Run workflow"** button
4. **Enter the git SHA** to rollback to (e.g., `abc123def`)
5. **Click "Run workflow"**
6. **Approve deployment** when prompted
7. **Wait for completion** (3-5 minutes)

---

## 🔍 **Find Rollback Targets**

### **Option 1: GitHub Actions History**
1. **Go to Actions tab** → Previous successful deployments
2. **Copy the git SHA** from successful runs (7-character code)

### **Option 2: AWS ECR Console**
1. **AWS Console** → **ECR** → Your repository
2. **See all available image tags**

### **Option 3: Command Line**
```bash
# List recent commits
git log --oneline -10

# List available ECR images
aws ecr describe-images --repository-name your-app-name --query 'imageDetails[*].imageTags' --output table
```

---

## 📋 **Rollback Process**

### **What Happens During Rollback**
1. **Verifies rollback image exists** in ECR
2. **Gets EC2 instance IPs** from Auto Scaling Group
3. **Stops current containers** on all instances
4. **Pulls and starts** rollback image
5. **Performs health checks** to verify success
6. **Notifies completion**

### **Rollback Time: 3-5 minutes**

---

## 🗄️ **Database Considerations**

### **Safe Rollbacks (No Database Changes)**
- ✅ **Bug fixes**
- ✅ **UI changes**
- ✅ **Configuration updates**
- ✅ **Performance improvements**

### **Risky Rollbacks (Database Schema Changes)**
- ⚠️ **New database columns** added
- ⚠️ **New tables** created
- ⚠️ **Data migrations** performed

### **Database Rollback Strategy**
```sql
-- If you added columns, you may need to remove them
ALTER TABLE users DROP COLUMN new_column;

-- If you added tables, you may need to drop them
DROP TABLE new_table;

-- Always backup before schema changes
pg_dump -h your-rds-endpoint -U admin your_database > backup.sql
```

---

## 🚨 **Emergency Rollback**

### **If GitHub Actions is Down**
```bash
# SSH directly to EC2 instances
ssh -i your-key.pem ec2-user@instance-ip

# Stop current container
docker stop your-app-name

# Pull and run previous version
docker pull your-ecr-repo:previous-git-sha
docker run -d --name your-app-name -p 8080:8080 your-ecr-repo:previous-git-sha
```

### **If Complete System Failure**
1. **Check AWS Console** → EC2 → Auto Scaling Groups
2. **Update Launch Template** to previous working AMI
3. **Terminate instances** to force recreation with previous version

---

## ✅ **Rollback Verification**

### **After Rollback Completes**
1. **Check application URL** (Load Balancer DNS)
2. **Verify key functionality** works
3. **Check application logs** in CloudWatch
4. **Monitor for any errors**

### **Health Check Endpoints**
- **Spring Boot**: `http://your-app/actuator/health`
- **React**: `http://your-app/health`
- **Node.js**: `http://your-app/health`

---

## 📊 **Best Practices**

### **Before Deployment**
- ✅ **Test thoroughly** in staging
- ✅ **Note current version** before deploying
- ✅ **Plan rollback strategy** for risky changes
- ✅ **Backup database** if schema changes

### **During Issues**
- ✅ **Act quickly** but don't panic
- ✅ **Identify root cause** before rollback
- ✅ **Communicate with team**
- ✅ **Document the incident**

### **After Rollback**
- ✅ **Verify application** works correctly
- ✅ **Fix the original issue**
- ✅ **Test fix** in staging
- ✅ **Plan next deployment**

---

## 🎯 **Example Rollback Scenarios**

### **Scenario 1: Bug in New Feature**
```
1. Identify the git SHA before the bug was introduced
2. Run manual rollback workflow with that SHA
3. Verify application works
4. Fix bug in development
5. Deploy fix when ready
```

### **Scenario 2: Performance Issue**
```
1. Check recent deployments in GitHub Actions
2. Find last known good performance version
3. Rollback to that version
4. Investigate performance issue
5. Deploy optimized version
```

### **Scenario 3: Database Migration Issue**
```
1. Rollback application first
2. Check if database needs rollback too
3. Restore database from backup if needed
4. Fix migration script
5. Test in staging before redeploying
```

---

## 🎉 **Summary**

With manual rollback, you have:
- ✅ **Full control** over when to rollback
- ✅ **Simple process** via GitHub Actions
- ✅ **3-5 minute** rollback time
- ✅ **Approval gates** for safety
- ✅ **Emergency procedures** for critical issues

**Manual rollback gives you precise control over your deployments!**