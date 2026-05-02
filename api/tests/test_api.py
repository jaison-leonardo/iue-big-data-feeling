import pytest
import sys
import os

# Agregamos la ruta padre (api/) al PYTHONPATH para que encuentre app.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Forzamos la conexión a localhost para que los tests (que se ejecutan fuera de Docker) encuentren MongoDB
os.environ["MONGO_URI"] = "mongodb://admin:admin123@localhost:27017/?authSource=admin"

from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Testea que el endpoint /health responda 200 y status ok"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'

def test_predict_sentiment(client):
    """Testea que el endpoint /api/predict procese un texto correctamente"""
    payload = {"texto": "Este es un mensaje de prueba"}
    response = client.post('/api/predict', json=payload)
    
    assert response.status_code == 201
    data = response.get_json()
    
    assert 'texto' in data
    assert data['texto'] == payload['texto']
    assert 'sentimiento' in data
    assert data['sentimiento'] in ['positivo', 'negativo', 'neutral']
    assert 'confianza' in data
    assert 0.0 <= data['confianza'] <= 1.0
    assert 'timestamp' in data

def test_predict_sentiment_no_text(client):
    """Testea que falle si no se envía texto"""
    response = client.post('/api/predict', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
