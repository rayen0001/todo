pipeline {
    agent any

    stages {
        stage('Setup Python Environment') {
            steps {
                sh '''
                    apt-get update
                    apt-get install -y python3 python3-pip python3-venv
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pylint
                    pylint *.py || true
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    . .venv/bin/activate
                    pytest unit_test.py
                '''
            }
        }

        stage('Integration Tests') {
            steps {
                sh '''
                    . .venv/bin/activate
                    pytest integration_test.py
                '''
            }
        }

        stage('Security Check') {
            steps {
                sh '''
                    . .venv/bin/activate
                    pip install bandit
                    bandit -r main.py -x B105,B104 || true
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t todo-app:${BUILD_NUMBER} .
                '''
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}