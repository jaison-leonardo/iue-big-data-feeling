# Funciones utilitarias para el modelo de la API
# (Actualmente vacías porque el Pipeline de scikit-learn se encarga del preprocesamiento internamente)

def preprocess_text(text: str) -> str:
    """Aplica preprocesamiento básico si es necesario antes de pasar al modelo."""
    return text.strip().lower()
