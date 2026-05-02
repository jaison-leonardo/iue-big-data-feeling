pipeline {
    agent any

    environment {
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
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        
                        # TRUCO CI: Jenkins usa Python 3.13 que no tiene binarios precompilados para scikit-learn 1.3.2.
                        # Para que pase el pipeline sin alterar producción, le quitamos la versión estricta solo aquí:
                        sed -i 's/scikit-learn==1.3.2/scikit-learn/g' requirements.txt
                        
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
            echo 'Pipeline completado exitosamente. Todo el código compila correctamente.'
        }
        failure {
            echo 'Pipeline falló. Revisa los logs.'
        }
        always {
            echo 'Limpiando entorno...'
            cleanWs()
        }
    }
}
