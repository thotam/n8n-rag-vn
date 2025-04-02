FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a startup script that uses config values
RUN echo '#!/bin/bash\npython -c "from app.config import HOST, PORT; import uvicorn; uvicorn.run(\"app.main:app\", host=HOST, port=PORT)"' > start.sh && \
    chmod +x start.sh

# Command to run the application using config values
CMD ["./start.sh"]

# Add a label for the image
LABEL maintainer="thanhtamtqno1@gmail.com"

# Push the image to Docker Hub
# Note: Replace 'your-username' and 'your-repository' with your Docker Hub username and repository name
# Example usage:
# docker build -t thotam/n8n_rag_vn:latest .
# docker push thotam/n8n_rag_vn:latest