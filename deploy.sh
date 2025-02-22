#!/bin/bash
set -e

echo "Authenticating with GitHub..."
git remote set-url origin https://x-access-token:${GH_DEPLOY_TOKEN}@github.com/${GITHUB_REPOSITORY}.git

echo "Deploying frontend to GitHub Pages..."
# Create and switch to gh-pages branch
git checkout --orphan gh-pages
git rm -rf .

# Ensure the working directory is correct
cd /app

# Copy frontend files
cp -r frontend/* .
touch .nojekyll

# Commit and push to gh-pages
git add .
git commit -m "Deploy to GitHub Pages"
git push -f origin gh-pages

echo "Deploying backend to AWS Elastic Beanstalk..."
cd backend
eb init -p python-3.9 class-share-app --region ap-southeast-2
eb deploy

echo "Deployment complete!"