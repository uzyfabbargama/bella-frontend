# 🌙 Bella - Tu Espejo Emocional Interactivo

Bella es una **aplicación web full-stack** que permite crear y interactuar con personajes de IA con personalidades únicas y dinámicas. Cada personaje tiene sus propias características emocionales y psicológicas que evolucionan a través de la conversación.

---

## 🎯 Propósito de la Aplicación

Bella es un **sistema de roleplay interactivo** donde:
- **Creas personajes personalizados** con rasgos psicológicos (bondad, hostilidad, lógica, ambición, miedo, posesividad)
- **Chats en tiempo real** con IA que responde como el personaje
- **Evolución emocional** - cada interacción afecta el estado mental del personaje
- **Autenticación segura** para guardar tus personajes y progreso

### Casos de uso:
- 📖 Escritura creativa y desarrollo de personajes
- 🎮 Juegos de rol interactivos
- 🧠 Exploración de dinámicas psicológicas
- 💬 Companion apps con personalidad

---

## 🏗️ Arquitectura

### Stack Tecnológico
```
Frontend: HTML5 + CSS3 + JavaScript (Vanilla)
Backend:  Python Flask + CORS
Base de datos: JSON (server-data/)
Autenticación: XOR Hash + Session Tokens
```

### Flujo General
```
[Cliente] --HTTP--> [Flask Server] ---> [Bella Core Engine]
                           ↓
                     [File Storage]
                   (personajes, usuarios)
```

---

## 🔐 Sistema de Seguridad (Hasheada)

### 1. **Almacenamiento de Contraseñas**
```python
# En xor_auth.py (backend)
- Las contraseñas se hashean con XOR + salt
- NO se guardan en texto plano
- Sistema: xorid(password) → hash seguro
```

### 2. **Tokens de Sesión**
```python
# Al hacer login:
1. Usuario envía username + password
2. Backend verifica el hash
3. Si es correcto, genera JWT Token
4. Token se envía al cliente
5. Cliente incluye token en todas las requests autenticadas
```

### 3. **Flujo de Autenticación**
```
REGISTER:
  username + password → guardar_usuario() → hash + almacenar

LOGIN:
  username + password → login_user() → verificar hash → generar token
  
CHAT/PERSONAJES:
  token en headers → verificación de sesión → acceso permitido
```

---

## 📱 Frontend

### Tecnología
- **HTML5**: Estructura semántica
- **CSS3**: Diseño responsivo con gradientes y animaciones
- **JavaScript Vanilla**: Sin dependencias externas

### Componentes Principales

#### 1. **Sección de Autenticación**
```javascript
// Ubicación: #auth
- Input: username
- Input: password
- Botones: Registrar | Iniciar Sesión
```

#### 2. **Galería de Personajes**
```javascript
// Ubicación: #personajes
- Lista dinámica de personajes disponibles
- Botón para crear nuevo personaje
- Cargar desde: GET /api/personajes
```

#### 3. **Chat Interactivo**
```javascript
// Ubicación: #chat-container
- Área de mensajes (scrollable)
- Input de texto
- Envío con Enter o botón
- Requiere: token + nombre de personaje
```

#### 4. **Creador de Personajes**
```javascript
// Ubicación: #creador
Campos:
  - Nombre del personaje
  - Introducción (textarea)
  - Peculiaridad (textarea)
  - Imagen (file upload → base64)
  
Atributos (0-1000):
  - Bondad
  - Hostilidad
  - Lógica
  - Ambición
  - Miedo
  - Posesividad

Plantillas rápidas:
  - Héroe, Villano, Sabio, Amigo, Loco
```

### Funciones Principales

```javascript
// Navegación
mostrarSeccion(id)           // Cambiar entre vistas
volverAHome()                // Volver a auth
volverAPersonajes()          // Volver a galería

// Autenticación
registrar()                  // POST /api/register
login()                      // POST /api/login → obtener token

// Personajes
cargarPersonajes()           // GET /api/personajes
crearPersonaje()             // POST /api/personajes/crear + imagen base64

// Chat
iniciarChat(nombre)          // Preparar chat con personaje
enviarMensaje()              // POST /api/chat/<nombre>

// Utilidades
actualizarDesdeSlider(id)    // Sincronizar slider ↔ input numérico
aplicarPlantilla()           // Aplicar presets de personalidad
```

---

## 🖥️ Backend (servidor Flask)

