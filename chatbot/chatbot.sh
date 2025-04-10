#!/bin/bash

# Export path to folder containing the Python script. Export the root directory of the chatbot using PWD
export ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Define a function to generate a response using a Python script
generate_response() {
    python3 "$1" "$2"
}

# add welcome message
echo "Chatbot: Hello! How can I assist you today?. You can type 'exit' to leave the chat."
echo " "
# Main loop for the chatbot
while true; do
    # Read user input
    read -p "User: " input
    # Check for exit command
    if [ "$input" == "exit" ]; then
        echo "Chatbot: Goodbye!"
        break
    fi

    # Generate response using a Python script
    response=$(generate_response "$ROOT_DIR/scheduler_response.py" "$input")

    # Print the response in yellow
    echo "Chatbot: $response" | GREP_COLOR='01;33' grep --color=always '.'
    echo " "


done
