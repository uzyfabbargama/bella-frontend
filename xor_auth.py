# xor_auth.py
def xorid(texto):
    id_acumulado = 0
    for char in texto:
        id_acumulado = ((id_acumulado ^ ord(char)) << 1) & 0xFFFFFFFF
    return id_acumulado

def login_user(username, password):
    # 1. Calcular IDs
    user_id = xorid(username)
    pass_id = xorid(password)
    
    # 2. Buscar en archivo .xrp
    # 3. Verificar si existe
    # 4. Devolver token de sesión
    return token
