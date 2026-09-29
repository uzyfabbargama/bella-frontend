# server_bhl.py (versión CORREGIDA)
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from pathlib import Path
from datetime import datetime
from xor_auth import xorid, login_user, guardar_usuario
from loader import cargar_personaje
from creator import crear_personaje
from bella_subconsciente import BellaSubconsciente
import base64

# Importar funciones de BHL en modo servidor
os.environ["BHL_MODO"] = "servidor"
from bhl_opt import inicializar_personaje, procesar_mensaje

app = Flask(__name__)
CORS(app)

# ============================================================
# RUTAS DE AUTENTICACIÓN
# ============================================================

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Faltan datos'}), 400
    
    try:
        guardar_usuario(username, password)
        return jsonify({'status': 'success', 'message': 'Usuario creado'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Faltan datos'}), 400
    
    resultado = login_user(username, password)
    if resultado['status'] == 'success':
        return jsonify(resultado)
    else:
        return jsonify(resultado), 401

# ============================================================
# RUTAS DE PERSONAJES
# ============================================================

@app.route('/api/personajes', methods=['GET'])
def listar_personajes():
    ruta = Path("server-data/personajes")
    personajes = []
    
    for carpeta in ruta.iterdir():
        if carpeta.is_dir():
            nucleo_path = carpeta / "nucleo.json"
            if nucleo_path.exists():
                with open(nucleo_path, 'r') as f:
                    nucleo = json.load(f)["nucleo"]
                personajes.append({
                    "nombre": nucleo["name"],
                    "icon": nucleo["icon"],
                    "intro": nucleo["intro"],
                    "fecha": nucleo.get("datetime", "desconocida")
                })
    
    return jsonify({"personajes": personajes})

@app.route('/api/personajes/<nombre>', methods=['GET'])
def obtener_personaje(nombre):
    try:
        personaje = cargar_personaje(nombre)
        return jsonify({
            'status': 'success',
            'personaje': {
                'nombre': personaje['name'],
                'intro': personaje['intro'],
                'peculiarity': personaje['peculiarity'],
                'bondad': personaje['initial_Bondad'],
                'hostilidad': personaje['initial_Hostilidad'],
                'logica': personaje['initial_Logica']
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 404

@app.route('/api/personajes/crear', methods=['POST'])
def crear_nuevo_personaje():
    data = request.json
    
    nombre = data.get('nombre')
    intro = data.get('intro')
    peculiaridad = data.get('peculiaridad')
    bondad = int(data.get('bondad', 500))
    hostilidad = int(data.get('hostilidad', 500))
    logica = int(data.get('logica', 500))
    ambicion = int(data.get('ambicion', 500))
    miedo = int(data.get('miedo', 500))
    posesividad = int(data.get('posesividad', 500))
    
    # --- CORRECCIÓN AQUÍ ---
    imagen_base64 = data.get('imagen', None)
    imagen_bytes = None
    if imagen_base64 and ',' in imagen_base64:
        try:
            imagen_bytes = base64.b64decode(imagen_base64.split(',')[1])
        except Exception as e:
            print(f"Error decodificando imagen: {e}")
            # Si falla, usamos una imagen por defecto o None
            imagen_bytes = None
    
    # Si no hay imagen, usamos una imagen por defecto (opcional)
    if imagen_bytes is None:
        # Puedes crear una imagen por defecto o simplemente guardar sin imagen
        pass
    
    resultado = crear_personaje(
        nombre, imagen_bytes, intro, peculiaridad,
        bondad, hostilidad, logica, ambicion, miedo, posesividad
    )
    
    return jsonify(resultado)
# ============================================================
# RUTA DE CHAT (ÚNICA, CORRECTA)
# ============================================================

@app.route('/api/chat/<nombre_personaje>', methods=['POST'])
def chat_con_personaje(nombre_personaje):
    data = request.json
    mensaje_usuario = data.get('mensaje')
    usuario = data.get('usuario', 'anonimo')
    api_key = data.get('api_key', '')
    
    if not mensaje_usuario:
        return jsonify({'status': 'error', 'message': 'Mensaje vacío'}), 400
    
    try:
        personaje = cargar_personaje(nombre_personaje)
        
        inicializar_personaje(
            nombre=personaje['name'],
            peculiaridad=personaje['peculiarity'],
            bondad=personaje['initial_Bondad'],
            hostilidad=personaje['initial_Hostilidad'],
            logica=personaje['initial_Logica'],
            api_key=api_key
        )
        
        resultado = procesar_mensaje(mensaje_usuario)
        
        return jsonify({
            'status': 'success',
            'respuesta': resultado['response']
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================================
# RUTA PRINCIPAL
# ============================================================

@app.route('/')
def index():
    return jsonify({
        'status': 'online',
        'nombre': 'Bella Server',
        'version': '1.0.0',
        'personajes': 'disponibles en /api/personajes'
    })

if __name__ == '__main__':
    Path("server-data/personajes").mkdir(parents=True, exist_ok=True)
    Path("server-data/usuarios").mkdir(parents=True, exist_ok=True)
    Path("server-data/config.json").touch()
    
    print("🚀 Bella Server iniciado en http://0.0.0.0:8080")
    print("📁 Personajes: server-data/personajes/")
    print("👤 Usuarios: server-data/usuarios/")
    print("💬 Chat: /api/chat/<nombre_personaje>")
    print("📋 Lista de personajes: /api/personajes")
    
    app.run(host='0.0.0.0', port=8080, debug=False)
