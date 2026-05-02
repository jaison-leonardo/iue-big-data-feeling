import os
import joblib

class SentimentPredictor:
    def __init__(self):
        # El modelo se asume empaquetado en api/model/model.joblib gracias al nuevo script de entrenamiento
        self.model_path = os.getenv(
            "MODEL_PATH",
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'model.joblib'))
        )
        
        print(f"Inicializando SentimentPredictor desde: {self.model_path}")
        self.model = None
        self.load_model()

    def load_model(self):
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                print("Modelo scikit-learn cargado exitosamente en Flask.")
            else:
                print(f"ADVERTENCIA: No se encontró el modelo en {self.model_path}. Verifica que train.py se haya ejecutado.")
        except Exception as e:
            print(f"ERROR crítico cargando el modelo: {e}")

    def predict(self, text: str) -> dict:
        if not self.model:
            raise RuntimeError("El modelo no está cargado o no se encontró en la ruta especificada.")
        
        if not text or not isinstance(text, str) or not text.strip():
            raise ValueError("El texto proporcionado es inválido o está vacío.")

        # Inferencia rápida
        pred = self.model.predict([text])[0]
        probs = self.model.predict_proba([text])[0]
        
        # Extraer confianza usando la máxima probabilidad
        confianza = float(max(probs))

        return {
            "sentimiento": str(pred),
            "confianza": round(confianza, 4)
        }
