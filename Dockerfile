FROM ollama/ollama

WORKDIR /app

COPY app/requirements.txt /app/requirements.txt



# Install dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip \
                       pkg-config \
                       libhdf5-dev

RUN pip install -r /app/requirements.txt


# Copy application files
COPY app .

COPY ./ollama/ollama /root/.ollama

COPY ./mobilenet_model /app/mobilenet_model

COPY ./assets /app/assets

# Copy entrypoint.sh to /app
COPY entrypoint.sh /app/entrypoint.sh


# Make entrypoint.sh executable
RUN chmod +x /app/entrypoint.sh

# Set environment variables
ENV PORT 8000
ENV HOST 0.0.0.0

EXPOSE 11434

# Use entrypoint.sh as the entry point
ENTRYPOINT ["/app/entrypoint.sh"]