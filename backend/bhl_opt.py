# ============================================================================
# bhl_opt.py - Motor BHL + Bella + Numeraso
# ============================================================================

import math
import random
import requests
import os
import json
import time
from bella_subconsciente import BellaSubconsciente

# ============================================================================
# MODO SERVIDOR
# ============================================================================
MODO_SERVIDOR = os.getenv("BHL_MODO", "consola") == "servidor"

# ============================================================================
# CONSTANTES
# ============================================================================
base = 1000
Necesidad_Social = 0
PosC2 = (base**3) * 2**2
PosX = (base**2) * 2**2
PosC1 = (base**2) * 2
PosY = base * 2
PosC = base
PosZ = 1

chat_history = []
Nivel_incomodidad = 0
password = ""

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def inputs(message, cons=None):
    if cons is not None:
        print(f"{message} {cons}")
        return cons
    return input(message)

def cualitivation(porcentaje):
    if porcentaje <= 0.01:
        return "nada"
    elif porcentaje <= 1:
        return "infimo"
    elif porcentaje <= 11.0:
        return "bajo"
    elif porcentaje <= 35.0:
        return "notable"
    elif porcentaje <= 55.0:
        return "medio"
    elif porcentaje <= 76.0:
        return "alto"
    else:
        return "dominante"

def get_prompt_history_text():
    return "\n".join([f"Usuario: {msg['user']}\nIA: {msg['character']}\n" for msg in chat_history])

def get_last_n_history(n=3):
    if len(chat_history) <= n:
        return "\n".join([f"Usuario: {msg['user']}\nIA: {msg['character']}\n" for msg in chat_history])
    return "\n".join([f"Usuario: {msg['user']}\nIA: {msg['character']}\n" for msg in chat_history[-n:]])

# ============================================================================
# NUMERASO (Motor emocional)
# ============================================================================

