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

        stage('Unit and Integration Tests') {
            steps {
                script {
                    try {
                        sh """
                            . ${VENV_PATH}/bin/activate
                            mkdir -p test-results
                            pytest unit_test.py integration_test.py ${PYTEST_ARGS} --cov=. --cov-report=html:htmlcov
                        """
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error "Tests failed: ${e.message}"
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
                        reportName: 'Unit and Integration Test Coverage Report'
                    ])
                }
            }
        }

        // stage('Clean Up Old Logs and Generate Report') {
        //     environment {
        //         LOG_DIR = 'logs' // Directory where logs are stored
        //         BACKUP_DIR = 'backup_logs' // Directory to store backups
        //         REPORT_FILE = 'cleanup_report.txt' // Report file
        //     }
        //     steps {
        //         script {
        //             try {
        //                 // Step 1: Clean up logs older than 7 days
        //                 echo "Cleaning up old logs in ${LOG_DIR}..."
        //                 sh """
        //                     find ${LOG_DIR} -type f -mtime +7 -exec rm -f {} \;
        //                 """

        //                 // Step 2: Backup remaining logs
        //                 echo "Backing up remaining logs to ${BACKUP_DIR}..."
        //                 sh """
        //                     mkdir -p ${BACKUP_DIR}
        //                     cp ${LOG_DIR}/* ${BACKUP_DIR}/
        //                 """

        //                 // Step 3: Generate a cleanup summary report
        //                 echo "Generating cleanup report..."
        //                 sh """
        //                     echo "Cleanup Report - Build: ${BUILD_NUMBER}" > ${REPORT_FILE}
        //                     echo "Logs older than 7 days have been removed." >> ${REPORT_FILE}
        //                     echo "Remaining logs have been backed up to ${BACKUP_DIR}." >> ${REPORT_FILE}
        //                     echo "Cleanup completed on: $(date)" >> ${REPORT_FILE}
        //                 """

        //                 // Step 4: Archive the cleanup report
        //                 archiveArtifacts artifacts: "${REPORT_FILE}", allowEmptyArchive: true
        //                 echo "Cleanup report generated and archived successfully."

        //             } catch (Exception e) {
        //                 currentBuild.result = 'FAILURE'
        //                 error "Cleanup failed: ${e.message}"
        //             }
        //         }
        //     }
        // }



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