pipeline {
    agent any // Run on any available executor

    stages {
        stage('Simple Python Test') {
            steps {
                // Run a simple Python command directly
                sh '''
                    python -c "print('Hello from Python!')"
                '''
            }
        }
    }
}