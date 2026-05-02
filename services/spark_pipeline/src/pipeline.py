from pyspark.ml import Pipeline

def build_spark_pipeline(preprocessing_stages, feature_stages, model_stages):
    """
    Construye y retorna el Pipeline completo uniendo todos los stages.
    """
    stages = preprocessing_stages + feature_stages + model_stages
    return Pipeline(stages=stages)
