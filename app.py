# app.py
import random
import time
import threading

from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room

from src.shared.bingo_card import BingoCard


# -----------------------------
# Configuración base de Flask
# -----------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = "bingo-super-secreto"  # para sesiones de SocketIO

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")


# -----------------------------
# Estado global del juego
# -----------------------------
players = {}        # sid -> { "card": BingoCard }
drawn_numbers = []  # números ya sorteados
game_running = False
game_lock = threading.Lock()


# -----------------------------
# Rutas HTTP (vistas)
# -----------------------------
@app.route("/")
def index():
    """Vista de jugador (cliente)."""
    return render_template("index.html")


@app.route("/admin")
def admin():
    """Vista del panel de control (servidor)."""
    return render_template("admin.html")


# -----------------------------
# Lógica del sorteo en segundo plano
# -----------------------------
def game_loop():
    global game_running, drawn_numbers

    with game_lock:
        if game_running:
            # Si ya hay un juego en curso, no arrancamos otro
            return
        game_running = True
        drawn_numbers = []

    all_numbers = list(range(1, 76))
    random.shuffle(all_numbers)

    while game_running and all_numbers:
        number = all_numbers.pop()

        drawn_numbers.append(number)

        # Determinar letra
        if 1 <= number <= 15:
            letter = "B"
        elif 16 <= number <= 30:
            letter = "I"
        elif 31 <= number <= 45:
            letter = "N"
        elif 46 <= number <= 60:
            letter = "G"
        else:
            letter = "O"

        # Enviar balota a todos los clientes conectados
        socketio.emit("ball", {"letter": letter, "number": number})

        # Pausa entre balotas (ajustable)
        time.sleep(1.5)

    # Cuando se acaben las balotas o se termine el juego
    with game_lock:
        game_running = False


# -----------------------------
# Eventos de SocketIO
# -----------------------------
@socketio.on("connect")
def handle_connect():
    """
    Cuando un cliente se conecta:
    - Crear una cartilla de Bingo para ese cliente.
    - Enviarle la cartilla.
    """
    sid = threading.get_ident()  # placeholder, lo ajustaremos luego si queremos
    card = BingoCard()

    players[sid] = {"card": card}

    # Enviar cartilla al cliente en formato simple (luego podemos mejorar el JSON)
    emit("card", {"text": card.to_string()})

    # Enviar también las balotas ya sorteadas (si entra a mitad de juego)
    if drawn_numbers:
        emit("history", {"numbers": drawn_numbers})


@socketio.on("disconnect")
def handle_disconnect():
    """
    Limpiar al jugador cuando se desconecta.
    """
    # Aquí podríamos borrar al jugador de players si lo identificamos bien.
    pass


@socketio.on("bingo")
def handle_bingo(data):
    """
    Un cliente avisa que tiene BINGO.
    Más adelante validaremos la cartilla aquí.
    """
    # Por ahora, simplemente avisamos a todos que alguien ganó.
    socketio.emit("winner", {"message": "¡Alguien cantó BINGO!"})

    global game_running
    with game_lock:
        game_running = False


@socketio.on("start_game")
def handle_start_game():
    """
    Evento que se dispara desde el panel admin para iniciar el sorteo.
    """
    socketio.start_background_task(game_loop)
    emit("game_started", broadcast=True)


# -----------------------------
# Punto de entrada
# -----------------------------
if __name__ == "__main__":
    # Usamos eventlet para soportar WebSockets en producción de forma simple
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
