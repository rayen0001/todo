pipeline {
    agent any
    
    environment {
        PYTHON_IMAGE = 'python:3.9'
        DOCKER_IMAGE = 'docker:20.10.23'
        VENV_PATH = '.venv'
        PYTEST_ARGS = '-v --junitxml=test-results/junit.xml'
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '5'))
        timeout(time: 1, unit: 'HOURS')
        disableConcurrentBuilds()
    }
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    checkout scm
                }
            }
        }

        stage('Setup Environment') {
            steps {
                script {
                    try {
                        sh """
                            python3 -m venv ${VENV_PATH}
                            . ${VENV_PATH}/bin/activate
                            python -m pip install --upgrade pip
                            pip install -r requirements.txt
                            pip install pylint python-jose pytest pytest-cov coverage
                        """
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error "Failed to setup Python environment: ${e.message}"
                    }
                }
            }
        }

        stage('Static Code Analysis') {
            parallel {
                stage('Lint') {
                    steps {
                        script {
                            try {
                                sh """
                                    . ${VENV_PATH}/bin/activate
                                    pylint --output-format=parseable *.py > pylint-report.txt || true
                                """
                            } catch (Exception e) {
                                unstable "Linting found issues: ${e.message}"
                            }
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'pylint-report.txt', allowEmptyArchive: true
                        }
                    }
                }
                
                stage('Security Scan') {
                    steps {
                        script {
                            try {
                                sh """
                                    . ${VENV_PATH}/bin/activate
                                    pip install bandit
                                    bandit -r . -f html -o bandit-report.html || true
                                """
                            } catch (Exception e) {
                                unstable "Security scan found issues: ${e.message}"
                            }
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'bandit-report.html', allowEmptyArchive: true
                        }
                    }
                }
            }
        }

        stage('Unit Tests') {
            steps {
                script {
                    try {
                        sh """
                            . ${VENV_PATH}/bin/activate
                            mkdir -p test-results
                            pytest unit_test.py ${PYTEST_ARGS} --cov=. --cov-report=html
                        """
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error "Unit tests failed: ${e.message}"
                    }
                }
            }
            post {
                always {
                    junit 'test-results/junit.xml'
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }

        stage('Integration Tests') {
            steps {
                script {
                    try {
                        sh """
                            . ${VENV_PATH}/bin/activate
                            mkdir -p test-results
                            pytest integration_test.py ${PYTEST_ARGS} --cov=. --cov-report=html
                        """
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error "Integration tests failed: ${e.message}"
                    }
                }
            }
            post {
                always {
                    junit 'test-results/junit.xml'
                }
            }
        }

        stage('Combine Coverage Reports') {
            steps {
                script {
                    try {
                        sh """
                            . ${VENV_PATH}/bin/activate
                            coverage erase
                            coverage html -d htmlcov_combined
                        """
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error "Combining coverage reports failed: ${e.message}"
                    }
                }
            }
            post {
                always {
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov_combined',
                        reportFiles: 'index.html',
                        reportName: 'Combined Coverage Report'
                    ])
                }
            }
        }

        stage('Build and Push Docker Image') {
            environment {
                DOCKER_REGISTRY = 'docker.io' // Docker Hub registry
                DOCKER_REPOSITORY = 'rayen1/my-image' // Replace with your Docker Hub username and repository name
                DOCKER_CREDENTIALS = credentials('docker-hub-creds') // Jenkins credentials ID for Docker Hub
            }
            steps {
                script {
                    try {
                        def imageTag = "${DOCKER_REPOSITORY}:${BUILD_NUMBER}"
                        
                        // Build Docker image
                        sh """
                            docker build -t ${imageTag} .
                        """
                        
                        // Login and push to Docker Hub
                        sh """
                            echo ${DOCKER_CREDENTIALS_PSW} | docker login ${DOCKER_REGISTRY} -u ${DOCKER_CREDENTIALS_USR} --password-stdin
                            docker push ${imageTag}
                        """
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error "Docker build/push failed: ${e.message}"
                    }
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
            
            // Send notification
            emailext (
                subject: "Pipeline ${currentBuild.result}: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: """
                    <p>Build Status: ${currentBuild.result}</p>
                    <p>Build Number: ${env.BUILD_NUMBER}</p>
                    <p>Check console output at <a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a></p>
                """,
                recipientProviders: [[$class: 'DevelopersRecipientProvider'], [$class: 'RequesterRecipientProvider']],
                to: 'rayenaouechria@gmail.com'
            )
        }
        
        success {
            echo 'Pipeline completed successfully!'
        }
        
        failure {
            echo 'Pipeline failed!'
        }
    }
}