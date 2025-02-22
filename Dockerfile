FROM python:3.9-slim

# Install required tools
RUN apt-get update && \
    apt-get install -y curl git awscli

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy application files
COPY . .

# Install AWS EB CLI
RUN pip install awsebcli

# Copy deployment scripts
COPY deploy.sh .
RUN chmod +x deploy.sh

# Configure git for GitHub Pages deployment
RUN git config --global user.email "github-actions@github.com" && \
    git config --global user.name "GitHub Actions"

CMD ["./deploy.sh"]