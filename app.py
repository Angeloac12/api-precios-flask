from flask import Flask, request, jsonify
import requests
from rapidfuzz import process

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

    print(f"Estado de la respuesta: {response.status_code}")  # Depuración
    print(f"Contenido de la respuesta: {response.text}")  # Depuración

    if response.status_code == 200:
        productos = response.json()
        print(f"Productos recuperados: {productos}")  # Depuración adicional
        return productos
    else:
        return []

def buscar_producto_aproximado(consulta):
    """Busca el producto más cercano usando coincidencia difusa."""
    productos = obtener_productos()
    if not productos:
        return {"error": "No hay productos disponibles para comparar"}

    # Extraer la lista de nombres de productos
    nombres = [producto['product'] for producto in productos]

    # Intentar encontrar la mejor coincidencia
    resultado = process.extractOne(consulta, nombres)

    if resultado:  # Verificar que extractOne no devuelva None
        mejor_match, score, index = resultado

        if score > 60:  # Si la coincidencia es mayor a 60
            producto_encontrado = productos[index]
            return {
                "id": producto_encontrado['id'],
                "product": producto_encontrado['product'],
                "brand": producto_encontrado['brand'],
                "price": producto_encontrado['price1']
            }
        else:
            return {"error": "No se encontró un producto suficientemente similar"}
    else:
        return {"error": "No se encontraron productos para comparar"}

@app.route('/consulta', methods=['GET'])
def consulta():
    """Endpoint para recibir la consulta del producto."""
    producto = request.args.get('producto')
    if not producto:
        return jsonify({"error": "Debes especificar un producto"}), 400

    resultado = buscar_producto_aproximado(producto)
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True)
