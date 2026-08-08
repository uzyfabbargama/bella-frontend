# xor_auth.py (versión definitiva)
import os
import json
from pathlib import Path

# Constantes secretas (cada instalación puede tener las suyas)
K_USER = 15386
K_PASS = 102846
K_SALDO = 3678
K_INVERT = 6888
K_SEP = 156
K_FIN = 232

# Archivos trampa (parecen XORID, pero no lo son)
TRAMPAS = [3844, 548, 9999, 7777, 12345]

def xorid(texto):
    """Algoritmo XORID irreversible."""
    id_acumulado = 0
    for char in texto:
        id_acumulado = ((id_acumulado ^ ord(char)) << 1) & 0xFFFFFFFF
    return id_acumulado

def guardar_usuario(username, password, saldo=0, invert=0):
    """Guarda un usuario con ofuscación total."""
    # 1. Calcular IDs reales
    user_id = xorid(username)
    pass_id = xorid(password)
    
    # 2. Ofuscar con constantes
    user_trit = K_USER + user_id
    pass_trit = K_PASS + pass_id
    saldo_trit = (~saldo) & 0xFFFFFFFF
    
    # 3. Generar números trampa (aleatorios)
    trampa1 = TRAMPAS[0]
    trampa2 = TRAMPAS[1]
    
    # 4. Crear contenido (con trampas intercaladas)
    contenido = f"{user_trit}{K_SEP}{user_id}{K_FIN}\n"
    contenido += f"{pass_trit}{K_SEP}{pass_trit}{K_FIN}\n"
    contenido += f"{saldo_trit}{K_SEP}{K_SALDO}{K_FIN}\n"
    contenido += f"{K_INVERT}{K_SEP}{invert+trampa1+trampa2}{K_FIN}\n"
    contenido += f"{trampa1}{K_SEP}{trampa2}{K_FIN}\n"  # Trampa
    
    # 5. Guardar
    ruta = Path(f"USERS/{username}.xs")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, 'w') as f:
        f.write(contenido)
    return True

def cargar_usuario(username, password):
    """Carga un usuario verificando identidad."""
    ruta = Path(f"USERS/{username}.xs")
    if not ruta.exists():
        return None, "Usuario no encontrado"
    
    with open(ruta, 'r') as f:
        lineas = f.readlines()
    
    datos = {}
    for linea in lineas:
        if K_SEP in linea and K_FIN in linea:
            partes = linea.split(K_SEP)
            clave = int(partes[0])
            valor = int(partes[1].replace(str(K_FIN), ''))
            datos[clave] = valor
    
    # Verificar usuario (con constantes)
    user_id_guardado = datos.get(K_USER, 0) - K_USER
    pass_id_guardado = datos.get(K_PASS, 0) - K_PASS
    
    user_id_ingresado = xorid(username)
    pass_id_ingresado = xorid(password)
    
    if user_id_guardado != user_id_ingresado:
        return None, "Credenciales inválidas"
    if pass_id_guardado != pass_id_ingresado:
        return None, "Credenciales inválidas"
    
    return {
        'username': username,
        'saldo': (~datos.get(K_SALDO, 0)) & 0xFFFFFFFF,
        'invert': datos.get(K_INVERT, 0)
    }, "OK"

def login_user(username, password):
    """Función principal de login."""
    datos, mensaje = cargar_usuario(username, password)
    if datos:
        token = xorid(f"{username}:{password}:{os.urandom(4).hex()}")
        return {
            'status': 'success',
            'token': token,
            'user': datos
        }
    return {'status': 'error', 'message': mensaje}

me encanta, es....increíble ¿te gusta?
