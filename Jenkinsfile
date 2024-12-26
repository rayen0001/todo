pipeline {
    agent any // Run on any available executor

    stages {
        stage('Python Test') {
            agent { docker { image 'python:3.9' } } // Run this stage in a Python 3.9 container
            steps {
                sh 'python -c "print(\'Hello from Python in Docker!\')"'
                sh 'pip install requests'
                sh 'python -c "import requests; print(requests.get(\'https://www.google.com\').status_code)"'
            }
        }
    }
}