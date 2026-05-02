# SentimentStream - Hito 3

Backend funcional local con Flask + MongoDB para análisis de sentimientos, integrando inferencia real de Machine Learning con Scikit-Learn.

## Arquitectura Híbrida de Machine Learning

El proyecto utiliza una **arquitectura híbrida** (Lambda Architecture pattern adaptado) para servir los modelos de NLP:

1. **Spark ML (Procesamiento Batch):**
   - Utilizado en `services/spark_pipeline/jobs/predict_batch.py`.
   - Lee volúmenes masivos de datos o bases de datos enteras, procesa las transformaciones usando procesamiento distribuido y vuelca los resultados directamente a MongoDB.

2. **Scikit-Learn (Inferencia en Tiempo Real - API Flask):**
   - Utilizado en `api/model/predictor.py`.
   - Se entrena en paralelo al modelo de Spark en `train.py` para tener exactamente el mismo pipeline lógico (`CountVectorizer` + `NaiveBayes`).
   - El modelo entrenado se exporta como `model.joblib`.
   - **Razón:** Spark es demasiado pesado (latencias de inicialización, overhead de JVM) para responder a una solicitud HTTP de un usuario final. Al instanciar un modelo pre-entrenado de scikit-learn en Flask, garantizamos respuestas ultrarrápidas (<100ms), mientras mantenemos la coherencia de los algoritmos de predicción.

## Requisitos Previos

- Docker y Docker Compose
- Python 3.10+ (Si deseas correr los tests localmente)

## Instrucciones de Ejecución

1. **Configurar el entorno**:
   Copia el archivo de variables de entorno:
   ```bash
   cp .env.example .env
   ```

2. **Levantar la Infraestructura**:
   Ve a la carpeta `infra` y ejecuta Docker Compose:
   ```bash
   cd infra
   docker-compose up -d --build
   ```

3. **Verificar estado de los servicios**:
   ```bash
   docker-compose ps
   ```

## Hito 5: Despliegue en la Nube (Cloud Deployment)

El sistema completo ha sido preparado para ser desplegado en plataformas gratuitas en la nube. Sigue estos pasos para obtener las URLs públicas de tu proyecto.

### 1. Base de Datos (MongoDB Atlas)
1. Ve a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) y crea un Cluster gratuito (M0).
2. En `Database Access`, crea un usuario y contraseña.
3. En `Network Access`, añade la IP `0.0.0.0/0` para permitir conexiones desde cualquier lugar (Render).
4. Copia el **Connection String** (asegúrate de reemplazar `<password>`).

### 2. Backend API (Render)
1. Crea una cuenta en [Render](https://render.com/) y selecciona **New Web Service**.
2. Conecta tu repositorio de GitHub apuntando a este proyecto.
3. Configuración del servicio:
   - **Root Directory:** `api`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app` (o `python app.py`)
4. Añade las siguientes **Environment Variables**:
   - `MONGO_URI`: *Tu Connection String de Atlas*
   - `MODEL_PATH`: `model/model.joblib`
   - `DB_NAME`: `sentiment_db`
   - `COLLECTION_NAME`: `sentiments`
5. Haz deploy y anota la URL pública (ej. `https://tu-api.onrender.com`).
6. Valida que funciona ingresando a `https://tu-api.onrender.com/health`.

### 3. Frontend Web (Vercel)
1. Entra a [Vercel](https://vercel.com/) y selecciona **Add New Project**.
2. Conecta tu repositorio y selecciona la carpeta **`apps/frontend`** como Root Directory.
3. Framework Preset: **Vite** (Vercel lo detecta automáticamente).
4. Añade las **Environment Variables**:
   - `VITE_API_URL`: *URL de tu API en Render* + `/api` (ej. `https://tu-api.onrender.com/api`)
   - `VITE_POWERBI_URL`: *Tu URL pública de Power BI*
5. Haz Deploy.

¡Listo! Una vez finalice, tendrás tu Frontend accesible públicamente consumiendo la API alojada en Render y guardando predicciones en Atlas.

## Endpoints Disponibles

La API estará disponible en `http://localhost:5000`.

- `GET /health` : Retorna el estado de la API.
- `GET /api/stats` : Conteo total de sentimientos registrados.
- `GET /api/sentiments?limit=20` : Lista de los últimos registros.
- `POST /api/predict` : Procesa un nuevo texto.

### Ejemplo de Request POST `/predict` (Prueba)

Usando **cURL**:
```bash
curl -X POST http://localhost:5000/api/predict \
     -H "Content-Type: application/json" \
     -d '{"texto": "Este es un excelente servicio, estoy muy feliz!"}'
```

Ejemplo de respuesta:
```json
{
  "texto": "Este es un excelente servicio, estoy muy feliz!",
  "sentimiento": "positivo",
  "confianza": 0.87,
  "timestamp": "2026-05-01T14:30:00.000Z"
}
```

## Pruebas (Tests)

Para ejecutar las pruebas localmente (fuera de Docker):
```bash
cd api
pip install -r requirements.txt
pytest tests/
```
