# bella_subconsciente.py
# Versión reducida y adaptada para ser importada como clase

import os
import time
import struct
import array
from pathlib import Path
from xiplow import XIP

class BellaSubconsciente:
    def __init__(self, archivo_xrp="bella.xrp", buffer_mb=1):
        # 1. Configuración de arquitectura
        self.bits = 15
        self.base = 1 << self.bits
        self.mask = self.base - 1
        self.num_n = 131072
        self.MASK_NEURONAS = self.num_n - 1
        self.MAX_UINT32 = 0xFFFFFFFF
        
        # 2. Inicializar XIP (1 MB)
        self.cerebro = XIP(buffer_size_mb=buffer_mb)
        self.traductor = {}
        
        # 3. Inicializar la memoria plana (exps_flat)
        self.total_elements = self.num_n * (3 + 64)
        self.exps_flat = array.array('I', [0] * self.total_elements)
        
        # 4. Cargar archivo de conciencia si existe
        self.archivo_xrp = archivo_xrp
        if not self.cerebro.load(archivo_xrp):
            print("[Bella] Mente virgen. Inicializando...")
            # Inicializar valores base si es nuevo
            base_alu = (1 << 15) + (1 << 16) + (1 << 17) # PosC, PosC1, PosC2 simulados
            for i in range(self.num_n):
                self.cerebro.mente[i] = base_alu
        else:
            print(f"[Bella] Mente cargada desde {archivo_xrp}")
            # Cargar el traductor y slots desde el archivo .xrp
            self._cargar_xrp(archivo_xrp)

    def _cargar_xrp(self, filename):
        """Carga el archivo .xrp con las neuronas y slots."""
        if not os.path.exists(filename):
            return
        try:
            with open(filename, "rb") as f:
                while True:
                    header = f.read(19)
                    if not header: 
                        break
                    idx, sep, open_b, mem, close_b, pres = struct.unpack(">IBBqBI", header)
                    texto_raw = f.read(24)
                    self.traductor[idx] = texto_raw.split(b'\x00')[0].decode('utf-8', errors='ignore')
                    f.read(1) 
                    slots_raw = f.read(256)
                    slots_restaurados = struct.unpack(">64I", slots_raw)
                    
                    if idx < self.num_n:
                        self.cerebro.mente[idx] = mem 
                        base_idx = (idx << 6) + (idx << 1) + idx
                        self.exps_flat[base_idx] = pres
                        self.exps_flat[base_idx + 1] = pres
                        self.exps_flat[base_idx + 2] = max(pres, 15)
                        for j in range(64):
                            self.exps_flat[base_idx + 3 + j] = slots_restaurados[j]
            print(f"[Bella] {len(self.traductor)} neuronas reanimadas.")
        except Exception as e:
            print(f"[Bella] Error cargando .xrp: {e}")

    def _xorid(self, frag):
        """Algoritmo XORID para generar IDs."""
        id_acc = 0
        for car in frag:
            id_acc = (id_acc ^ ord(car)) << 1
        return (id_acc * 20) & self.MASK_NEURONAS

    def _numeraso2_update(self, ex0, ex1, ex2, valor_mente):
        """Simplificación del Numeraso para Bella."""
        # Simulación rápida para evitar dependencias de BHL
        # (Esencialmente, suma experiencia y evita overflow)
        ex0 = (ex0 + 1) % self.base
        ex1 = (ex1 + 1) % self.base
        ex2 = (ex2 + 1) % self.base
        # Regenerar el valor de mente basado en las experiencias
        nuevo_valor = (ex0 << 15) + (ex1 << 16) + (ex2 << 17) + (1 << 15) + (1 << 16) + (1 << 17)
        return nuevo_valor, ex0, ex1, ex2

    def _registrar_conexion(self, idx_origen, idx_destino, xorid_destino, es_futuro):
        """Registra una conexión en los slots."""
        inicio = 32 if es_futuro else 0
        fin = 64 if es_futuro else 32
        base_origen = (idx_origen << 6) + (idx_origen << 1) + idx_origen
        
        slot_encontrado = -1
        slot_vacio = -1
        
        for i in range(inicio, fin):
            idx_slot_real = base_origen + 3 + i
            slot_actual = self.exps_flat[idx_slot_real]
            id_vecino = (slot_actual >> 16) & 0xFFFF
            
            if id_vecino == (idx_destino & 0xFFFF):
                slot_encontrado = idx_slot_real
                break
            if slot_actual == 0 and slot_vacio == -1:
                slot_vacio = idx_slot_real

        target_slot_idx = slot_encontrado if slot_encontrado != -1 else slot_vacio
        
        if target_slot_idx != -1:
            slot_actual = self.exps_flat[target_slot_idx]
            fuerza_actual = slot_actual & 0xFFFF
            incremento = xorid_destino & 0xFFFF
            nueva_fuerza = min(0xFFFF, fuerza_actual + incremento)
            self.exps_flat[target_slot_idx] = ((idx_destino & 0xFFFF) << 16) | nueva_fuerza

    def entrenar(self, texto):
        """Entrena a Bella con el texto (mensaje + respuesta del LLM)."""
        # Limpiar y tokenizar
        texto_limpio = ''.join(c for c in texto if c.isprintable() or c in 'áéíóúñÑ ')
        palabras = texto_limpio.split()
        
        idx_anterior = None
        xorid_anterior = None
        
        for i, palabra in enumerate(palabras):
            if len(palabra) > 14:
                partes = [palabra[:14], palabra[14:]]
            else:
                partes = [palabra]
                
            for palabra_procesada in partes:
                if not palabra_procesada: 
                    continue
                    
                raw_xor = self._xorid(palabra_procesada)
                idx = raw_xor & self.MASK_NEURONAS
                self.traductor[idx] = palabra_procesada
                
                # Actualizar mente y experiencias
                fuerza = len(palabra_procesada) * 2 + (i % 10)
                self.cerebro.mente[idx] += fuerza << 15
                
                base_idx = (idx << 6) + (idx << 1) + idx
                
                ex0 = self.exps_flat[base_idx]
                ex1 = self.exps_flat[base_idx + 1]
                ex2 = self.exps_flat[base_idx + 2]
                
                n_gen, n_ex0, n_ex1, n_ex2 = self._numeraso2_update(ex0, ex1, ex2, self.cerebro.mente[idx])
                
                self.exps_flat[base_idx] = n_ex0
                self.exps_flat[base_idx + 1] = n_ex1
                self.exps_flat[base_idx + 2] = min(self.MAX_UINT32, int(n_ex2) + int(fuerza))
                
                if idx_anterior is not None and idx_anterior != idx:
                    self._registrar_conexion(idx, idx_anterior, xorid_anterior, es_futuro=False)
                    self._registrar_conexion(idx_anterior, idx, raw_xor, es_futuro=True)
                    
                idx_anterior = idx
                xorid_anterior = raw_xor

    def susurrar(self, cantidad_palabras=7):
        """
        Bella proyecta sus pensamientos (ruido de fondo).
        Ideal para inyectar en el prompt del LLM como contexto.
        """
        # Buscar neuronas activas
        candidatas = [i for i in range(self.num_n) if i in self.traductor and self.exps_flat[(i * 67) + 2] > 5]
        if not candidatas: 
            return "..."
        
        # Elegir la más activa como faro
        faro_idx = max(candidatas, key=lambda i: self.exps_flat[(i * 67) + 2])
        
        # Calcular resonancia
        def calcular_resonancia(idx):
            distancia_frecuencia = abs(idx - faro_idx)
            proximidad = 1.0 / (distancia_frecuencia + 1) 
            valor_alu = int(self.cerebro.mente[idx])
            return self.exps_flat[((idx << 6) + (idx << 1) + idx) + 2] * proximidad * (valor_alu & self.mask)

        # Seleccionar las mejores
        candidatas_ordenadas = sorted(candidatas, key=calcular_resonancia, reverse=True)[:cantidad_palabras]
        palabras_final = []
        for idx in candidatas_ordenadas:
            contenido = self.traductor.get(idx, "")
            if isinstance(contenido, str) and len(contenido) >= 1:
                palabras_final.append(contenido)
        
        return " ".join(palabras_final) if palabras_final else "..."

    def guardar(self, archivo=None):
        """Guarda el estado de Bella."""
        if archivo is None:
            archivo = self.archivo_xrp
        # Usar el método de guardado de Bellav3_11low3 (simplificado)
        try:
            with open(archivo, "wb") as f:
                for idx, texto in self.traductor.items():
                    texto_fijo = texto.encode('utf-8')[:24].ljust(24, b'\x00')
                    base_idx = (idx << 6) + (idx << 1) + idx
                    slots = self.exps_flat[base_idx + 3 : base_idx + 67]
                    paquete = struct.pack(">IBBqBI24sB64I", 
                        idx, 0x9C, 0xB6, int(self.cerebro.mente[idx]), 0xBA, 
                        self.exps_flat[base_idx + 2], texto_fijo, 0xE8, *slots)
                    f.write(paquete)
            print(f"[Bella] Guardado en {archivo}")
        except Exception as e:
            print(f"[Bella] Error guardando: {e}")
