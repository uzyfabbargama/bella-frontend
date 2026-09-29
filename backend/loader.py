# loader.py
import json
import os
from pathlib import Path

def cargar_personaje(nombre_personaje):
    """Carga un personaje desde server-data/personajes/[nombre]/"""
    ruta_base = Path(f"server-data/personajes/{nombre_personaje}")
    
    # 1. Cargar nucleo.json
    with open(ruta_base / "nucleo.json", 'r') as f:
        nucleo = json.load(f)["nucleo"]
    
    # 2. Leer archivos de texto
    with open(ruta_base / nucleo["intro"], 'r') as f:
        intro = f.read()
    
    with open(ruta_base / nucleo["peculiarity"], 'r') as f:
        peculiarity = f.read()
    
    # 3. Devolver todo
    return {
        "name": nucleo["name"],
        "icon": nucleo["icon"],
        "intro": intro,
        "peculiarity": peculiarity,
        "initial_Bondad": nucleo["initial_Bondad"],
        "initial_Hostilidad": nucleo["initial_Hostilidad"],
        "initial_Logica": nucleo["initial_Logica"],
        "ruta": ruta_base
    }

# Prueba
personaje = cargar_personaje("character01")
print(f"Personaje: {personaje['name']}")
print(f"Intro: {personaje['intro']}")
print(f"Peculiaridad: {personaje['peculiarity']}")
print(f"Bondad: {personaje['initial_Bondad']}")
