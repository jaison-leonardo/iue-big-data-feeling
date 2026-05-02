import os
import sys
import datetime
import re
from dotenv import load_dotenv

# Agregar src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Solo en Windows aplicar hacks de entorno para Hadoop
if os.name == 'nt':
    hadoop_home = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'hadoop'))
    if os.path.exists(hadoop_home):
        os.environ['HADOOP_HOME'] = hadoop_home
        os.environ['PATH'] = os.path.join(hadoop_home, 'bin') + os.pathsep + os.environ.get('PATH', '')

from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel
from pyspark.sql.functions import col
from pymongo import MongoClient

from src.preprocessing import clean_text_df

# Cargar variables de entorno
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../.env'))
if os.path.exists(env_path):
    load_dotenv(env_path)

def get_mongo_collection():
    """Retorna la colección de MongoDB usando pymongo."""
    uri = os.getenv("MONGO_URI", "mongodb://admin:admin123@localhost:27017/?authSource=admin")
    db_name = os.getenv("DB_NAME", "sentiment_db")
    coll_name = os.getenv("COLLECTION_NAME", "sentiments")

    # Si estamos corriendo fuera de docker pero la URI dice "mongo:"
    # En Docker, RUNNING_IN_DOCKER debería estar seteado o simplemente probar resolverlo.
    # Como tu docker-compose pasa MONGO_URI apuntando a "mongo", no se reemplazará si se corre por docker-compose.
    # Pero si lo corres local de Windows, cambiará a localhost.
    if "mongo:" in uri and not os.path.exists("/.dockerenv"):
        uri = uri.replace("mongo:", "localhost:")

    client = MongoClient(uri)
    return client[db_name][coll_name]

def main():
    spark = SparkSession.builder \
        .appName("SentimentPredictBatch") \
        .master("local[*]") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models', 'sentiment_model'))
    
    # Soporte para Docker y Windows Local
    docker_data_path = "/app/data/dataset_sentimientos_500.csv"
    local_data_path  = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../data/dataset_sentimientos_500.csv'))
    csv_path = docker_data_path if os.path.exists(docker_data_path) else local_data_path

    if not os.path.exists(model_dir):
        print(f"ERROR: No se encontró el modelo en {model_dir}. ¡Ejecuta train.py primero!")
        return

    if not os.path.exists(csv_path):
        print(f"ERROR: No se encontraron los datos en {csv_path}.")
        return

    print(f"Cargando modelo serializado desde {model_dir}...")
    model = PipelineModel.load(model_dir)

    print(f"Cargando datos para predecir desde {csv_path}...")
    df = spark.read.csv(csv_path, header=True, inferSchema=True).limit(10)

    df_clean = clean_text_df(df, text_col="texto", out_col="cleaned_text")

    print("Generando predicciones con Spark ML...")
    predictions = model.transform(df_clean)

    print("Extrayendo resultados al Driver...")
    predictions_str = predictions.withColumn("prob_str", col("probability").cast("string"))
    rows = predictions_str.select("texto", "prediction", "prob_str").collect()

    documents = []
    current_time = datetime.datetime.utcnow().isoformat()
    mapping = {0.0: "positivo", 1.0: "negativo", 2.0: "neutral"}

    for row in rows:
        try:
            nums = re.findall(r"[\d\.]+", row["prob_str"])
            prob_values = [float(n) for n in nums]
            confianza = max(prob_values) if prob_values else 0.0
        except Exception:
            confianza = 0.0

        pred_val = float(row["prediction"])
        sentimiento_predicho = mapping.get(pred_val, "desconocido")

        documents.append({
            "texto":       row["texto"],
            "sentimiento": sentimiento_predicho,
            "confianza":   confianza,
            "timestamp":   current_time,
            "origen":      "spark_batch"
        })

    print(f"Insertando {len(documents)} documentos en MongoDB...")
    try:
        collection = get_mongo_collection()
        if documents:
            collection.insert_many(documents)
            print("¡Inserción en MongoDB completada con éxito!")
        else:
            print("No hay documentos para insertar.")
    except Exception as e:
        print(f"ERROR insertando en MongoDB: {e}")

    spark.stop()


if __name__ == "__main__":
    main()