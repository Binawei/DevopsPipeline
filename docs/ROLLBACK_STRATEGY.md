# Rollback Strategy & Recovery Plan

## 🎯 **Rollback Capabilities**

Your pipeline includes **multiple rollback strategies** for different failure scenarios:

1. **Automatic Rollback** - On deployment failure
2. **Manual Rollback** - User-triggered via GitHub Actions
3. **Database Rollback** - For database schema changes
4. **Infrastructure Rollback** - Terraform state recovery

---

## 🔄 **Automatic Rollback**

### **When It Triggers**
- ✅ **Health check failures** after deployment
- ✅ **Container startup failures**
- ✅ **Application crashes** during deployment
- ✅ **Load balancer health check failures**

### **What Happens Automatically**
1. **Detects failure** during deployment
2. **Identifies previous working image**
3. **Stops failed containers**
4. **Starts previous working version**
5. **Verifies health checks pass**
6. **Notifies team** of rollback completion

### **No Action Required**
The pipeline handles failures automatically - your application stays online with the previous working version.

---

## 🖱️ **Manual Rollback**

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

### **Step 2: Execute Manual Rollback**

1. **Go to GitHub** → Your repo → **Actions tab**
2. **Click "Manual Rollback"** workflow
3. **Click "Run workflow"** button
4. **Enter the image tag** to rollback to (e.g., `abc123def` or `v1.2.0`)
5. **Click "Run workflow"**
6. **Approve deployment** when prompted
7. **Wait for completion**

### **Step 3: Find Available Rollback Targets**

**Option A: GitHub Actions History**
- Go to **Actions tab** → Previous successful deployments
- Copy the **git SHA** from successful runs

**Option B: AWS ECR Console**
- Go to **AWS Console** → **ECR** → Your repository
- See all available **image tags**

**Option C: Command Line**
```bash
# List available images
aws ecr describe-images --repository-name your-app-name --query 'imageDetails[*].imageTags' --output table
```

---

## 🗄️ **Database Rollback**

### **For Schema Changes**
Database rollbacks are **more complex** and require planning:

#### **Safe Database Changes (Auto-Rollback Safe)**
- ✅ **Adding new columns** (with defaults)
- ✅ **Adding new tables**
- ✅ **Adding indexes**
- ✅ **Data inserts/updates**

#### **Risky Database Changes (Manual Rollback Required)**
- ⚠️ **Dropping columns**
- ⚠️ **Dropping tables**
- ⚠️ **Changing column types**
- ⚠️ **Removing indexes**

### **Database Rollback Process**

#### **Step 1: Backup Before Changes**
```sql
-- Automatic backup is created before each deployment
-- Manual backup command:
pg_dump -h your-rds-endpoint -U admin your_database > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### **Step 2: Application Rollback First**
```bash
# Always rollback application first
# Then handle database if needed
```

#### **Step 3: Database Schema Rollback (if needed)**
```sql
-- Example: Rollback column addition
ALTER TABLE users DROP COLUMN new_column;

-- Example: Rollback table creation
DROP TABLE new_table;
```

### **Database Rollback Best Practices**
1. **Test migrations** in staging first
2. **Use backward-compatible** changes when possible
3. **Keep old columns** for a few releases before dropping
4. **Plan rollback scripts** before deployment

---

## 🏗️ **Infrastructure Rollback**

### **Terraform State Recovery**

#### **If Infrastructure Changes Fail**
```bash
# 1. Check Terraform state
cd devops/terraform
terraform show

# 2. Rollback to previous state
terraform apply -target=specific_resource

# 3. Or destroy and recreate
terraform destroy -target=problematic_resource
terraform apply
```

#### **If Complete Infrastructure Failure**
```bash
# 1. Backup current state
cp terraform.tfstate terraform.tfstate.backup

# 2. Import existing resources
terraform import aws_instance.app i-1234567890abcdef0

