# Guía de Despliegue en Nube (Cloud)

Esta guía documenta los pasos necesarios para desplegar los diferentes componentes del proyecto SentimentStream en servicios en la nube gratuitos.

## 1. Almacenamiento: MongoDB Atlas

1. Crea una cuenta en [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. Crea un Cluster gratuito (M0 Sandbox).
3. En la sección "Database Access", crea un usuario de base de datos con contraseña.
4. En "Network Access", permite el acceso desde cualquier IP (`0.0.0.0/0`) ya que Render e IPs dinámicas necesitarán conectarse.
5. Obtén la URI de conexión (`mongodb+srv://...`) y guárdala para los siguientes pasos.

## 2. Backend API: Render

1. Crea una cuenta en [Render.com](https://render.com/).
2. Conecta tu repositorio de GitHub y crea un "Web Service".
3. Configura el Web Service:
   - **Root Directory**: `api`
   - **Environment**: Docker
4. En **Environment Variables**, agrega:
   - `MONGO_URI`: La URI obtenida de MongoDB Atlas.
   - `MONGO_DB`: `sentiment_db`
5. **Estrategia Anti-Sleep**: 
   - La capa gratuita de Render se duerme tras 15 minutos sin peticiones.
   - Entra a [cron-job.org](https://cron-job.org/), crea un cuenta y configura un job.
   - URL: `https://<tu-app-render>.onrender.com/health`
   - Ejecución: Cada 14 minutos.
   - Esto mantendrá la API siempre activa.

## 3. Frontend: Vercel

1. Entra a [Vercel](https://vercel.com/) y conecta tu repositorio.
2. Al importar el proyecto, configura:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
3. En **Environment Variables**, agrega:
   - `VITE_API_URL`: La URL pública de tu API en Render (ej. `https://<tu-app-render>.onrender.com/api`).
4. Haz clic en "Deploy".

## 4. Pipeline CI/CD: Jenkins (Oracle Cloud)

1. En [Oracle Cloud](https://cloud.oracle.com/), crea una instancia de Compute (Always Free ARM o Micro).
2. Instala Docker y Jenkins en la VM.
3. Configura Jenkins con el repositorio de GitHub.
4. El `Jenkinsfile` en la raíz está preparado para correr las pruebas y validar la construcción de la imagen.

## 5. Visualización: Power BI

1. Usa Power BI Desktop para conectar a MongoDB (mediante conector ODBC o exportando los datos).
2. Crea el dashboard.
3. Publica a **Power BI Service**.
4. En la web de Power BI, ve a Archivo > Insertar informe > **Publicar en la Web (público)**.
5. Toma el enlace del iframe generado y colócalo en el archivo `App.jsx` de la carpeta `frontend/src/`.
