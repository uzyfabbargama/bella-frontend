// script.js
const API_URL = 'https://compromise-bare-comparisons-room.trycloudflare.com'; // <--- CAMBIA ESTO
let token = null;
let usuarioActual = null;
let personajeActual = null;

// --- FUNCIONES DE NAVEGACIÓN ---
function mostrarSeccion(id) {
    document.querySelectorAll('.seccion').forEach(el => el.style.display = 'none');
    document.getElementById(id).style.display = 'block';
}

function volverAHome() {
    mostrarSeccion('auth');
}

function volverAPersonajes() {
    mostrarSeccion('personajes');
    cargarPersonajes();
}

// --- AUTENTICACIÓN ---
async function registrar() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    if (!username || !password) return alert('Completa todos los campos');
    try {
        const resp = await fetch(`${API_URL}/api/register`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });
        const data = await resp.json();
        alert(data.message || data.status);
    } catch (e) { alert('Error: ' + e.message); }
}

async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    if (!username || !password) return alert('Completa todos los campos');
    try {
        const resp = await fetch(`${API_URL}/api/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });
        const data = await resp.json();
        if (data.status === 'success') {
            token = data.token;
            usuarioActual = username;
            mostrarSeccion('personajes');
            cargarPersonajes();
        } else {
            alert('Error: ' + data.message);
        }
    } catch (e) { alert('Error: ' + e.message); }
}

// --- PERSONAJES ---
async function cargarPersonajes() {
    try {
        const resp = await fetch(`${API_URL}/api/personajes`);
        const data = await resp.json();
        const lista = document.getElementById('lista-personajes');
        lista.innerHTML = '';
        data.personajes.forEach(p => {
            const btn = document.createElement('button');
            btn.textContent = p.nombre;
            btn.onclick = () => iniciarChat(p.nombre);
            lista.appendChild(btn);
        });
    } catch (e) { alert('Error cargando personajes: ' + e.message); }
}
function actualizarDesdeSlider(id) {
    const slider = document.getElementById(id);
    const num = document.getElementById(id + '-num');
    const valor = document.getElementById(id + '-valor');
    num.value = slider.value;
    valor.textContent = slider.value;
}

function actualizarDesdeNumero(id) {
    const num = document.getElementById(id + '-num');
    const slider = document.getElementById(id);
    const valor = document.getElementById(id + '-valor');
    let val = parseInt(num.value);
    if (isNaN(val)) val = 0;
    if (val < 0) val = 0;
    if (val > 1000) val = 1000;
    slider.value = val;
    valor.textContent = val;
}

function aplicarPlantilla() {
    const plantilla = document.getElementById('plantilla').value;
    const valores = {
        heroe: { bondad: 700, hostilidad: 200, logica: 600, ambicion: 500, miedo: 300, posesividad: 400 },
        villano: { bondad: 200, hostilidad: 800, logica: 300, ambicion: 700, miedo: 600, posesividad: 800 },
        sabio: { bondad: 500, hostilidad: 300, logica: 800, ambicion: 400, miedo: 300, posesividad: 200 },
        amigo: { bondad: 800, hostilidad: 100, logica: 400, ambicion: 300, miedo: 200, posesividad: 300 },
        loco: { bondad: 300, hostilidad: 600, logica: 100, ambicion: 400, miedo: 700, posesividad: 500 }
    };
    
    if (plantilla === 'personalizado') return;
    
    const v = valores[plantilla];
    if (!v) return;
    
    // Aplicar valores a cada slider y número
    ['bondad', 'hostilidad', 'logica', 'ambicion', 'miedo', 'posesividad'].forEach(key => {
        const slider = document.getElementById(key);
        const num = document.getElementById(key + '-num');
        const valor = document.getElementById(key + '-valor');
        slider.value = v[key];
        num.value = v[key];
        valor.textContent = v[key];
    });
}
function iniciarChat(nombre) {
    personajeActual = nombre;
    document.getElementById('chat').innerHTML = '';
    mostrarSeccion('chat-container');
}

// --- CHAT ---
async function enviarMensaje() {
    const msg = document.getElementById('msg').value;
    if (!msg) return;
    const chat = document.getElementById('chat');
    chat.innerHTML += `<div class="user">Tú: ${msg}</div>`;
    document.getElementById('msg').value = '';
    try {
        const resp = await fetch(`${API_URL}/api/chat/${personajeActual}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({mensaje: msg, usuario: usuarioActual})
        });
        const data = await resp.json();
        if (data.status === 'success') {
            chat.innerHTML += `<div class="bella">${personajeActual}: ${data.respuesta}</div>`;
        } else {
            chat.innerHTML += `<div class="bella">Error: ${data.message}</div>`;
        }
        chat.scrollTop = chat.scrollHeight;
    } catch (e) {
        chat.innerHTML += `<div class="bella">Error: ${e.message}</div>`;
    }
}

// --- CREAR PERSONAJE ---
function actualizarValor(id) {
    const valor = document.getElementById(id).value;
    document.getElementById(id + '-valor').textContent = valor;
}

sync function crearPersonaje() {
    const nombre = document.getElementById('nombre-personaje').value.trim();
    const intro = document.getElementById('intro-personaje').value.trim();
    const peculiaridad = document.getElementById('peculiaridad-personaje').value.trim();
    const bondad = document.getElementById('bondad').value;
    const hostilidad = document.getElementById('hostilidad').value;
    const logica = document.getElementById('logica').value;
    const ambicion = document.getElementById('ambicion').value;
    const miedo = document.getElementById('miedo').value;
    const posesividad = document.getElementById('posesividad').value;
    const fileInput = document.getElementById('imagen-personaje');
    let imagenBase64 = '';
    
    if (fileInput.files && fileInput.files[0]) {
        const file = fileInput.files[0];
        const reader = new FileReader();
        imagenBase64 = await new Promise((resolve) => {
            reader.onload = (e) => resolve(e.target.result);
            reader.readAsDataURL(file);
        });
    }
    
    if (!nombre || !intro || !peculiaridad) {
        return alert('Nombre, introducción y peculiaridad son obligatorios');
    }

    // --- SOLO UN PAYLOAD ---
    const payload = {
        nombre, intro, peculiaridad,
        bondad, hostilidad, logica,
        ambicion, miedo, posesividad,
        imagen: imagenBase64
    };

    try {
        const resp = await fetch(`${API_URL}/api/personajes/crear`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await resp.json();
        if (data.status === 'success') {
            alert('✅ Personaje creado correctamente');
            volverAPersonajes();
        } else {
            alert('Error: ' + data.message);
        }
    } catch (e) {
        alert('Error: ' + e.message);
    }
}
