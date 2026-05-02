pipeline {
    agent any

    environment {
        // Configuramos la variable de entorno para evitar warnings de npm
        CI = 'true'
    }

    stages {
        stage('1. Checkout') {
            steps {
                echo 'Clonando el repositorio...'
                checkout scm
            }
        }

        stage('2. Backend (API)') {
            steps {
                echo 'Instalando dependencias de Python para la API Flask...'
                dir('api') {
                    // Usamos sh para Linux/Docker. (Si tu Jenkins corre nativo en Windows usa 'bat' en lugar de 'sh')
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                        echo "Backend construido exitosamente."
                    '''
                }
            }
        }

        stage('3. Frontend (React/Vite)') {
            steps {
                echo 'Construyendo la aplicación React...'
                dir('apps/frontend') {
                    sh '''
                        npm install
                        npm run build
                        echo "Frontend construido exitosamente."
                    '''
                }
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline completado exitosamente. Todo el código compila correctamente.'
        }
        failure {
            echo '❌ Pipeline falló. Revisa los logs.'
        }
        always {
            echo 'Limpiando entorno...'
            cleanWs()
        }
    }
}
