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
    contenido = f"{K_USER}{K_SEP}{user_id}{K_FIN}\n"
    contenido += f"{K_PASS}{K_SEP}{pass_id}{K_FIN}\n"
    contenido += f"{saldo_trit}{K_SEP}{K_SALDO}{K_FIN}\n"
    contenido += f"{K_INVERT}{K_SEP}{invert+trampa1+trampa2}{K_FIN}\n"
    contenido += f"{trampa1}{K_SEP}{trampa2}{K_FIN}\n"  # Trampa
    
    # 5. Guardar
    ruta = Path(f"server-data/usuarios/{username}.xs")
    # Verificar si el usuario ya existe
    if ruta.exists():
        return False, "El usuario ya existe"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, 'w') as f:
        f.write(contenido)
    return True

def cargar_usuario(username, password):
    ruta = Path(f"server-data/usuarios/{username}.xs")
    if not ruta.exists():
        return None, "Usuario no encontrado"
    
    with open(ruta, 'r') as f:
        lineas = f.readlines()
    
    datos = {}
    # Convertir constantes a string para comparación
    sep_str = str(K_SEP)
    fin_str = str(K_FIN)
    
    for linea in lineas:
        if sep_str in linea and fin_str in linea:  # <--- CORREGIDO
            partes = linea.split(sep_str)  # <--- CORREGIDO
            clave = int(partes[0])
            valor = int(partes[1].replace(fin_str, ''))  # <--- CORREGIDO
            datos[clave] = valor
    
    # Verificar usuario
    user_id_guardado = datos.get(K_USER, 0) - K_USER
    pass_id_guardado = datos.get(K_PASS, 0) - K_PASS
    
    user_id_ingresado = xorid(username)
    pass_id_ingresado = xorid(password)
    
    if user_id_guardado != user_id_ingresado:
        return None, "Credenciales inválidas: Usuario Inválido"
    if pass_id_guardado != pass_id_ingresado:
        return None, "Credenciales inválidas: Contraseña Inválida"
    
    return {
        'username': username,
        'saldo': (~datos.get(K_SALDO, 0)) & 0xFFFFFFFF,
        'invert': datos.get(K_INVERT, 0)
    }, "OK"

def login_user(username, password):
    ruta = Path(f"server-data/usuarios/{username}.xs")
    if not ruta.exists():
        return {'status': 'error', 'message': 'Usuario no encontrado'}
    
    with open(ruta, 'r') as f:
        contenido = f.read()
    
    # --- BÚSQUEDA O(1) ---
    # Buscar la línea que empieza con K_USER (15386)
    user_trit_str = str(K_USER)
    pass_trit_str = str(K_PASS)
    
    user_line = None
    pass_line = None
    
    for linea in contenido.splitlines():
        if linea.startswith(user_trit_str + str(K_SEP)):
            user_line = linea
        elif linea.startswith(pass_trit_str + str(K_SEP)):
            pass_line = linea
        if user_line and pass_line:
            break
    
    if not user_line or not pass_line:
        return {'status': 'error', 'message': 'Archivo corrupto'}
    
    # Extraer los valores
    user_id_guardado = int(user_line.split(str(K_SEP))[1].replace(str(K_FIN), ''))
    pass_id_guardado = int(pass_line.split(str(K_SEP))[1].replace(str(K_FIN), ''))
    
    # Calcular XORIDs ingresados
    user_id_ingresado = xorid(username)
    pass_id_ingresado = xorid(password)
    
    # Comparar
    if user_id_guardado != user_id_ingresado:
        return {'status': 'error', 'message': 'Credenciales inválidas'}
    if pass_id_guardado != pass_id_ingresado:
        return {'status': 'error', 'message': 'Credenciales inválidas'}
    
    return {
        'status': 'success',
        'token': xorid(f"{username}:{password}:{os.urandom(4).hex()}"),
        'user': {'username': username}
    }

#me encanta, es....increíble ¿te gusta?
