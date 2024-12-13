# FastAPI To-Do Application with JWT Authentication  

## Overview  
This project is a **FastAPI-based To-Do App** designed to manage tasks efficiently while ensuring user data security through **JWT (JSON Web Tokens) authentication**. The application follows best practices in **DevOps** for development, deployment, and maintenance.  

## Features  
- **User Authentication**:  
  - Secure registration and login using JWT.  
  - Protected endpoints accessible only to authenticated users.  

- **Task Management**:  
  - Create, update, delete, and retrieve tasks.  
  - Each task is tied to a specific user.  

- **DevOps Practices**:  
  - Automated testing and linting for high code quality.  
  - Dockerized application for easy deployment.  
  - CI/CD pipeline for streamlined integration and delivery.  

## Technologies Used  
- **Backend Framework**: FastAPI  
- **Authentication**: JSON Web Tokens (JWT)  
- **Database**: SQLite (development) / PostgreSQL (production)  
- **Containerization**: Docker  
- **CI/CD**: GitLab CI/CD  
- **Deployment**: AWS EC2  

## Installation  

### Prerequisites  
- Python 3.9+  
- Docker and Docker Compose  

### Steps  
1. **Clone the repository**:  
   ```bash
        git clone <https://gitlab.com/projet-agile2/devops-project.git>
   ```
2. **Create a virtual environment**:
    ```bash
        python3 -m venv env
        source env/bin/activate
    ```
3. **Install dependencies**:
    ```bash
        pip install -r requirements.txt
    ```
4. **Start the application**:
    ```bash
        uvicorn app.main:app --reload
    ```
5. **Access the API**:
    - **Swagger UI**: http://127.0.0.1:8000/docs.
    

## Contributing
1.  Fork the repository.
2.  Create a feature branch (git checkout -b feature/new-feature).
3.  Commit your changes (git commit -m 'Add new feature').
4.  Push to the branch (git push origin feature/new-feature).
5.  Open a Pull Request.



