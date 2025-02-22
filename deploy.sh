#!/bin/bash
set -e

echo "Authenticating with GitHub..."
git remote set-url origin https://x-access-token:${GH_DEPLOY_TOKEN}@github.com/${GITHUB_REPOSITORY}.git

echo "Deploying frontend to GitHub Pages..."
# First, save frontend files to temp directory
mkdir -p /tmp/frontend-files
cp -r frontend/* /tmp/frontend-files/

# Create and switch to gh-pages branch
git checkout --orphan gh-pages
git rm -rf .

# Copy saved frontend files back
cp -r /tmp/frontend-files/* .
touch .nojekyll

# Debug info
echo "Current directory contents:"
ls -la

git add .
git commit -m "Deploy to GitHub Pages"
git push -f origin gh-pages

echo "Deploying backend to AWS Elastic Beanstalk..."
cd /app/backend
eb init -p python-3.9 class-share-app --region ap-southeast-2
eb deploy

echo "Deployment complete!"