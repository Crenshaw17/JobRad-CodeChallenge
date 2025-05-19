# JobRad-CodeChallenge
May 2025

# Usage
- This application is built using **Docker**

- Run `run_docker_setup.sh` within this directory to build the *ChatApp* Docker image and the *chatapp-network*
- Then run `run_server.sh` to start the Docker container for the ChatApp server
  - this starts the *chatserver* container and makes it available inside the created docker *chatapp-network*
  - additionally, it creates or assigns a docker volume *db-data* for persisting the data
- Run `run_client.sh` to interact with the *chatserver* using the ChatClient app