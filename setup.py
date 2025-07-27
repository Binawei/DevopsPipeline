#!/usr/bin/env python3

import os
import sys
import yaml
import shutil
from pathlib import Path

class PipelineSetup:
    def __init__(self, project_path, config_file="pipeline-config.yml"):
        self.project_path = Path(project_path)
        self.config = self.load_config(config_file)
        
    def load_config(self, config_file):
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def setup_project(self, app_type, project_name):
        """Setup DevOps pipeline for a project"""
        print(f"Setting up {app_type} pipeline for {project_name}")
        
        # Create devops directory structure
        devops_dir = self.project_path / "devops"
        devops_dir.mkdir(exist_ok=True)
        
        # Copy templates based on app type
        self.copy_templates(app_type, devops_dir)
        
        # Generate configuration files
        self.generate_configs(app_type, project_name, devops_dir)
        
        print(f"✅ Pipeline setup complete for {project_name}")
        print(f"📁 Files created in: {devops_dir}")
        
    def copy_templates(self, app_type, target_dir):
        """Copy template files to target project"""
        template_dir = Path("templates") / app_type
        
        if template_dir.exists():
            shutil.copytree(template_dir, target_dir, dirs_exist_ok=True)
        
        # Copy common templates
        common_dir = Path("templates/common")
        if common_dir.exists():
            shutil.copytree(common_dir, target_dir, dirs_exist_ok=True)
    
    def generate_configs(self, app_type, project_name, target_dir):
        """Generate project-specific configuration files"""
        
        # Generate Terraform variables
        tf_vars = f"""
project_name = "{project_name}"
app_type = "{app_type}"
aws_region = "{self.config['defaults']['aws_region']}"
instance_type = "{self.config['defaults']['instance_type']}"
min_instances = {self.config['defaults']['min_instances']}
max_instances = {self.config['defaults']['max_instances']}
enable_database = {str(self.config['defaults']['enable_database']).lower()}
database_type = "{self.config['defaults']['database_type']}"
database_instance_class = "{self.config['defaults']['database_instance_class']}"
"""
        
        with open(target_dir / "terraform" / "terraform.tfvars", "w") as f:
            f.write(tf_vars)
        
        # Generate Ansible inventory template
        inventory = f"""
[staging]
# Add your staging server IPs here
# staging-1 ansible_host=10.0.1.10 ansible_user=ec2-user

[production]
# Add your production server IPs here  
# prod-1 ansible_host=10.0.2.10 ansible_user=ec2-user

[all:vars]
project_name={project_name}
app_type={app_type}
"""
        
        with open(target_dir / "ansible" / "inventory.template", "w") as f:
            f.write(inventory)
            
        # Generate GitHub workflow
        self.generate_github_workflow(app_type, project_name)
    
    def generate_github_workflow(self, app_type, project_name):
        """Generate GitHub workflow for the target project"""
        workflow_dir = self.project_path / ".github" / "workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine workflow template
        template_name = "backend-deploy.yml" if app_type in ["java-spring-boot", "node-backend"] else "frontend-deploy.yml"
        
        # Read template
        template_path = Path("templates/github-workflows") / template_name
        with open(template_path, "r") as f:
            workflow_content = f.read()
        
        # Replace placeholders
        workflow_content = workflow_content.replace("{{PROJECT_NAME}}", project_name)
        workflow_content = workflow_content.replace("{{APP_TYPE}}", app_type)
        
        # Write workflow file
        with open(workflow_dir / "deploy.yml", "w") as f:
            f.write(workflow_content)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python setup.py <project_path> <app_type> <project_name>")
        print("App types: java-spring-boot, react-frontend, node-backend")
        sys.exit(1)
    
    project_path = sys.argv[1]
    app_type = sys.argv[2] 
    project_name = sys.argv[3]
    
    setup = PipelineSetup(project_path)
    setup.setup_project(app_type, project_name)