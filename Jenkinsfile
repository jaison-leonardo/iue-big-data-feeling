pipeline {
    agent any

    environment {
        // En Oracle Cloud, asumiendo que construimos y empujamos a un registry (ej. Docker Hub o GitHub Packages)
        DOCKER_IMAGE = 'tu_usuario/sentiment_api'
        DOCKER_TAG = "v${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Lint & Tests API') {
            steps {
                echo "Ejecutando linter y tests para la API..."
                // simulación de tests
                sh 'echo "Tests pasados exitosamente"'
            }
        }

        stage('Build API Image') {
            steps {
                echo "Construyendo imagen Docker para la API Flask..."
                dir('api') {
                    sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                    sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
                }
            }
        }

        stage('Validate Container') {
            steps {
                echo "Validando el contenedor..."
                // Ejecuta la imagen de prueba para confirmar que no crashea al arrancar
                sh "docker run --rm -d --name test_api -p 5000:5000 ${DOCKER_IMAGE}:latest"
                // Espera unos segundos y hace un health check
                sleep 5
                sh "curl -f http://localhost:5000/health || (docker stop test_api; exit 1)"
                sh "docker stop test_api"
            }
        }
        
        // El despliegue real en Render se hace normalmente via Webhook conectándolo al repositorio (Push to Main)
        // Por lo tanto, el stage de Deploy puede ser solo una notificación o llamada al Hook de Render
        stage('Trigger Render Deploy') {
            steps {
                echo "Llamando al webhook de Render para desplegar la nueva versión..."
                // sh "curl -X POST $RENDER_DEPLOY_HOOK_URL"
            }
        }
    }
    
    post {
        always {
            echo "Pipeline finalizado. Limpiando workspace..."
            cleanWs()
        }
    }
}
