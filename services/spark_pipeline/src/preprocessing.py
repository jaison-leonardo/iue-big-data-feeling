from pyspark.sql.functions import lower, regexp_replace
from pyspark.ml.feature import Tokenizer, StopWordsRemover

def clean_text_df(df, text_col="texto", out_col="cleaned_text"):
    # Convertir a minúsculas
    df_clean = df.withColumn(out_col, lower(df[text_col]))
    # Remover caracteres especiales (deja solo alfanuméricos y espacios)
    df_clean = df_clean.withColumn(out_col, regexp_replace(df_clean[out_col], r"[^a-zA-Z0-9\sáéíóúÁÉÍÓÚñÑ]", ""))
    return df_clean

def get_preprocessing_stages(input_col="cleaned_text"):
    # Tokenizer
    tokenizer = Tokenizer(inputCol=input_col, outputCol="words")
    # StopWordsRemover
    # Por defecto usa stopwords en inglés. Si necesitas español, se pueden pasar: stopWords=StopWordsRemover.loadDefaultStopWords("spanish")
    stopwords_remover = StopWordsRemover(inputCol=tokenizer.getOutputCol(), outputCol="filtered_words")
    
    return [tokenizer, stopwords_remover]
