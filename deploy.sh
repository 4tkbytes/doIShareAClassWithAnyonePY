#!/bin/bash
set -e

echo "Authenticating with GitHub..."
# Modified git authentication
git remote set-url origin "https://${GH_DEPLOY_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"

echo "Deploying frontend to GitHub Pages..."
mkdir -p /tmp/frontend-files
cp -r frontend/* /tmp/frontend-files/

git checkout --orphan gh-pages
git rm -rf .

cp -r /tmp/frontend-files/* .
touch .nojekyll

# Debug info
echo "Current directory contents:"
ls -la

git config --global user.email "actions@github.com"
git config --global user.name "GitHub Actions"

git add .
git commit -m "Deploy to GitHub Pages"
git push -f origin gh-pages

echo "Deploying backend to AWS Elastic Beanstalk..."
cd /app/backend
eb init -p python-3.9 class-share-app --region ap-southeast-2
eb deploy

echo "Deployment complete!"