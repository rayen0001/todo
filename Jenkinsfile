pipeline {
    agent any
    
    stages {
        stage('Lint') {
            steps {
                sh '''#!/bin/bash
                    python3 -m pip install --user pylint
                    python3 -m pip install --user -r requirements.txt
                    python3 -m pylint *.py || true
                '''
            }
        }
        
        stage('Unit Tests') {
            steps {
                sh '''#!/bin/bash
                    python3 -m pip install --user pytest
                    python3 -m pip install --user -r requirements.txt
                    python3 -m pytest unit_test.py
                '''
            }
        }
        
        stage('Integration Tests') {
            steps {
                sh '''#!/bin/bash
                    python3 -m pip install --user pytest
                    python3 -m pytest integration_test.py
                '''
            }
        }
        
        stage('Security Check') {
            steps {
                sh '''#!/bin/bash
                    python3 -m pip install --user bandit
                    python3 -m bandit -r main.py -x B105,B104 || true
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh '''#!/bin/bash
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