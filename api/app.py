from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import os
import datetime

from model.predictor import SentimentPredictor

app = Flask(__name__)
CORS(app)

# Inicializar el modelo globalmente una sola vez al levantar la API
predictor = SentimentPredictor()

# Variables de entorno requeridas
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:admin123@mongo:27017/?authSource=admin")
DB_NAME = os.getenv("DB_NAME", "sentiment_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "sentiments")

# Conexión a MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    client.admin.command('ping')
    print("Conexión a MongoDB exitosa.")
except Exception as e:
    print(f"Error conectando a MongoDB: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Conteo de sentimientos desde MongoDB"""
    try:
        pipeline = [
            {"$group": {"_id": "$sentimiento", "count": {"$sum": 1}}}
        ]
        stats = list(collection.aggregate(pipeline))
        result = {item["_id"]: item["count"] for item in stats if item["_id"] is not None}
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sentiments', methods=['GET'])
def get_sentiments():
    """Lista últimos registros (limit=20, ordenado por fecha desc)"""
    try:
        limit = int(request.args.get('limit', 20))
        # Se asume que timestamp es ISO string o Date object
        recent = list(collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit))
        return jsonify(recent), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict_sentiment():
    """Recibe texto, asigna sentimiento y guarda en BD"""
    data = request.get_json()
    if not data or 'texto' not in data:
        return jsonify({"error": "No texto provided"}), 400
    
    texto = data['texto']
    
    # Inferencia con modelo real (Scikit-Learn)
    try:
        resultado = predictor.predict(texto)
        prediccion = resultado["sentimiento"]
        confianza = resultado["confianza"]
    except Exception as e:
        return jsonify({"error": f"Error en inferencia del modelo: {str(e)}"}), 500
        
    timestamp = datetime.datetime.utcnow().isoformat()
    
    nuevo_registro = {
        "texto": texto,
        "sentimiento": prediccion,
        "confianza": confianza,
        "timestamp": timestamp
    }
    
    try:
        collection.insert_one(nuevo_registro)
        if "_id" in nuevo_registro:
            del nuevo_registro["_id"]
        return jsonify(nuevo_registro), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
