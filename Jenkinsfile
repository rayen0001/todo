pipeline {
    agent any
    stages {
    stage('Python Test') {
        steps {
                sh 'python3 --version'
                sh 'pip3 install pytest'
                sh 'pytest tests/'
    }
}
}
}
