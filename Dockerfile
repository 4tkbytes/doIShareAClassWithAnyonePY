FROM python:3.9-slim

# Install required tools
RUN apt-get update && \
    apt-get install -y curl git awscli

WORKDIR /workspace

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Install AWS EB CLI
RUN pip install awsebcli

# Make deploy script executable
RUN chmod +x deploy.sh

# Configure git
RUN git config --global user.email "actions@github.com" && \
    git config --global user.name "GitHub Actions"

CMD ["./deploy.sh"]