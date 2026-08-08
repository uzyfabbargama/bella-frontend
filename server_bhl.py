# server_bhl.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from bhl_opt import main, BellaSubconsciente, Numeraso_update, save_state
from bella_subconsciente import BellaSubconsciente

app = Flask(__name__)
CORS(app)  # Permite conexiones desde cualquier frontend

# Estado global del servidor
bella = BellaSubconsciente(archivo_xrp="bella.xrp")

@app.route('/chat', methods=['POST'])
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    user_id = data.get('user_id', 'anonimo')
    
    # === PROCESAR MENSAJE CON BELLA ===
    # 1. Entrenar a Bella con el mensaje del usuario
    bella.entrenar(user_message)
    
    # 2. Obtener respuesta de Bella (susurro)
    respuesta = bella.susurrar(cantidad_palabras=10)
    
    # 3. Guardar estado (opcional)
    # bella.guardar()
    
    return jsonify({
        'response': respuesta,
        'status': 'ok',
        'user_id': user_id
    })
    
    # 1. Procesar mensaje con BHL
    # 2. Actualizar Numeraso
    # 3. Obtener respuesta de Bella
    # 4. Guardar estado
    
    return jsonify({
        'response': respuesta,
        'status': 'ok'
    })

@app.route('/login', methods=['POST'])
def login():
    # Autenticación XOR Session
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