### Ubicación
```
/backend/server_bhl.py
```

### Estructura de Carpetas
```
server-data/
├── personajes/
│   ├── personaje_1/
│   │   ├── nucleo.json         (nombre, icon, intro, datetime)
│   │   ├── imagen.png          (foto del personaje)
│   │   └── memoria.json        (historial de conversaciones)
│   └── personaje_2/
└── usuarios/
    ├── usuario_1.json          (username, password hash, metadata)
    └── usuario_2.json
```

### Rutas API

#### 🔑 Autenticación

**POST** `/api/register`
```json
Request:  {"username": "string", "password": "string"}
Response: {"status": "success", "message": "Usuario creado"}
Error:    {"status": "error", "message": "..."}
```

**POST** `/api/login`
```json
Request:  {"username": "string", "password": "string"}
Response: {
  "status": "success",
  "token": "jwt_token_aquí",
  "username": "user123"
}
Error:    {"status": "error", "message": "Credenciales inválidas"}
```

---

#### 👥 Personajes

**GET** `/api/personajes`
```json
Response: {
  "personajes": [
    {
      "nombre": "Bella",
      "icon": "🌙",
      "intro": "Soy Bella...",
      "fecha": "2026-09-29"
    }
  ]
}
```

**GET** `/api/personajes/<nombre>`
```json
Response: {
  "status": "success",
  "personaje": {
    "nombre": "string",
    "intro": "string",
    "peculiarity": "string",
    "bondad": 700,
    "hostilidad": 200,
    "logica": 600
  }
}
```

**POST** `/api/personajes/crear`
```json
Request: {
  "nombre": "string",
  "intro": "string",
  "peculiaridad": "string",
  "bondad": 500,
  "hostilidad": 500,
  "logica": 500,
  "ambicion": 500,
  "miedo": 500,
  "posesividad": 500,
  "imagen": "data:image/png;base64,..."  // Opcional
}
Response: {"status": "success", "message": "Personaje creado"}
```

---

#### 💬 Chat

**POST** `/api/chat/<nombre_personaje>`
```json
Request: {
  "mensaje": "¿Cómo estás?",
  "usuario": "user123",
  "api_key": "opcional"  // Para procesamiento avanzado
}
Response: {
  "status": "success",
  "respuesta": "Respuesta del personaje aquí..."
}
Error: {"status": "error", "message": "..."}
```

---

### Funciones Clave del Backend

#### 1. **Gestión de Usuarios** (`xor_auth.py`)
```python
guardar_usuario(username, password)    # Hash + guardar
login_user(username, password)         # Verificar + generar token
xorid(password)                        # Crear hash XOR
```

#### 2. **Gestión de Personajes** (`loader.py` / `creator.py`)
```python
cargar_personaje(nombre)               # Leer nucleo.json + imagen
crear_personaje(...)                   # Crear estructura de carpeta + archivos
```

#### 3. **Motor de Conversación** (`bhl_opt.py` / `bella_subconsciente.py`)
```python
inicializar_personaje(nombre, peculiaridad, rasgos, api_key)
procesar_mensaje(mensaje_usuario)      # Generar respuesta con IA
```

---

## 🔄 Flujo Completo: Cómo Funciona Todo Junto

### 1️⃣ Registro
```
[Cliente] Completa registro
   ↓
POST /api/register {username, password}
   ↓
[Backend] xor_auth.py → guardar_usuario()
   ↓
Hash password + crear archivo usuario
   ↓
Respuesta: {"status": "success"}
```

### 2️⃣ Login
```
[Cliente] Completa login
   ↓
POST /api/login {username, password}
   ↓
[Backend] Verificar hash XOR
   ↓
Si es correcto → generar JWT token
   ↓
Respuesta: {"status": "success", "token": "..."}
   ↓
[Cliente] Guarda token en variable global
```

### 3️⃣ Ver Personajes
```
[Cliente] Click en "Personajes"
   ↓
GET /api/personajes
   ↓
[Backend] Leer folder server-data/personajes/
   ↓
Para cada carpeta → leer nucleo.json
   ↓
Respuesta: lista de personajes
   ↓
[Cliente] Renderizar botones dinámicamente
```

