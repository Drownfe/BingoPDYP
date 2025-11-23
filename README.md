# BingoPDYP 🎉  
Juego de Bingo Multijugador en Tiempo Real (Flask + Socket.IO)

## 🚀 Características principales
- Juego de bingo completamente funcional.
- Multijugador en tiempo real usando Flask-SocketIO.
- Vista Admin con control total:
  - Iniciar juego
  - Reiniciar juego
  - Ver número de jugadores conectados
  - Ver última balota anunciada
- Vista Jugador con:
  - Cartón generado aleatoriamente
  - Tablero general de balotas del 1 al 75
  - Marcación automática de números
  - Última balota visual y animada
- Tema visual oscuro premium.
- Compatible con dispositivos móviles.
- Reinicio completo con nuevos cartones.

## 📦 Estructura del proyecto

```
BingoPDYP/
│── app.py
│── requirements.txt
│── templates/
│   ├── layout.html
│   ├── index.html
│   └── admin.html
│── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── client.js
│       └── admin.js
│── README.md
```

## 🛠 Tecnologías utilizadas
- Python 3.10+
- Flask
- Flask-SocketIO
- HTML5
- CSS3
- JavaScript
- Socket.IO (cliente)
- Threading

## 🔧 Instalación y ejecución

### 1️⃣ Clonar el repositorio
```
git clone https://github.com/Drownfe/BingoPDYP
cd BingoPDYP
```

### 2️⃣ Crear entorno virtual (opcional pero recomendado)
```
python -m venv venv
venv/Scripts/activate   # Windows
```

### 3️⃣ Instalar dependencias
```
pip install -r requirements.txt
```

### 4️⃣ Ejecutar el servidor
```
python app.py
```

El servidor estará disponible en:

- **Admin:** http://localhost:5000/admin  
- **Jugador:** http://localhost:5000/

Desde celular en la misma red:

Usa la IP local que aparece en consola, por ejemplo:

```
http://192.168.1.10:5000/
```

(Asegúrate de permitir conexiones en el firewall.)

## 🕹 Cómo jugar

### 👤 Jugadores
1. Entras al link del jugador.
2. Recibes automáticamente:
   - Un ID nuevo (Jugador X)
   - Un cartón único
3. Cada refresh = nuevo ID + nuevo cartón.
4. Verás:
   - Tu cartón actualizado
   - Última balota
   - Marcación automática
   - Tablero general completo

### 🛠 Administrador
1. Entra a:
```
http://localhost:5000/admin
```
2. Desde ahí puedes:
   - Iniciar el juego
   - Reiniciar el juego
   - Ver cuántos jugadores hay conectados
   - Ver la última balota

### 🎯 Reglas oficiales del Bingo
Un jugador gana cuando:
- **Completa una fila**, o
- **Completa una columna**

Cuando alguien canta BINGO:
- El sistema detiene el sorteo
- Se anuncia el ganador a todos
- Finaliza la partida

## 🎨 Diseño visual
- Tema oscuro premium `#020617`.
- Colores vibrantes para balotas y marcaciones.
- Animaciones suaves y transiciones.
- Cartón y tablero general perfectamente alineados.
- Responsivo para celulares y tablets.

## 🔁 Reiniciar juego
Cuando el admin presiona *Reiniciar juego*:
- Se detiene el sorteo
- Se limpian todas las interfaces
- Se generan nuevos cartones para todos
- El sistema vuelve al estado inicial

## 💡 Futuras mejoras recomendadas
- Sonido al anunciar balota
- Animación de confeti para el ganador
- Panel de historial de balotas
- Modo claro / modo oscuro alternable
- Posibilidad de tener múltiples salas

---

## 👨‍💻 Desarrollado por Juan + Jhennifer 
Versión estable y final del semestre.
