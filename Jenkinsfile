pipeline {
    agent any // Run on any available executor

    stages {
        stage('Simple Python Test') {
            steps {
                // Run a simple Python command directly
                sh '''
                    python -c "print('Hello from Python!')"
                '''

                // Run a Python script (you'll need to have a script in your repo)
                // Assuming you have a file called 'test.py'
                //sh 'python test.py'

                // Example using a Docker container (more isolated and recommended)
                sh '''
                    docker run --rm -v $(pwd):/app -w /app python:3.9 sh -c "python -c \\"print('Hello from Python in Docker!')\\""
                '''
                sh '''
                    docker run --rm -v $(pwd):/app -w /app python:3.9 sh -c "pip install requests && python -c \\"import requests; print(requests.get('https://www.google.com').status_code)\\""
                '''
            }
        }
    }
}