import os
import sys
import ctypes
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib

# Agregar src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Forzar PYSPARK_PYTHON a nivel de script para ignorar la variable incorrecta de la terminal
def get_short_path_name(long_name):
    try:
        buf = ctypes.create_unicode_buffer(260)
        ctypes.windll.kernel32.GetShortPathNameW(long_name, buf, 260)
        return buf.value if buf.value else long_name
    except:
        return long_name

short_python_path = get_short_path_name(sys.executable)
os.environ['PYSPARK_PYTHON'] = short_python_path
os.environ['PYSPARK_DRIVER_PYTHON'] = short_python_path

# Solución para Windows: Configurar HADOOP_HOME apuntando a los binarios descargados
hadoop_home = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'hadoop'))
os.environ['HADOOP_HOME'] = hadoop_home
os.environ['PATH'] = os.path.join(hadoop_home, 'bin') + os.pathsep + os.environ.get('PATH', '')

from pyspark.sql import SparkSession
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

from src.preprocessing import clean_text_df, get_preprocessing_stages
from src.model import get_feature_engineering_stages, get_model_stages
from src.pipeline import build_spark_pipeline

def main():
    spark = SparkSession.builder \
        .appName("SentimentTrainJob") \
        .master("local[*]") \
        .getOrCreate()
        
    spark.sparkContext.setLogLevel("ERROR")
    
    # Rutas dinámicas
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    csv_path = os.path.join(base_dir, 'data', 'dataset_sentimientos_500.csv')
    model_dir = os.path.join(os.path.dirname(__file__), '..', 'models', 'sentiment_model')
    
    print(f"Cargando dataset desde: {csv_path}")
    if not os.path.exists(csv_path):
        print(f"ERROR: Dataset no encontrado en {csv_path}")
        return
        
    df = spark.read.csv(csv_path, header=True, inferSchema=True)
    
    # Validar si el dataset tiene las columnas necesarias
    if "texto" not in df.columns or "etiqueta" not in df.columns:
        print("ERROR: El dataset debe tener las columnas 'texto' y 'etiqueta'")
        return
    
    # 1. Preprocesamiento (limpieza de df)
    df_clean = clean_text_df(df, text_col="texto", out_col="cleaned_text")
    
    # 2. División de datos (Train/Test)
    train_data, test_data = df_clean.randomSplit([0.8, 0.2], seed=42)
    print(f"Datos de entrenamiento: {train_data.count()}, Datos de prueba: {test_data.count()}")
    
    # 3. Obtener stages del pipeline
    prep_stages = get_preprocessing_stages(input_col="cleaned_text")
    feat_stages = get_feature_engineering_stages(input_col="filtered_words")
    mod_stages = get_model_stages(label_col="etiqueta")
    
    # 4. Construir pipeline
    pipeline = build_spark_pipeline(prep_stages, feat_stages, mod_stages)
    
    # 5. Entrenar el modelo
    print("Entrenando modelo (Pipeline completo)...")
    model = pipeline.fit(train_data)
    
    # 6. Evaluar
    print("Evaluando modelo con datos de prueba...")
    predictions = model.transform(test_data)
    
    evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
    accuracy = evaluator.evaluate(predictions)
    
    print("=====================================")
    print(f"Precisión (Accuracy) del modelo: {accuracy:.4f}")
    print("=====================================")
    
    # 7. Guardar modelo serializado Spark
    print(f"Guardando modelo en: {model_dir}")
    model.write().overwrite().save(model_dir)
    print("¡Entrenamiento Spark finalizado exitosamente!")
    
    # 8. Entrenar y Guardar modelo equivalente en scikit-learn para inferencia en API
    print("Entrenando modelo equivalente en scikit-learn para la API...")
    pdf = pd.read_csv(csv_path)
    
    # Validar que no haya valores nulos en texto
    pdf = pdf.dropna(subset=['texto', 'etiqueta'])
    
    sklearn_pipeline = Pipeline([
        ('vect', CountVectorizer(stop_words='english', lowercase=True)),
        ('clf', MultinomialNB())
    ])
    
    sklearn_pipeline.fit(pdf['texto'], pdf['etiqueta'])
    
    # Validar modelo en entrenamiento
    acc = sklearn_pipeline.score(pdf['texto'], pdf['etiqueta'])
    print(f"Precisión scikit-learn (sobre datos de entrenamiento): {acc:.4f}")
    
    joblib_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
    os.makedirs(joblib_dir, exist_ok=True)
    joblib_path = os.path.join(joblib_dir, 'model.joblib')
    
    # También guardamos una copia en la carpeta de la API para que el Dockerfile la empaquete para producción
    api_model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../api/model'))
    os.makedirs(api_model_dir, exist_ok=True)
    api_joblib_path = os.path.join(api_model_dir, 'model.joblib')
    
    print(f"Guardando modelo scikit-learn en: {joblib_path}")
    joblib.dump(sklearn_pipeline, joblib_path)
    
    print(f"Guardando copia para la API en: {api_joblib_path}")
    joblib.dump(sklearn_pipeline, api_joblib_path)
    
    print("¡Entrenamiento scikit-learn finalizado exitosamente!")
    
    spark.stop()

if __name__ == "__main__":
    main()
