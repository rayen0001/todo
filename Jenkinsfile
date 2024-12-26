pipeline {
    agent none
    stages {
        stage('Lint') {
            agent {
                docker {
                    image 'qnib/pytest'
                }
            }
            steps {
                script {
                    echo "Installing dependencies for linting..."
                    sh '''
                        pip install -r requirements.txt
                        pip install pylint
                        pylint *.py
                    '''
                }
            }
        }
        stage('Unit Test') {
            agent {
                docker {
                    image 'qnib/pytest'
                }
            }
            steps {
                script {
                    echo "Setting up environment for unit tests..."
                    sh '''
                        pip install -r requirements.txt
                        pytest unit_test.py
                    '''
                }
            }
            post {
                always {
                    junit 'test-reports/unit_test_results.xml'
                }
            }
        }
        stage('Integration Test') {
            agent {
                docker {
                    image 'qnib/pytest'
                }
            }
            steps {
                script {
                    echo "Setting up environment for integration tests..."
                    sh '''
                        pip install -r requirements.txt
                        pytest integration_test.py
                    '''
                }
            }
            post {
                always {
                    junit 'test-reports/integration_test_results.xml'
                }
            }
        }
        stage('Security Check') {
            agent {
                docker {
                    image 'qnib/pytest'
                }
            }
            steps {
                script {
                    echo "Installing dependencies for security checks..."
                    sh '''
                        pip install -r requirements.txt
                        pip install bandit
                        bandit -r main.py -x B105,B104
                    '''
                }
            }
        }
    }
}
