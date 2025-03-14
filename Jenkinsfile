pipeline{
    agent any
    triggers {
        pollSCM('H/15 * * * *')
        cron('0 13 * * 1-5')
    }
    environment { 
        SMTP_SERVER = "smtp.gmail.com"
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