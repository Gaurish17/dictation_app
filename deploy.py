#!/usr/bin/env python3
"""
Deployment script for Dictation & Typing Practice App
Supports multiple hosting platforms and deployment scenarios
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path

class DeploymentManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.app_name = "dictation-typing-app"
        
    def check_requirements(self):
        """Check if all required files exist"""
        required_files = [
            'app.py', 'config.py', 'requirements.txt', 
            'Procfile', '.env.example', 'Dockerfile'
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.project_root / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Missing required files: {', '.join(missing_files)}")
            return False
        
        print("✅ All required files present")
        return True
    
    def setup_environment(self):
        """Setup environment variables"""
        env_file = self.project_root / '.env'
        env_example = self.project_root / '.env.example'
        
        if not env_file.exists() and env_example.exists():
            print("📋 Creating .env file from .env.example")
            shutil.copy(env_example, env_file)
            print("⚠️  Please update .env file with your actual values before deployment")
            return False
        
        return True
    
    def deploy_to_railway(self):
        """Deploy to Railway.app"""
        print("\n🚂 Deploying to Railway...")
        
        # Check if Railway CLI is installed
        try:
            subprocess.run(['railway', '--version'], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Railway CLI not found. Install it first:")
            print("npm install -g @railway/cli")
            return False
        
        commands = [
            ['railway', 'login'],
            ['railway', 'init'],
            ['railway', 'up']
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to run: {' '.join(cmd)}")
                print(f"Error: {e}")
                return False
        
        print("✅ Successfully deployed to Railway!")
        return True
    
    def deploy_to_heroku(self):
        """Deploy to Heroku"""
        print("\n🟣 Deploying to Heroku...")
        
        # Check if Heroku CLI is installed
        try:
            subprocess.run(['heroku', '--version'], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Heroku CLI not found. Install it first:")
            print("https://devcenter.heroku.com/articles/heroku-cli")
            return False
        
        commands = [
            ['heroku', 'create', self.app_name],
            ['heroku', 'addons:create', 'heroku-postgresql:hobby-dev'],
            ['git', 'add', '.'],
            ['git', 'commit', '-m', 'Deploy to Heroku'],
            ['git', 'push', 'heroku', 'main']
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to run: {' '.join(cmd)}")
                print(f"Error: {e}")
                return False
        
        print("✅ Successfully deployed to Heroku!")
        return True
    
    def deploy_to_digitalocean(self):
        """Deploy to DigitalOcean App Platform"""
        print("\n🌊 Deploying to DigitalOcean...")
        
        # Create app spec
        app_spec = {
            "name": self.app_name,
            "services": [
                {
                    "name": "web",
                    "source_dir": "/",
                    "github": {
                        "repo": "your-github-username/your-repo-name",
                        "branch": "main"
                    },
                    "run_command": "gunicorn app:app",
                    "environment_slug": "python",
                    "instance_count": 1,
                    "instance_size_slug": "basic-xxs",
                    "routes": [
                        {
                            "path": "/"
                        }
                    ],
                    "envs": [
                        {
                            "key": "FLASK_ENV",
                            "value": "production"
                        }
                    ]
                }
            ],
            "databases": [
                {
                    "engine": "PG",
                    "name": "db",
                    "num_nodes": 1,
                    "size": "basic-xs",
                    "version": "12"
                }
            ]
        }
        
        # Save app spec
        with open(self.project_root / 'app-spec.yaml', 'w') as f:
            import yaml
            yaml.dump(app_spec, f)
        
        print("📄 Created app-spec.yaml for DigitalOcean App Platform")
        print("🔗 Please visit https://cloud.digitalocean.com/apps and create an app using this spec")
        return True
    
    def setup_docker_deployment(self):
        """Setup Docker deployment"""
        print("\n🐳 Setting up Docker deployment...")
        
        # Create docker-compose.yml
        docker_compose = {
            'version': '3.8',
            'services': {
                'web': {
                    'build': '.',
                    'ports': ['5000:5000'],
                    'environment': [
                        'FLASK_ENV=production',
                        'DATABASE_URL=postgresql://postgres:password@db:5432/dictation_app'
                    ],
                    'depends_on': ['db'],
                    'volumes': ['./uploads:/app/uploads', './typing_passages:/app/typing_passages']
                },
                'db': {
                    'image': 'postgres:13',
                    'environment': [
                        'POSTGRES_DB=dictation_app',
                        'POSTGRES_USER=postgres',
                        'POSTGRES_PASSWORD=password'
                    ],
                    'volumes': ['postgres_data:/var/lib/postgresql/data'],
                    'ports': ['5432:5432']
                }
            },
            'volumes': {
                'postgres_data': {}
            }
        }
        
        with open(self.project_root / 'docker-compose.yml', 'w') as f:
            import yaml
            yaml.dump(docker_compose, f)
        
        print("✅ Created docker-compose.yml")
        print("Run: docker-compose up -d")
        return True
    
    def create_nginx_config(self):
        """Create Nginx configuration for VPS deployment"""
        nginx_config = f"""
