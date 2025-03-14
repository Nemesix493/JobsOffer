pipeline{
    agent any
    triggers {
        pollSCM('H/30 * * * *')
    }
    stages{
        stage('Build'){
            when {
                triggeredBy 'SCMTrigger'
            }
            steps{
                script{
                    def envDir = 'env/'
                    if (fileExists(envDir)) {
                        sh "python3 -m venv ${envDir}"
                    }
                }
            }
        }
    }
}