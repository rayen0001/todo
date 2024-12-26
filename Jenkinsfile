pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.9'
    }

    stages {
        stage('Lint') {
            agent {
                docker {
                    image 'python:3.9'
                    reuseNode true
                }
            }
            steps {
                sh '''
                    python -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pylint
                    pylint *.py
                '''
            }
        }

        stage('Unit Tests') {
            agent {
                docker {
                    image 'python:3.9'
                    reuseNode true
                }
            }
            steps {
                sh '''
                    python -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pytest unit_test.py
                '''
            }
        }

        stage('Integration Tests') {
            agent {
                docker {
                    image 'python:3.9'
                    reuseNode true
                }
            }
            steps {
                sh '''
                    python -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pytest integration_test.py
                '''
            }
        }

        stage('Security Check') {
            agent {
                docker {
                    image 'python:3.9'
                    reuseNode true
                }
            }
            steps {
                sh '''
                    python -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install bandit
                    bandit -r main.py -x B105,B104
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    def dockerImage = docker.build("todo-app:${env.BUILD_ID}")
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}