def Numeraso_Exp(ExpB, ExpH, ExpL):
    NumerasoXP = (ExpB * PosX) + (ExpH * PosY) + (ExpL * PosZ) + PosC + PosC1 + PosC2
    C1 = (NumerasoXP // PosC) % 2
    C2 = (NumerasoXP // PosC1) % 2
    C3 = (NumerasoXP // PosC2) % 2
    caso = C1 + C2 + C3
    while caso != 3:
        D1 = 1 - C1
        D2 = 1 - C2
        D3 = 1 - C3
        NumerasoXP += D1 * PosC + D2 * PosC1 + D3 * PosC2
        NumerasoXP += D1 - (D1 * PosY) - (D2 * PosZ) - (D3 * PosX)
        C1 = (NumerasoXP // PosC) % 2
        C2 = (NumerasoXP // PosC1) % 2
        C3 = (NumerasoXP // PosC2) % 2
        caso = C1 + C2 + C3
    ExpB = (NumerasoXP // PosX) % base
    ExpH = (NumerasoXP // PosY) % base
    ExpL = (NumerasoXP // PosZ) % base
    return int(ExpB), int(ExpH), int(ExpL)

def Numeraso(a, b, c):
    return (a * PosX) + (b * PosY) + (c * PosZ) + PosC + PosC1 + PosC2

def Numeraso_update(expB, expH, expL, Numero_generado):
    C1 = (Numero_generado // PosC) % 2
    C2 = (Numero_generado // PosC1) % 2
    C3 = (Numero_generado // PosC2) % 2
    caso = C1 + C2 + C3
    tiempo = 0
    while caso != 3:
        D1 = 1 - C1
        D2 = 1 - C2
        D3 = 1 - C3
        expB += D1
        expH += D2
        expL += D3
        tiempo += D1 * 0.000238923 + D2 * 2.2781388 + D3 * 1.7238498
        Numero_generado += D1 * PosC + D2 * PosC1 + D3 * PosC2
        Numero_generado += D1 * expB
        Numero_generado -= (D1 * expB) * PosY
        Numero_generado -= D2 * expH * PosZ - D2 * expH * PosX
        Numero_generado -= (D3 * expL) * PosX - D3 * expL * PosY
        Numero_generado += D1 * (base // (expL + 1)) % base + D2 * (base // (expH + 1)) % base + D3 * (base // (expB + 1)) % base
        C1 = (Numero_generado // PosC) % 2
        C2 = (Numero_generado // PosC1) % 2
        C3 = (Numero_generado // PosC2) % 2
        caso = C1 + C2 + C3
        Numero_generado = int(Numero_generado % ((base ** 3) * 2 ** 3))
        expB = int(expB)
        expH = int(expH)
        expL = int(expL)
        tiempo = float(tiempo)
    return Numero_generado, expB, expH, expL, tiempo

def Numeraso2(a, b, c):
    return (a * PosX) + (b * PosY) + (c * PosZ) + PosC + PosC1 + PosC2

def Numeraso2_update(expS, expHu, expC, Numero_de_necesidad):
    C4 = (Numero_de_necesidad // PosC) % 2
    C5 = (Numero_de_necesidad // PosC1) % 2
    C6 = (Numero_de_necesidad // PosC2) % 2
    caso = C4 + C5 + C6
    expS, expHu, expC = Numeraso_Exp(expS, expHu, expC)
    while caso != 3:
        D4 = 1 - C4
        D5 = 1 - C5
        D6 = 1 - C6
        expS += D4
        expHu += D5
        expC += D6
        Numero_de_necesidad += (D4 * PosZ) + (D4 * PosC) + (D5 * PosC1) + (D6 * PosC2)
        Numero_de_necesidad += D4 * expC * PosZ
        Numero_de_necesidad -= (D4 * expC) * PosY
        Numero_de_necesidad -= D5 * expHu * PosZ - D5 * expHu * PosX
        Numero_de_necesidad -= (D6 * expS) * PosX - D6 * expS * PosY
        C4 = (Numero_de_necesidad // PosC2) % 2
        C5 = (Numero_de_necesidad // PosC1) % 2
        C6 = (Numero_de_necesidad // PosC) % 2
        caso = C4 + C5 + C6
        Numero_de_necesidad += D4 * (base // (expS + 1)) % base + D5 * (base // (expHu + 1)) % base + D6 * (base // (expC + 1)) % base
        Numero_de_necesidad = int(Numero_de_necesidad % ((base ** 3) * 2 ** 3))
        expS = int(expS)
        expHu = int(expHu)
        expC = int(expC)
    return Numero_de_necesidad, expS, expHu, expC

# ============================================================================
# FUNCIONES PARA GEMINI (con reintentos)
# ============================================================================

def llamar_con_reintentos(url, headers, payload, max_intentos=3):
    for intento in range(max_intentos):
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                espera = 2 ** intento
                print(f"⚠️ Límite de API. Esperando {espera}s... (Intento {intento+1}/{max_intentos})")
                time.sleep(espera)
            else:
                raise e
        except Exception as e:
            print(f"Error inesperado: {e}")
            break
    return None

def build_unified_prompt(msg, peculiaridad, necesidad_social):
    return f"""Actúa como Analizador Emocional Avanzado y Generador de Personalidad.

### TAREA 1: Analiza emocionalmente esta frase del usuario: '{msg}'

ESCALA LOGARÍTMICA 0-1000 (no lineal):
- 0-300: FÁCIL | 301-500: MODERADO | 501-700: DIFÍCIL | 701-800: MUY DIFÍCIL | 801-900: EXTREMO | 901-1000: SOBREHUMANO

CATEGORÍAS (0-1000):
1. BONDAD: empatía, compasión, calidez
2. HOSTILIDAD: agresividad, sarcasmo, frialdad
3. LÓGICA: precisión, estructura, análisis
4. INCOMODIDAD: 0-1000 (cuánto te incomoda la interacción)
5. NECESIDAD SOCIAL: 0-1000 (anhelo de conexión, MÁS IMPORTANTE)

NECESIDADES BIOLÓGICAS (0-50 lineal):
- Ir al baño: 50=saciado, 0=urgente
- Hambre: 50=saciado, 0=famélico
- Sueño: 50=descansado, 0=agotado

### TAREA 2: Genera descripción del personaje
Bondad_actual: {{res_b}} | Hostilidad: {{res_h}} | Lógica: {{res_l}}
Necesidades: {{res_c}}, {{res_hu}}, {{res_s}}
Peculiaridad: {peculiaridad}
Necesidad Social: {necesidad_social}

DEVUELVE JSON EXACTO:
{{
    "ab": número,
    "ah": número,
    "al": número,
    "ac": número,
    "ahu": número,
    "As": número,
    "ai": número,
    "NS": número,
    "descripcion_personaje": "texto de 1-2 párrafos"
}}"""

# ============================================================================
# FUNCIONES PARA MODO SERVIDOR
# ============================================================================

def inicializar_personaje(nombre, peculiaridad, bondad, hostilidad, logica, api_key):
    """Inicializa un personaje desde la web."""
    global Peculiaridad, a, b, c, expB, expH, expL, expAmb, expMie, expPos
    global expC, expHu, expS, baño, hambre, sueño, Numero, Numero1, Numero2
    global tiempo, Necesidad_Social, password, bella
    
    Peculiaridad = peculiaridad
    a = bondad
    b = hostilidad
    c = logica
    password = api_key
    
    amb = 500
    mie = 500
    pos = 500
    
    expB, expL, expH = 0, 0, 0
    expC, expHu, expS = 0, 0, 0
    expAmb, expMie, expPos = 0, 0, 0
    baño = 50
    hambre = 50
    sueño = 50
    
    expB, expL, expH = Numeraso_Exp(expB, expH, expL)
    expS, expHu, expC = Numeraso_Exp(expS, expHu, expC)
    expAmb, expMie, expPos = Numeraso_Exp(expAmb, expMie, expPos)
    
    Numero = Numeraso(a, b, c)
    Numero1 = Numeraso2(baño, hambre, sueño)
    Numero2 = Numeraso(amb, mie, pos)
    
    Numero, expB, expH, expL, tiempo = Numeraso_update(expB, expH, expL, Numero)
    Numero1, expS, expHu, expC = Numeraso2_update(expS, expHu, expC, Numero1)
    Numero2, expAmb, expMie, expPos = Numeraso2_update(expAmb, expMie, expPos, Numero2)
    
    bella = BellaSubconsciente(archivo_xrp=f"{nombre}.xrp")
    
    print(f"✅ Personaje '{nombre}' inicializado en modo servidor.")
    return {"status": "ok", "nombre": nombre}

def procesar_mensaje(mensaje_usuario):
    """Procesa un mensaje desde la web y devuelve la respuesta."""
    global chat_history, Necesidad_Social, Numero, Numero1, Numero2, tiempo
    global expB, expH, expL, expS, expHu, expC, expAmb, expMie, expPos
    global bella, Peculiaridad, password
    
    # ================================================================
    # SECCIÓN 10: Calcular porcentajes
    # ================================================================
    tiempo %= 10
    Bondad_actual = max(1, (Numero // PosX) % base)
    Hostilidad_actual = max(1, (Numero // PosY) % base)
    Lógica_actual = max(1, (Numero // PosZ) % base)

    Cagar_actual = (max(1, Numero1 // PosX) % base) + ((max(1, tiempo) * 100) // 1) % 10
    Hambre_actual = max(1, Numero1 // PosY) % base + ((max(1, tiempo) * 1) // 1) % 10
    Sueño_actual = max(1, Numero1 // PosZ) % base + ((max(1, tiempo) * 10) // 1) % 10

    Ambición_actual = max(1, (Numero2 // PosX) % base)
    Miedo_actual = max(1, (Numero2 // PosY) % base)
    Posesión_actual = max(1, (Numero2 // PosZ) % base)

    cosiente = Bondad_actual + Hostilidad_actual + Lógica_actual
    cosiente_necesidad = Cagar_actual + Hambre_actual + Sueño_actual
    cosiente_psicológico = Ambición_actual + Miedo_actual + Posesión_actual

    porB = (Bondad_actual * 100) / (cosiente + 1)
    porH = (Hostilidad_actual * 100) / (cosiente + 1)
    porL = (Lógica_actual * 100) / (cosiente + 1)
    porC = (Cagar_actual * 100) / (cosiente_necesidad + 1)
    porHu = (Hambre_actual * 100) / (cosiente_necesidad + 1)
    porS = (Sueño_actual * 100) / (cosiente_necesidad + 1)

    res_b = cualitivation(porB)
    res_h = cualitivation(porH)
    res_l = cualitivation(porL)
    res_c = cualitivation(porC)
    res_hu = cualitivation(porHu)
    res_s = cualitivation(porS)

    # ================================================================
    # SECCIÓN 11: LLAMADA UNIFICADA
    # ================================================================
    unified_prompt = build_unified_prompt(mensaje_usuario, Peculiaridad, Necesidad_Social)
    unified_prompt = unified_prompt.replace("{res_b}", res_b)
    unified_prompt = unified_prompt.replace("{res_h}", res_h)
    unified_prompt = unified_prompt.replace("{res_l}", res_l)
    unified_prompt = unified_prompt.replace("{res_c}", res_c)
    unified_prompt = unified_prompt.replace("{res_hu}", res_hu)
    unified_prompt = unified_prompt.replace("{res_s}", res_s)

    api_key = os.getenv("GEMINI_API_KEY") or password
    url_unified = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}

    payload_unified = {
        "contents": [{"parts": [{"text": unified_prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.1
        }
    }

    try:
        time.sleep(0.5)
        response = llamar_con_reintentos(url_unified, headers, payload_unified)
        if response:
            unified_data = json.loads(response.json()['candidates'][0]['content']['parts'][0]['text'])
            ab = unified_data.get('ab', 0)
            ah = unified_data.get('ah', 0)
            al = unified_data.get('al', 0)
            ac = unified_data.get('ac', 0)
            ahu = unified_data.get('ahu', 0)
            As = unified_data.get('As', 0)
            ai = unified_data.get('ai', 0)
            NS = unified_data.get('NS', 0)
            Character = unified_data.get('descripcion_personaje', "Personaje sin descripción")
            Necesidad_Social = base - NS
        else:
            print("⚠️ No se pudo obtener respuesta de Gemini. Usando valores neutros.")
            ab, ah, al, ac, ahu, As, ai, NS = 0, 0, 0, 0, 0, 0, 0, 0
            Character = "Personaje neutro por límite de API"
            Necesidad_Social = 0
    except Exception as e:
        print(f"Error en llamada unificada: {e}")
        ab, ah, al, ac, ahu, As, ai, NS = 0, 0, 0, 0, 0, 0, 0, 0
        Character = "Personaje neutro por error"
        Necesidad_Social = 0

    # ================================================================
    # SECCIÓN 12: ACTUALIZACIÓN DEL NUMERASO
    # ================================================================
    Numero += ab * PosX + expB - Necesidad_Social
    Numero += ah * PosY + expH + Necesidad_Social
    Numero += al * PosZ + expL - Necesidad_Social

    Numero1 -= ac * PosX + expC
    Numero1 -= ahu * PosY + expHu
    Numero1 -= As * PosZ + expS

    Numero2 += ((ab * PosX * -1) + expAmb) + ((ab * PosZ) + expAmb)
    Numero2 += ((ah * PosY * -1) + expMie) + ((ah * PosX) + expMie)
    Numero2 += ((al * PosZ * -1) + expPos) + ((al * PosZ) + expPos)

    Necesidad_C = (Numero1 // PosX) % base
    Necesidad_H = (Numero1 // PosY) % base
    Necesidad_S = (Numero1 // PosZ) % base

    Numero -= (Necesidad_C * PosX) % base + (Necesidad_H * PosX) + (Necesidad_S * PosX)
    Numero += (Necesidad_C * PosY) % base + (Necesidad_H * PosY) + (Necesidad_S * PosY)
    Numero -= (Necesidad_C * PosZ) * 2 + (Necesidad_H * PosZ) * 2 + (Necesidad_S * 10) * 2

    AddexpHu, AddexpC, AddexpS = Numeraso_Exp(max(1, expHu), max(1, expC), max(1, expS))
    AddexpB, AddexpH, AddexpL = Numeraso_Exp(expH, expB, expL)

    expB += AddexpB
    expH += AddexpH
    expL += AddexpL
    expHu += AddexpHu
    expC += AddexpC
    expS += AddexpS

    Numero = Numeraso(Bondad_actual, Hostilidad_actual, Lógica_actual)
    Numero, expB, expH, expL, tiempo = Numeraso_update(expB, expH, expL, Numero)

    Numero1 = Numeraso2(Cagar_actual, Hambre_actual, Sueño_actual)
    Numero1, expS, expHu, expC = Numeraso2_update(expS, expHu, expC, Numero1)

    Numero2 = Numeraso(Ambición_actual, Miedo_actual, Posesión_actual)
    Numero2, expAmb, expMie, expPos = Numeraso2_update(expAmb, expMie, expPos, Numero1)

    # ================================================================
    # SECCIÓN 13: RESPUESTA FINAL
    # ================================================================
    susurro_bella = bella.susurrar(cantidad_palabras=7)

    prompt_respuesta = (
        f"Eres un personaje con esta personalidad:\n{Character}\n\n"
        f"--- VOCES INTERNAS ---\n{susurro_bella}\n\n"
        f"--- CONTEXTO RECIENTE ---\n{get_last_n_history(3)}\n\n"
        f"Usuario dice: '{mensaje_usuario}'\n\n"
        f"Responde como tu personaje (máximo 150 palabras, natural y coherente):"
    )

    url_response = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    data_response = {"contents": [{"parts": [{"text": prompt_respuesta}]}]}

    try:
        response = llamar_con_reintentos(url_response, headers, data_response)
        if response:
            respuesta_ia = response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            respuesta_ia = "Lo siento, estoy teniendo problemas para conectarme."

        bella.entrenar(mensaje_usuario + " " + respuesta_ia)
        chat_history.append({"user": mensaje_usuario, "character": respuesta_ia})
        if len(chat_history) > 5:
            chat_history = chat_history[-5:]

        return {"response": respuesta_ia}
    except Exception as e:
        print(f"Error en respuesta: {e}")
        return {"response": "Error procesando tu mensaje."}

# ============================================================================
# MODO CONSOLA
# ============================================================================

def main():
    if MODO_SERVIDOR:
        print("🤖 BHL en modo servidor. Usa inicializar_personaje() y procesar_mensaje()")
        return
    
    global Peculiaridad, a, b, c, expB, expH, expL, expAmb, expMie, expPos
    global expC, expHu, expS, baño, hambre, sueño, Numero, Numero1, Numero2
    global tiempo, Necesidad_Social, password, bella, chat_history
    
    Peculiaridad = inputs("Describe la peculiaridad de tu personaje: ")
    a = max(1, int(inputs("Define la bondad: "))) % base
    b = max(1, int(inputs("Define la hostilidad: "))) % base
    c = max(1, int(inputs("Define la Lógica: "))) % base
    amb = max(1, int(inputs("Define la ambición: "))) % base
    mie = max(1, int(inputs("Define el miedo a sí mismo: "))) % base
    pos = max(1, int(inputs("Define la posesividad: "))) % base
    password = inputs("Ingrese su clave API: ")
    
    expB, expL, expH = 0, 0, 0
    expC, expHu, expS = 0, 0, 0
    expAmb, expMie, expPos = 0, 0, 0
    baño = 50
    hambre = 50
    sueño = 50
    
    expB, expL, expH = Numeraso_Exp(expB, expH, expL)
    expS, expHu, expC = Numeraso_Exp(expS, expHu, expC)
    expAmb, expMie, expPos = Numeraso_Exp(expAmb, expMie, expPos)
    
    Numero = Numeraso(a, b, c)
    Numero1 = Numeraso2(baño, hambre, sueño)
    Numero2 = Numeraso(amb, mie, pos)
    
    Numero, expB, expH, expL, tiempo = Numeraso_update(expB, expH, expL, Numero)
    Numero1, expS, expHu, expC = Numeraso2_update(expS, expHu, expC, Numero1)
    Numero2, expAmb, expMie, expPos = Numeraso2_update(expAmb, expMie, expPos, Numero2)
    
    bella = BellaSubconsciente(archivo_xrp="bella.xrp")
    
    print(f"Númeraso: {Numero}")
    print(f"Numeraso1: {Numero1}")
    print(f"Numeraso2: {Numero2}")
    
    while True:
        Numero1 += PosX + PosY + PosZ
        message = inputs("Escriba un mensaje... ")
        
        if message == "exit":
            print("Saliendo...")
            bella.guardar()
            break
        
        resultado = procesar_mensaje(message)
        print(f"\nRespuesta: {resultado['response']}")
        print("-" * 50)

# ============================================================================
# EJECUCIÓN
# ============================================================================

if __name__ == "__main__":
    main()
