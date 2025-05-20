# JobRad-CodeChallenge
May 2025

## Task
- Implement a simple solution for a chat that enables customers to send messages to customer service.

## Usage
- This application is built using **Docker**

- Run `run_docker_setup.sh` within this directory to build the *ChatApp* Docker image and the *chatapp-network*
- Then run `run_server.sh` to start the Docker container for the ChatApp server
  - this starts the *chatserver* container and makes it available inside the created docker *chatapp-network*
  - additionally, it creates or assigns a docker volume *db-data* for persisting the data
- Run `run_client.sh` to interact with the *chatserver* using the ChatClient app

## Talking points
Imagine a situation where you need to implement a chat software for our customer service to interact with our customers.
- Quick win solution:
  - simple chat UI for customers and customer service
  - backend server for handling the chat functionality and database to store messages for corresponding chats
- State-of-the-art solution:
  - chat accessible to customers via online app or Messenger app endpoint (e.g. Whatsapp, ...)
  - identify recurring user via cookie or token
  - Chatbot functionality
    - trained with most common customer questions
    - provides quick answers on demand for simple/common questions without need of customer service personnel
    - available 24/7
  - ability to provide chat input via audio
    - automatically transcribed for customer service using AI
  - media upload functionality
  - message-status and live-chat functionality
  - implementation: threaded application with possibly multiple servers and load-balancing 
  - or even split frontend, backend, and database into scalable microservices with defined APIs
  - integration / interaction with customer service software/case management