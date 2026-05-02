from pyspark.ml.feature import HashingTF, IDF, StringIndexer
from pyspark.ml.classification import NaiveBayes

def get_feature_engineering_stages(input_col="filtered_words"):
    # HashingTF (crea el vector de frecuencias)
    hashingTF = HashingTF(inputCol=input_col, outputCol="rawFeatures", numFeatures=2000)
    # IDF (Ponderación)
    idf = IDF(inputCol="rawFeatures", outputCol="features")
    return [hashingTF, idf]

def get_model_stages(label_col="etiqueta"):
    # StringIndexer para transformar las etiquetas de texto a números
    label_indexer = StringIndexer(inputCol=label_col, outputCol="label", handleInvalid="skip")
    
    # Clasificador NaiveBayes
    nb = NaiveBayes(smoothing=1.0, modelType="multinomial")
    return [label_indexer, nb]
