# Database Integration Guide

## 🎯 **RDS Database Support**

Your pipeline now supports **automatic RDS database creation** with zero configuration required!

---

## 🚀 **How to Enable Database**

### **Step 1: Update Your Workflow**

In your project's `.github/workflows/deploy.yml`:

```yaml
name: Build and Deploy with Database

on:
  push:
    branches: [main, master, develop, feature/*]
  workflow_dispatch:

jobs:
  build-and-deploy:
    uses: YOUR_USERNAME/DevOpsPipeline/.github/workflows/build-and-deploy.yml@main
    with:
      project_name: "riderapp"
      app_type: "java-spring-boot"
      aws_region: "us-east-1"
      enable_database: true              # Add this line
      database_type: "postgres"          # Add this line (postgres or mysql)
      database_instance_class: "db.t3.micro"  # Add this line
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      EC2_SSH_KEY: ${{ secrets.EC2_SSH_KEY }}
```

### **Step 2: Update Your Application**

**For Spring Boot** - Update `application.yml`:

```yaml
spring:
  datasource:
    # These environment variables are set automatically by the pipeline
    url: ${SPRING_DATASOURCE_URL:jdbc:h2:mem:testdb}
    username: ${SPRING_DATASOURCE_USERNAME:sa}
    password: ${SPRING_DATASOURCE_PASSWORD:}
  jpa:
    hibernate:
      ddl-auto: update
    database-platform: ${DATABASE_PLATFORM:org.hibernate.dialect.H2Dialect}
```

**For Node.js** - Environment variables available:
```javascript
const dbConfig = {
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  username: process.env.DB_USERNAME,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT || 5432
};
```

### **Step 3: Deploy**

```bash
git add .
git commit -m "Enable RDS database"
git push origin main
```

---

## 🔧 **What Gets Created Automatically**

### **RDS Instance**
- ✅ **PostgreSQL 15.4** or **MySQL 8.0**
- ✅ **Encrypted storage** at rest
- ✅ **Auto-scaling storage** (20GB → 100GB)
- ✅ **Automated backups** (7 days retention)
- ✅ **Maintenance windows** configured

### **Security**
- ✅ **Private database subnets**
- ✅ **Security groups** (only app servers can access)
- ✅ **Credentials** stored in AWS Parameter Store
- ✅ **No public internet access**

### **Environment Variables**
Your application automatically receives:
- `SPRING_DATASOURCE_URL` - Database connection URL
- `SPRING_DATASOURCE_USERNAME` - Database username
- `SPRING_DATASOURCE_PASSWORD` - Database password

---

## ⚙️ **Configuration Options**

### **Database Types**
```yaml
database_type: "postgres"    # PostgreSQL (recommended)
# or
database_type: "mysql"       # MySQL
```

### **Instance Classes**
```yaml
database_instance_class: "db.t3.micro"    # Free tier (1 vCPU, 1GB RAM)
database_instance_class: "db.t3.small"    # Production light (2 vCPU, 2GB RAM)
database_instance_class: "db.t3.medium"   # Production standard (2 vCPU, 4GB RAM)
```

### **Complete Example**
```yaml
# Development setup
with:
  project_name: "riderapp"
  app_type: "java-spring-boot"
  enable_database: true
  database_type: "postgres"
  database_instance_class: "db.t3.micro"

# Production setup
with:
  project_name: "riderapp"
  app_type: "java-spring-boot"
  enable_database: true
  database_type: "postgres"
  database_instance_class: "db.t3.small"
```

---

## 🔒 **Security Features**

### **Automatic Security**
- **Encrypted storage** with AWS KMS
- **Private subnets** for database isolation
- **Security groups** restrict access to app servers only
- **Credentials** stored in AWS Parameter Store (encrypted)
- **No public internet access** to database

### **Access Control**
- Database only accessible from your application servers
- Automatic credential injection into containers
- No hardcoded passwords in code or configuration

---

## 📊 **Monitoring & Maintenance**

### **What You Get**
- **CloudWatch metrics** for database performance
- **Automated backups** every day (7 days retention)
- **Maintenance windows** for automatic updates
- **Storage auto-scaling** when needed

### **AWS Console Access**
1. **Go to RDS** in AWS Console
2. **Find your database** (named `{project_name}-db`)
3. **Monitor performance** in CloudWatch tab
4. **View backup status** in Maintenance & backups tab

---

## 💰 **Cost Breakdown**

### **Monthly Costs (US East)**
- **db.t3.micro** - ~$13/month (Free tier: 750 hours)
- **db.t3.small** - ~$25/month
- **db.t3.medium** - ~$50/month

### **Free Tier Benefits**
- **750 hours** of db.t3.micro per month (covers 1 instance)
- **20GB storage** included
- **20GB backup storage** included

---

## 🎯 **Recommended Configurations**

### **For Development/Testing**
```yaml
enable_database: true
database_type: "postgres"
database_instance_class: "db.t3.micro"  # Uses free tier
```

### **For Production**
```yaml
enable_database: true
database_type: "postgres"
database_instance_class: "db.t3.small"  # Better performance
```

### **For High Traffic**
```yaml
enable_database: true
database_type: "postgres"
database_instance_class: "db.t3.medium"  # High performance
```

---

## 🔄 **Migration from Existing Database**

### **If You Have Existing Data**
1. **Export your current database**
2. **Deploy with database enabled**
3. **Connect to new RDS instance**:
   ```bash
   # Get database endpoint from AWS Console
   psql -h your-rds-endpoint -U admin -d your_database_name
   ```
4. **Import your data**

### **Connection Details**
- **Host**: Available in AWS Console → RDS → Your DB → Connectivity
- **Username**: `admin`
- **Password**: Stored in AWS Parameter Store
- **Database**: Same as your project name (without hyphens)

---

## 🚨 **Troubleshooting**

### **Application Can't Connect**
1. **Check security groups** in AWS Console
2. **Verify database is running** (status: Available)
3. **Check application logs** for connection errors

### **Database Not Created**
1. **Verify `enable_database: true`** in workflow
2. **Check Terraform logs** in GitHub Actions
3. **Ensure AWS permissions** include RDS access

### **Performance Issues**
1. **Monitor CloudWatch metrics**
2. **Consider upgrading instance class**
3. **Check for long-running queries**

---

## 🎉 **Benefits Summary**

- ✅ **Zero configuration** - Just set `enable_database: true`
- ✅ **Production ready** - Backups, encryption, monitoring
- ✅ **Secure by default** - Private subnets, encrypted credentials
- ✅ **Auto-scaling** - Storage grows as needed
- ✅ **Cost effective** - Free tier eligible
- ✅ **Fully managed** - AWS handles maintenance

**Your application now has enterprise-grade database infrastructure with zero DevOps overhead!**