### 4️⃣ Crear Personaje
```
[Cliente] Completa formulario + sube imagen
   ↓
POST /api/personajes/crear {
  nombre, intro, peculiaridad, 
  bondad, hostilidad, logica, ambicion, miedo, posesividad,
  imagen: base64
}
   ↓
[Backend] creator.py → crear_personaje()
   ↓
Crear carpeta: server-data/personajes/[nombre]/
Guardar:
  - nucleo.json (metadata)
  - imagen.png (desde base64)
  - memoria.json (conversaciones vacías)
   ↓
Respuesta: {"status": "success"}
```

### 5️⃣ Chat con Personaje
```
[Cliente] Escribe mensaje
   ↓
POST /api/chat/[nombre_personaje] {
  mensaje: "...",
  usuario: "user123"
}
   ↓
[Backend] bhl_opt.py
   ↓
1. Cargar personaje (cargar_personaje)
2. Inicializar contexto (inicializar_personaje)
3. Procesar input (procesar_mensaje)
4. IA genera respuesta basada en personalidad
5. Guardar en memoria.json
   ↓
Respuesta: {"status": "success", "respuesta": "..."}
   ↓
[Cliente] Mostrar en chat
```

---

## ⚙️ Configuración y Setup

### Backend
```bash
# 1. Instalar dependencias
pip install flask flask-cors

# 2. Crear estructura de carpetas
mkdir -p server-data/personajes
mkdir -p server-data/usuarios

# 3. Ejecutar servidor
python backend/server_bhl.py

# Servidor escuchará en http://0.0.0.0:8080
```

### Frontend
```bash
# El frontend no necesita build
# Solo abre index.html en un navegador

# Importante: Cambiar la URL del API en script.js
// Línea 2:
const API_URL = 'https://tu-servidor.com';  // Cambiar esto
```

---

## 🔧 Variables Importantes

### Frontend (`script.js`)
```javascript
API_URL                // URL del servidor backend
token                  // JWT del usuario actual
usuarioActual          // Username del usuario logueado
personajeActual        // Nombre del personaje seleccionado
```

### Backend (`server_bhl.py`)
```python
app.config['CORS_ORIGINS'] = '*'  // Permite conexiones de cualquier origen
Path("server-data/personajes")    // Donde se guardan personajes
Path("server-data/usuarios")      // Donde se guardan usuarios
```

---

## 📊 Estructura de Datos

### Usuario (JSON)
```json
{
  "username": "user123",
  "password_hash": "xor_encrypted_hash",
  "created_at": "2026-09-29T12:00:00Z",
  "personajes_creados": ["Bella", "Villano"]
}
```

### Personaje (nucleo.json)
```json
{
  "nucleo": {
    "name": "Bella",
    "icon": "🌙",
    "intro": "Soy Bella, tu espejo emocional...",
    "peculiarity": "Cambia según tus emociones",
    "initial_Bondad": 700,
    "initial_Hostilidad": 200,
    "initial_Logica": 600,
    "initial_Ambicion": 500,
    "initial_Miedo": 300,
    "initial_Posesividad": 400,
    "datetime": "2026-09-29T21:46:23Z"
  }
}
```

### Memoria de Chat
```json
{
  "conversaciones": [
    {
      "usuario": "user123",
      "timestamp": "2026-09-29T12:00:00Z",
      "entrada": "¿Cómo estás?",
      "salida": "Estoy bien, gracias",
      "estado_emocional": {"bondad": 695, "hostilidad": 205}
    }
  ]
}
```

---

## 🐛 Bugs y TODOs

### Problemas Conocidos
- ❌ Línea 157 en `script.js`: typo `sync` en lugar de `async`
- ⚠️ Imagen base64 requiere manejo de CORS en algunos navegadores
- ⚠️ El backend tiene código duplicado en `/chat` endpoint

### Mejoras Futuras
- [ ] Sistema de persistencia de memoria más robusto
- [ ] WebSockets para chat en tiempo real
- [ ] Dashboard de estadísticas del personaje
- [ ] Exportar/importar personajes
- [ ] Multi-idioma
- [ ] Rate limiting de API

---

## 📝 Licencia
No especificada (considera añadir LICENSE)

## 👤 Autor
**uzyfabbargama**

---

## 🎓 Aprende Más
- **Autenticación**: Ver `backend/xor_auth.py`
- **Creación de personajes**: Ver `backend/creator.py`
- **Motor IA**: Ver `backend/bella_subconsciente.py` y `backend/bhl_opt.py`
- **Frontend**: Ver `script.js` y `index.html`
