#!/bin/bash
set -e

echo "Authenticating with GitHub..."
git remote set-url origin "https://${GH_DEPLOY_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"

# Store current directory and backup backend
CURRENT_DIR=$(pwd)
TEMP_DIR=$(mktemp -d)
cp -r backend/* "$TEMP_DIR/"

echo "Deploying frontend to GitHub Pages..."
mkdir -p /tmp/frontend-files
cp -r frontend/* /tmp/frontend-files/

git checkout --orphan gh-pages
git rm -rf .

cp -r /tmp/frontend-files/* .
touch .nojekyll

git add .
git commit -m "Deploy to GitHub Pages"
git push -f origin gh-pages

echo "Deploying backend to AWS Elastic Beanstalk..."
git checkout main
# Restore backend files
rm -rf backend
mkdir -p backend
cp -r "$TEMP_DIR"/* backend/

cd backend || exit 1
eb init -p python-3.9 class-share-app --region ap-southeast-2
eb deploy

echo "Deployment complete!"