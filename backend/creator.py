# creator.py
import json
import os
from pathlib import Path
from datetime import datetime

def crear_personaje(nombre, imagen_bytes, intro, peculiaridad, bondad, hostilidad, logica, ambicion=500, miedo=500, posesividad=500):
    """Crea un nuevo personaje con todos los parámetros (incluyendo AMP)."""
    
    # 1. Crear la carpeta del personaje
    ruta_personaje = Path(f"server-data/personajes/{nombre}")
    ruta_personaje.mkdir(parents=True, exist_ok=True)
    
    # 2. Guardar la imagen (si existe)
    if imagen_bytes:
        with open(ruta_personaje / "icon.png", 'wb') as f:
            f.write(imagen_bytes)
    
    # 3. Guardar la introducción
    with open(ruta_personaje / "intro.txt", 'w', encoding='utf-8') as f:
        f.write(intro)
    
    # 4. Guardar la peculiaridad
    with open(ruta_personaje / "peculiarity.txt", 'w', encoding='utf-8') as f:
        f.write(peculiaridad)
    
    # 5. Crear nucleo.json con TODOS los valores (BHL + AMP)
    nucleo = {
        "nucleo": {
            "icon": "icon.png" if imagen_bytes else "",
            "name": nombre,
            "intro": "intro.txt",
            "peculiarity": "peculiarity.txt",
            "initial_Bondad": bondad,
            "initial_Hostilidad": hostilidad,
            "initial_Logica": logica,
            "initial_Ambicion": ambicion,        # <--- NUEVO
            "initial_Miedo": miedo,              # <--- NUEVO
            "initial_Posesividad": posesividad,  # <--- NUEVO
            "datetime": datetime.now().isoformat()
        }
    }
    
    with open(ruta_personaje / "nucleo.json", 'w', encoding='utf-8') as f:
        json.dump(nucleo, f, indent=4, ensure_ascii=False)
    
    # 6. Crear la carpeta USERS
    (ruta_personaje / "USERS").mkdir(exist_ok=True)
    
    return {"status": "success", "nombre": nombre, "message": f"Personaje {nombre} creado correctamente"}
