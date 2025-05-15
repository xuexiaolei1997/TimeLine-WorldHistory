# Start from Ubuntu base image
FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3.10-venv \
    nodejs \
    npm \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy frontend package.json and install Node.js dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy the rest of the application
COPY . .

# Build frontend
RUN npm run build

# Expose ports
EXPOSE 3000 8000

# Create startup script
RUN echo '#!/bin/bash\n\
cd /app/backend && python run.py &\n\
cd /app && npm start' > /app/start.sh && \
chmod +x /app/start.sh

# Set environment variables
ENV MONGO_URI=mongodb://localhost:27017/timeline
ENV ENVIRONMENT=production
ENV REACT_APP_API_URL=http://localhost:8000

# Start the application
CMD ["/app/start.sh"]