# 3. Re-apply configuration
terraform plan
terraform apply
```

---

## 📊 **Rollback Monitoring**

### **Health Check Verification**
After any rollback, the pipeline verifies:
- ✅ **Application responds** to health checks
- ✅ **Load balancer** shows healthy targets
- ✅ **Database connections** work (if enabled)
- ✅ **All instances** are running correctly

### **Rollback Notifications**
You'll receive notifications via:
- **GitHub Actions** status updates
- **AWS CloudWatch** alarms (if configured)
- **Application logs** in CloudWatch

---

## 🚨 **Emergency Procedures**

### **Complete System Failure**

#### **Step 1: Immediate Response**
```bash
# 1. Check AWS Console for infrastructure status
# 2. Check GitHub Actions for pipeline status
# 3. Check application logs in CloudWatch
```

#### **Step 2: Quick Recovery Options**

**Option A: Rollback via GitHub Actions**
- Use manual rollback workflow
- Select last known good version

**Option B: Direct AWS Console**
```bash
# 1. Go to EC2 → Auto Scaling Groups
# 2. Update Launch Template to previous AMI
# 3. Terminate instances to force recreation
```

**Option C: Emergency Manual Deployment**
```bash
# 1. SSH into EC2 instances
ssh -i your-key.pem ec2-user@instance-ip

# 2. Manually pull and run previous image
docker pull your-ecr-repo:previous-tag
docker stop your-app
docker run -d --name your-app -p 8080:8080 your-ecr-repo:previous-tag
```

### **Database Emergency Recovery**
```bash
# 1. Check RDS status in AWS Console
# 2. Restore from automated backup if needed
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier your-app-db-restored \
  --db-snapshot-identifier your-app-db-snapshot-id

# 3. Update application to use restored database
```

---

## 📋 **Rollback Checklist**

### **Before Rollback**
- [ ] **Identify the issue** and root cause
- [ ] **Determine rollback target** (which version to rollback to)
- [ ] **Check if database changes** are involved
- [ ] **Notify team members** about the rollback
- [ ] **Document the incident** for post-mortem

### **During Rollback**
- [ ] **Execute rollback** via GitHub Actions
- [ ] **Monitor health checks** during rollback
- [ ] **Verify application functionality**
- [ ] **Check database connectivity** (if applicable)
- [ ] **Confirm load balancer** shows healthy targets

### **After Rollback**
- [ ] **Verify application** is working correctly
- [ ] **Check all critical features**
- [ ] **Monitor for any issues**
- [ ] **Plan fix** for the original problem
- [ ] **Update team** on status

---

## 🎯 **Rollback Time Estimates**

### **Automatic Rollback**
- **Detection**: 30 seconds - 2 minutes
- **Execution**: 2-5 minutes
- **Total**: 3-7 minutes

### **Manual Rollback**
- **Initiation**: 1-2 minutes
- **Approval**: 1-5 minutes (depending on team)
- **Execution**: 3-5 minutes
- **Total**: 5-12 minutes

### **Database Rollback**
- **Simple changes**: 5-10 minutes
- **Complex changes**: 15-30 minutes
- **Full restore**: 30-60 minutes

---

## 💡 **Best Practices**

### **Prevention**
- ✅ **Test thoroughly** in staging
- ✅ **Use feature flags** for risky changes
- ✅ **Deploy during low-traffic** periods
- ✅ **Monitor closely** after deployments
- ✅ **Keep rollback plans** updated

### **Preparation**
- ✅ **Document rollback procedures**
- ✅ **Test rollback process** regularly
- ✅ **Train team members** on procedures
- ✅ **Keep emergency contacts** handy
- ✅ **Maintain backup strategies**

### **Execution**
- ✅ **Act quickly** but don't panic
- ✅ **Communicate clearly** with team
- ✅ **Document everything** during incident
- ✅ **Verify thoroughly** after rollback
- ✅ **Learn from incidents** for improvement

---

## 🎉 **Recovery Success**

With this rollback strategy, you have:
- ✅ **Automatic failure recovery** (3-7 minutes)
- ✅ **Manual rollback capability** (5-12 minutes)
- ✅ **Database rollback procedures**
- ✅ **Infrastructure recovery plans**
- ✅ **Emergency procedures** for critical failures

**Your applications are protected with enterprise-grade rollback capabilities!**