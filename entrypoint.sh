# !/bin/bash

# Install ollama
echo "Installing ollama..."
wget https://ollama.com/download/ollama-linux.tar.gz -O ollama-linux.tar.gz
tar -xzvf ollama-linux.tar.gz
chmod +x ollama
mv ollama /usr/local/bin/

# Check if the llama3.1 model is already pulled
if ! /usr/local/bin/ollama list | grep -q 'llama3.1'; then
  echo "Pulling the llama3.1 model..."
  /usr/local/bin/ollama pull llama3.1
fi

# Start the Streamlit server
echo "Starting the Streamlit server"
streamlit run app.py --server.port $PORT --server.address 0.0.0.0

# #!/bin/sh

# # Function to check if the model is already available
# model_is_pulled() {
#     # Implement the logic to check if the model is available
#     # This depends on how `ollama` handles model storage and availability
#     # For example, you might check for the existence of a model file or directory
#     # Here we assume a placeholder command that checks if the model is pulled
#     # Replace `ollama list` with the actual command to check for the model
#     ollama list | grep -q "llama3"
# }

# # Start the Ollama server in the background
# ollama serve &

# # Get the PID of the Ollama server process
# # SERVER_PID=$!

# # Wait for a few seconds to ensure the server starts properly
# echo "Waiting for the server to start..."


# # Check if the model is already pulled; if not, pull it
# # if ! model_is_pulled; then
# echo "Model not found. Pulling the latest Llama3 model..."
# ollama pull llama3.1
# # else
# #     echo "Model already pulled. Skipping pull."
# # fi

# # Perform additional tasks here
# # Example: Echo a message or run a custom script
# echo "Performing additional tasks..."

# # Optionally add a timeout if needed
# # timeout 300 bash -c "while kill -0 $SERVER_PID 2>/dev/null; do sleep 1; done" &
# # WAIT_PID=$!

# # Wait for the Ollama server process to finish
# # wait $SERVER_PID

# # If needed, run any final commands or clean-up tasks
# echo "Ollama server has stopped. Performing final tasks..."


# # Start the streamlit server, blocking exit
# echo "Starting the Streamlit server"

# # streamlit run app/main.py --server.port=8501 --server.address=0.0.0.0

# streamlit run --server.port ${PORT} --server.address ${HOST} /app/main.py
