# SentimentStream: Sistema Distribuido de Análisis de Sentimientos

## 1. Introducción

**SentimentStream** es una solución arquitectónica integral diseñada para el análisis de sentimientos en texto mediante el uso de algoritmos de Machine Learning. El proyecto implementa una variación de la **Arquitectura Lambda**, permitiendo procesar y analizar datos textuales en dos modalidades operativas: procesamiento masivo distribuido (Batch) e inferencia transaccional en tiempo real (Speed). 

Este repositorio consolida el desarrollo del ecosistema completo, abarcando desde la ingesta y vectorización de datos hasta la integración continua y el despliegue en infraestructuras Cloud.

---

## 2. Arquitectura del Sistema

El ecosistema se compone de capas funcionales estrictamente delimitadas para garantizar alta disponibilidad, baja latencia computacional y escalabilidad horizontal:

### 2.1. Capa de Procesamiento Batch (Apache Spark)
- **Componente Central:** `services/spark_pipeline/jobs/predict_batch.py` y `train.py`.
- **Propósito:** Responsable del procesamiento distribuido de conjuntos de datos masivos. Emplea `Spark MLlib` para la extracción de características textuales y la vectorización de términos. Su ejecución asíncrona es ideal para la consolidación de modelos estadísticos robustos y la inserción de métricas analíticas directas a la base de datos sin afectar el rendimiento transaccional.

### 2.2. Capa de Inferencia en Tiempo Real (Scikit-Learn & Flask)
- **Componente Central:** `api/model/predictor.py` y entorno WSGI (`gunicorn`).
- **Propósito:** Resuelve la problemática de latencia inherente a la instanciación de la JVM (Java Virtual Machine) que requiere Spark. En paralelo al entrenamiento distribuido, se exporta una representación optimizada del modelo predictivo (`CountVectorizer` y clasificador `Multinomial Naive Bayes`) utilizando la librería `scikit-learn`. El modelo se expone mediante una interfaz RESTful sobre el framework Flask, reduciendo el tiempo de respuesta en la inferencia a valores sub-100ms.

### 2.3. Capa de Presentación (React & Vite)
- **Componente Central:** `apps/frontend/`.
- **Propósito:** Single Page Application (SPA) que provee una interfaz gráfica asíncrona. Se apoya en heurísticas reactivas para reflejar inmediatamente las variaciones estadísticas reportadas por la API, integrando adicionalmente cuadros de mando (dashboards) avanzados construidos en Microsoft Power BI para la inteligencia de negocios (BI).

---

## 3. Estrategia de Despliegue en la Nube (Cloud Deployment)

El sistema ha sido estructurado siguiendo el paradigma de un Monorepo, facilitando su despliegue automatizado y segmentado en múltiples plataformas especializadas de Cloud Computing.

### 3.1. Persistencia de Datos (MongoDB Atlas)
- **Proveedor:** MongoDB Atlas.
- **Configuración:** Implementación de un clúster de bases de datos NoSQL para la persistencia transaccional. Requiere configuración explícita de `Network Access` (IP `0.0.0.0/0`) para mitigar rechazos a nivel TLS durante las peticiones asíncronas desde instancias Cloud dinámicas.

### 3.2. Despliegue del Backend RESTful (Render)
- **Proveedor:** Render Cloud Platform.
- **Configuración Requerida:** 
  - Directorio Raíz: `api`
  - Ejecución WSGI: `gunicorn app:app`
  - Variables de Entorno Obligatorias:
    - `MONGO_URI`: Cadena de conexión hacia MongoDB Atlas.
    - `MODEL_PATH`: Ubicación relativa del modelo exportado (`model/model.joblib`).
    - `DB_NAME` y `COLLECTION_NAME`.

### 3.3. Despliegue del Frontend Cliente (Vercel)
- **Proveedor:** Vercel.
- **Configuración Requerida:** 
  - Directorio Raíz: `apps/frontend`
  - Variables de Entorno Obligatorias:
    - `VITE_API_URL`: Dirección de la API pública desplegada.
    - `VITE_POWERBI_URL`: URL del reporte analítico embebido.

---

## 4. Integración Continua y Entrega Continua (CI/CD)

El repositorio incorpora una canalización de despliegue automatizado gestionada mediante **Jenkins**.

### Estructura del Pipeline (`Jenkinsfile`)
El flujo de validación automática se rige por tres fases declarativas que garantizan la integridad del código previo a cualquier despliegue productivo:
1. **Source Control Checkout:** Sincronización criptográfica con el repositorio remoto.
2. **Backend Validation:** Creación de un entorno virtual aislado para validar las dependencias algorítmicas de Python (`requirements.txt`). Implementa mitigaciones dinámicas en el pipeline para la resolución automática de dependencias que carecen de binarios pre-compilados en entornos virtualizados de pruebas (e.g., resolviendo colisiones con versiones recientes de Python mediante `sed`).
3. **Frontend Compilation:** Descarga de paquetes Node.js (`npm install`) y ensamblaje de los artefactos estáticos listos para distribución (SPA build).

---

## 5. Documentación de Endpoints REST (API)

A continuación, se detalla la especificación de los recursos expuestos por la API alojada en la raíz del entorno productivo (por defecto `http://localhost:5000` en entornos de desarrollo).

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Validación de disponibilidad del servicio y tolerancia a fallos. |
| `GET` | `/api/stats` | Agrupación analítica y agregación de sentimientos globales mediante pipelines O-D en MongoDB. |
| `GET` | `/api/sentiments?limit=N` | Recuperación paginada del histórico reciente de inferencias. |
| `POST` | `/api/predict` | End-point transaccional. Ingiere el texto (payload JSON `{"texto": "..."}`), lo procesa a través del modelo Naive Bayes y retorna la clasificación estadística con su respectivo factor de confianza. |

---

