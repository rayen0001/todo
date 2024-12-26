pipeline {
    agent any
    environment {
        PYTHON_IMAGE = 'python:3.9'
        DOCKER_IMAGE = 'docker:20.10.23'
    }
    stages {
        stage('Lint') {
            when {
                not {
                    branch 'main'
                }
            }
            steps {
                script {
                    echo "Installing dependencies for linting..."
                    // Create virtual environment and install dependencies
                    sh 'python3 -m venv .venv'
                    sh '. .venv/bin/activate && pip install -r requirements.txt'
                    sh '. .venv/bin/activate && pip install pylint'
                    echo "Running linting..."
                    sh '. .venv/bin/activate && pylint *.py'
                }
            }
        }

        stage('Unit Test') {
            when {
                not {
                    branch 'main'
                }
            }
            steps {
                script {
                    echo "Setting up environment for unit tests..."
                    // Create virtual environment and install dependencies
                    sh 'python3 -m venv .venv'
                    sh '. .venv/bin/activate && pip install --upgrade pip'
                    sh '. .venv/bin/activate && pip install -r requirements.txt'
                    echo "Running unit tests..."
                    sh '. .venv/bin/activate && pytest unit_test.py'
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: '.venv/**', allowEmptyArchive: true
                }
            }
        }

        stage('Integration Test') {
            when {
                not {
                    branch 'main'
                }
            }
            steps {
                script {
                    echo "Setting up environment for integration tests..."
                    // Create virtual environment and install dependencies
                    sh 'python3 -m venv .venv'
                    sh '. .venv/bin/activate && pip install --upgrade pip'
                    sh '. .venv/bin/activate && pip install -r requirements.txt'
                    echo "Running integration tests..."
                    sh '. .venv/bin/activate && pytest integration_test.py'
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: '.venv/**', allowEmptyArchive: true
                }
            }
        }
    }
    post {
        always {
            cleanWs() // Clean workspace after every build
        }
    }
}
