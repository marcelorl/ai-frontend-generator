# AI Frontend Generator

## Overview
AI Frontend Generator is a powerful tool designed to automate the creation of frontend applications. Leveraging the capabilities of Open API, Streamlit, Python, Docker, and Nginx, this generator streamlines the development process, from gathering requirements to generating and validating the code. The generated static files are stored in the /results directory.

## Features
 - Automated Requirement Gathering: Utilizes AI agents that communicate with each other to refine and extract comprehensive requirements from a given prompt.
 - Code Generation: Automatically generates frontend code based on the refined requirements.
 - Self-Validation: The AI checks the generated code and iteratively refines it until it meets the requirements and functions correctly.
 - Docker and Nginx Integration: The generated applications are containerized using Docker and served with Nginx for efficient deployment.

## Technologies Used
 - Open API: For natural language understanding and processing.
 - Streamlit: To provide an interactive interface for the generator.
 - Python: The core programming language used for the generator's logic.
 - Docker: To containerize the generated applications.
 - Nginx: To serve the generated applications efficiently.

## How It Works
 - Prompt Input: The user provides an initial prompt describing the desired frontend application.
 - Requirement Refinement: AI agents regenerate and refine the prompt to extract detailed requirements.
 - Code Generation: Based on the refined requirements, the AI generates the necessary frontend code.
 - Self-Validation: The AI tests the generated code, making iterative improvements until it functions correctly.
 - Deployment: The final application is containerized using Docker, and static files are placed in the /results directory. Nginx is used to serve the applications within an iframe.

## Installation

To set up and run the AI Frontend Generator, follow these steps:

```bash
cp .env.example .env
```

 - Create an OpenAPI account and API Key
 - Paste the key in the .env file.

 ```bash
docker compose up --build
```

## Examples
![App 1](images/app1.png)
![App 2](images/app2.png)

## License
This project is licensed under the MIT License.