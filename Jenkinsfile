pipeline{
    agent any
    triggers {
        pollSCM('H/15 * * * *')
        cron('0 13 * * 1-5')
    }
    environment { 
        SMTP_SERVER = "smtp.gmail.com"
        SONAR_SERVER = "Sonar"
        PYLINT_MIN_SCORE = 7
    }
    stages{
        stage('Build'){
            when {
                triggeredBy 'SCMTrigger'
            }
            steps{
                script{
                    def envDir = 'env/'
                    if (!fileExists(envDir)) {
                        sh "python3 -m venv ${envDir}"
                    }
                }
                sh './env/bin/pip install -q -r ./requirements.txt'
                sh './env/bin/pip install -q -r ./test_requirements.txt'
            }
        }
        stage('Lint tests'){
            when {
                triggeredBy 'SCMTrigger'
            }
            steps{
                sh './env/bin/python -m pylint --fail-under=$PYLINT_MIN_SCORE --output=report-pylint.txt .'
                sh './env/bin/python -m flake8 --output-file=flake8-report.txt'
            }
        }
        stage('SonarQube Analysis'){
            when {
                triggeredBy 'SCMTrigger'
            }
            steps{
                script {
                    def scannerHome = tool 'SonarQube'
                    withSonarQubeEnv(SONAR_SERVER) {
                        withCredentials([string(credentialsId: 'jobs-offer-sonarqube-pjtk', variable: 'PROJECT_TOKEN')]) {
                            sh '''
                            /var/jenkins_home/tools/hudson.plugins.sonar.SonarRunnerInstallation/SonarQube/bin/sonar-scanner -Dsonar.token=$PROJECT_TOKEN
                            '''
                        } 
                    }
                }
                waitForQualityGate abortPipeline: true, credentialsId: 'SONAR_TOKEN'
            }
        }
        stage('Run'){
            options {
                // Avoid Jenkins kill the processus during the scrapping
                timeout(time: 70, unit: 'MINUTES') 
            }
            when {
                triggeredBy 'TimerTrigger'
            }
            steps{
                sh "./env/bin/python -m run research -p $WORK_RESEARCH_PARAMETERS"
                withCredentials([usernamePassword(credentialsId: 'GmailCreds', usernameVariable: 'EMAIL_SENDER', passwordVariable: 'EMAIL_PASSWORD')]) {
                    sh 'env/bin/python -m run report -e'
                }
            }
        }
        stage('Manual Run'){
            when{
                triggeredBy 'UserIdCause'
            }
            steps{
                script {
                    
                    def command = input(
                        message: "Which command would you run?",
                        ok: "Run",
                        parameters: [
                            text(name: 'COMMAND', defaultValue: '-h', description: 'Who should I say hello to?')
                        ]
                    )
                    sh "./env/bin/python -m run ${command}"
                }
            }
        }
    }
}