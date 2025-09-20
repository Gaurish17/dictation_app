#!/bin/bash
# Git setup and push script for dictation_app

echo "🚀 Setting up Git repository and pushing to GitHub..."

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
fi

# Add all files
echo "📋 Adding files to Git..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "Initial commit: Complete dictation and typing practice application with deployment setup"

# Add remote origin
echo "🔗 Adding GitHub remote..."
git remote add origin https://github.com/Gaurish17/dictation_app.git

# Set main branch
echo "🌿 Setting main branch..."
git branch -M main

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push -u origin main

echo "✅ Successfully pushed to GitHub!"
echo "🔗 Your repository: https://github.com/Gaurish17/dictation_app"
echo ""
echo "🚀 Next steps for deployment:"
echo "1. Railway: python deploy.py railway"
echo "2. Heroku: python deploy.py heroku"
echo "3. DigitalOcean: python deploy.py digitalocean"
echo "4. Docker: python deploy.py docker"
