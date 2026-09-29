import ctypes
import os

class XIP:
    def __init__(self, buffer_size_mb=1):
        # Carga de la librería optimizada
        path = os.path.join(os.path.dirname(__file__), 'libxip.so')
        self.lib = ctypes.CDLL(path)
        
        # Mente: 1MB / 8 = 131072 slots de 64 bits [cite: 18, 27]
        self._size = (buffer_size_mb * 1024 * 1024) // 8
        self.mente = (ctypes.c_longlong * self._size)()
        
        # Máscara mágica de 17 bits (0x1FFFF) coincidente con el ASM 
        self.MASK = 0x1FFFF

    def generar_id(self, nombre):
        """Replicación exacta del algoritmo XORID del motor[cite: 21, 26]."""
        r14 = 0
        for char in nombre:
            r11 = r14
            r11 ^= ord(char)
            r11 <<= 1
            r14 = r11 & self.MASK
        return r14

    def inyectar(self, data_string):
        """
        Envía el string al motor NASM x64.
        Ahora soporta: 'clave:: [otra_clave],,'
        """
        if isinstance(data_string, str):
            data_string = data_string.encode('utf-8')
        
        # El motor procesa y dereferencia en r12 antes de save_id
        self.lib._xip_parse(ctypes.c_char_p(data_string), self.mente)

    def referenciar(self, clave_destino, clave_origen):
        """
        Crea un vínculo manual: clave_destino toma el valor actual de clave_origen.
        Equivalente a 'clave_destino:: [clave_origen],,' en el string.
        """
        id_dest = self.generar_id(clave_destino)
        id_orig = self.generar_id(clave_origen)
        self.mente[id_dest] = self.mente[id_orig]

    def __getitem__(self, key):
        idx = self.generar_id(key) if isinstance(key, str) else key
        return self.mente[idx & self.MASK]

    def __setitem__(self, key, value):
        """Inyección directa de valores numéricos a la mente."""
        idx = self.generar_id(key) if isinstance(key, str) else key
        self.mente[idx & self.MASK] = value

    def snapshot(self, filename="bella.xip"):
        with open(filename, "wb") as f:
            f.write(self.mente)

    def load(self, filename="bella.xip"):
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                f.readinto(self.mente)
            return True
        return False
