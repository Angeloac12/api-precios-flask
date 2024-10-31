import os
from flask import Flask, request, jsonify
import requests
from rapidfuzz import process, fuzz

# Configuración de la API Supabase
API_URL = "https://mrpitiwepgfuomjcmgkh.supabase.co/rest/v1/base_precios_por_cliente"
HEADERS = {
    "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1ycGl0aXdlcGdmdW9tamNtZ2toIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzAyMTM4OTIsImV4cCI6MjA0NTc4OTg5Mn0.A3tlcIUcMFCukedf0SsmqXkA6ze3Xlamg71tBIw9Bik",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1ycGl0aXdlcGdmdW9tamNtZ2toIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzAyMTM4OTIsImV4cCI6MjA0NTc4OTg5Mn0.A3tlcIUcMFCukedf0SsmqXkA6ze3Xlamg71tBIw9Bik"
}

app = Flask(__name__)

def obtener_productos():
    """Consulta todos los productos desde la base de datos Supabase."""
    response = requests.get(API_URL, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        return []

def buscar_opciones_cercanas(consulta, umbral=80, max_opciones=5):
    """Busca las 5 opciones más cercanas usando coincidencia difusa."""
    productos = obtener_productos()
    productos_candidatos = []

    # Iterar sobre cada producto y calcular la similitud con la consulta
    for producto in productos:
        detalles_producto = f"{producto['product']} {producto['brand']} {producto.get('category', '')} {producto['price']}"
        
        # Calcular el puntaje de similitud
        puntuacion = fuzz.token_set_ratio(consulta, detalles_producto)
        
        # Añadir productos que cumplen con el umbral de similitud
        if puntuacion >= umbral:
            productos_candidatos.append((producto, puntuacion))

    # Ordenar los productos por puntaje en orden descendente
    productos_candidatos = sorted(productos_candidatos, key=lambda x: x[1], reverse=True)

    # Seleccionar las 5 mejores opciones
    mejores_opciones = [producto for producto, _ in productos_candidatos[:max_opciones]]
    
    return mejores_opciones

@app.route('/consulta_natural', methods=['GET'])
def consulta_natural():
    """Endpoint para recibir consultas en lenguaje natural."""
    consulta = request.args.get('consulta')
    if not consulta:
        return jsonify({"error": "Debes especificar una consulta en lenguaje natural"}), 400

    # Buscar las opciones más cercanas basadas en la consulta
    mejores_opciones = buscar_opciones_cercanas(consulta)

    if mejores_opciones:
        return jsonify(mejores_opciones)
    else:
        return jsonify({"error": "No se encontraron productos que coincidan con la consulta"}), 404

@app.route('/')
def home():
    """Endpoint básico para verificar que la API funciona."""
    return "API funcionando correctamente en Render"

if __name__ == '__main__':
    # Usamos el puerto asignado por Render, o 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
