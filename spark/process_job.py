from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, current_timestamp
import os

def main():
    # Inicializar Spark Session con soporte para MongoDB Atlas
    # En producción (fuera de Docker Compose), esta URI apuntará a Atlas
    mongo_uri = os.getenv("MONGO_URI", "mongodb://admin:admin123@localhost:27017/sentiment_db.sentiments?authSource=admin")
    
    spark = SparkSession.builder \
        .appName("SentimentProcessJob") \
        .config("spark.mongodb.output.uri", mongo_uri) \
        .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
        .master("local[*]") \
        .getOrCreate()
        
    spark.sparkContext.setLogLevel("ERROR")
    print("Iniciando procesamiento de sentimientos (Script Independiente)...")

    # Asumimos que el CSV está en la carpeta data
    csv_path = os.getenv("CSV_PATH", "../data/dataset_sentimientos_500.csv")
    
    if not os.path.exists(csv_path):
        print(f"Error: No se encontró el archivo en {csv_path}")
        return

    # Leer datos
    df = spark.read.csv(csv_path, header=True, inferSchema=True)
    print(f"Total de registros a procesar: {df.count()}")

    # Agregar timestamp
    df_processed = df.withColumn("processed_at", current_timestamp())

    # TODO: Integración con modelo ML entrenado previamente

    # Escribir a MongoDB (Atlas o Local)
    print(f"Guardando datos en MongoDB usando URI configurada...")
    df_processed.write \
        .format("mongo") \
        .mode("append") \
        .save()
        
    print("Proceso finalizado. Datos guardados exitosamente en la base de datos.")
    spark.stop()

if __name__ == "__main__":
    main()