server {{
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    location / {{
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    location /uploads/ {{
        alias /path/to/your/app/uploads/;
    }}
    
    location /typing_passages/ {{
        alias /path/to/your/app/typing_passages/;
    }}
    
    client_max_body_size 50M;
}}
"""
        
        with open(self.project_root / 'nginx.conf', 'w') as f:
            f.write(nginx_config)
        
        print("✅ Created nginx.conf")
        return True
    
    def create_systemd_service(self):
        """Create systemd service file for VPS deployment"""
        service_config = f"""
[Unit]
Description=Dictation Typing App
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/your/app
Environment=PATH=/path/to/your/app/venv/bin
ExecStart=/path/to/your/app/venv/bin/gunicorn --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
"""
        
        with open(self.project_root / 'dictation-app.service', 'w') as f:
            f.write(service_config)
        
        print("✅ Created dictation-app.service")
        return True
    
    def generate_ssl_setup_script(self):
        """Generate SSL setup script using Let's Encrypt"""
        ssl_script = """#!/bin/bash
# SSL Setup Script using Let's Encrypt

# Install certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Setup auto-renewal
sudo crontab -l | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | sudo crontab -

echo "SSL certificate installed and auto-renewal configured!"
"""
        
        with open(self.project_root / 'setup-ssl.sh', 'w') as f:
            f.write(ssl_script)
        
        os.chmod(self.project_root / 'setup-ssl.sh', 0o755)
        print("✅ Created setup-ssl.sh")
        return True
    
    def run_deployment(self, platform):
        """Main deployment function"""
        print(f"🚀 Starting deployment for {platform}")
        
        if not self.check_requirements():
            return False
        
        if not self.setup_environment():
            print("⚠️  Please setup .env file first")
            return False
        
        if platform.lower() == 'railway':
            return self.deploy_to_railway()
        elif platform.lower() == 'heroku':
            return self.deploy_to_heroku()
        elif platform.lower() == 'digitalocean':
            return self.deploy_to_digitalocean()
        elif platform.lower() == 'docker':
            return self.setup_docker_deployment()
        elif platform.lower() == 'vps':
            self.create_nginx_config()
            self.create_systemd_service()
            self.generate_ssl_setup_script()
            print("✅ VPS deployment files created!")
            print("📋 Next steps:")
            print("1. Upload files to your VPS")
            print("2. Setup virtual environment and install dependencies")
            print("3. Configure nginx with the provided config")
            print("4. Setup systemd service")
            print("5. Run setup-ssl.sh for SSL certificate")
            return True
        else:
            print(f"❌ Unknown platform: {platform}")
            print("Supported platforms: railway, heroku, digitalocean, docker, vps")
            return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python deploy.py <platform>")
        print("Platforms: railway, heroku, digitalocean, docker, vps")
        sys.exit(1)
    
    platform = sys.argv[1]
    deployer = DeploymentManager()
    
    success = deployer.run_deployment(platform)
    if success:
        print(f"\n🎉 Deployment setup for {platform} completed successfully!")
    else:
        print(f"\n❌ Deployment setup for {platform} failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
