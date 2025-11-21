# app.py

import random
import time
import threading

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

from src.shared.bingo_card import BingoCard  # tu clase de cartón


# =========================
# CONFIGURACIÓN FLASK
# =========================

app = Flask(__name__)
app.config["SECRET_KEY"] = "bingo-super-secreto"

# Usamos hilos normales, más simple en Windows / Python 3.13
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")


# =========================
# ESTADO GLOBAL
# =========================

# sid -> {"card": BingoCard, "name": str}
players = {}

# Balotas ya sorteadas (solo número 1–75)
drawn_numbers = []

# ¿Juego corriendo?
game_running = False

# Para evitar condiciones de carrera en hilos
game_lock = threading.Lock()

# Para dar nombres amigables: Jugador 1, Jugador 2, ...
next_player_number = 1


# =========================
# RUTAS HTTP
# =========================

@app.route("/")
def index():
    """Vista de jugador."""
    return render_template("index.html")


@app.route("/admin")
def admin():
    """Vista del panel (profesor/administrador)."""
    return render_template("admin.html")


# =========================
# LOOP DEL JUEGO (HILO)
# =========================

def game_loop():
    """
    Hilo que:
    - Mezcla números 1–75.
    - Saca una balota cada cierto tiempo.
    - Marca en todas las cartillas.
    - Emite la balota a todos.
    - Si detecta BINGO, anuncia ganador y termina.
    - Si se acaban las balotas sin ganador, avisa fin del juego.
    """
    global game_running, drawn_numbers

    print("[GAME] Iniciando loop de juego...")

    with game_lock:
        if game_running:
            print("[GAME] Ya hay un juego corriendo, no inicio otro.")
            return
        game_running = True
        drawn_numbers = []

    all_numbers = list(range(1, 76))
    random.shuffle(all_numbers)

    winner_name = None

    while True:
        with game_lock:
            if not game_running:
                print("[GAME] game_running = False, termino loop.")
                break

        if not all_numbers:
            print("[GAME] No quedan más balotas.")
            break

        number = all_numbers.pop()
        drawn_numbers.append(number)

        # Letra de la balota
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

        token = f"{letter}{number}"
        print(f"[GAME] Balota sorteada: {token}")

        # Marcar número en todas las cartillas
        for sid, data in players.items():
            data["card"].mark_number(number)

        # Enviar balota a todos (jugadores + admin)
        socketio.emit("ball", {"letter": letter, "number": number})

        # Revisar BINGO después de marcar
        for sid, data in players.items():
            card = data["card"]
            name = data.get("name", sid)
            if card.has_bingo():
                winner_name = name
                print(f"[BINGO] ¡{winner_name} tiene BINGO!")
                with game_lock:
                    game_running = False
                # Avisar ganador
                msg = f"🎉 ¡{winner_name} tiene BINGO! 🎉"
                socketio.emit("winner", {"message": msg})
                break

        if not game_running:
            break

        time.sleep(1.5)

    with game_lock:
        game_running = False

    # Si nadie ganó, avisamos fin de juego sin ganador
    if winner_name is None:
        socketio.emit(
            "game_over",
            {"message": "No quedan más balotas. Fin del juego (sin ganador)."}
        )
    else:
        socketio.emit(
            "game_over",
            {"message": f"Juego finalizado. Ganador: {winner_name}."}
        )

    print("[GAME] Loop de juego finalizado.")


# =========================
# EVENTOS SOCKET.IO
# =========================

@socketio.on("connect")
def handle_connect(auth=None):
    """
    Se dispara cuando alguien se conecta por WebSocket.
    auth viene desde el cliente y nos dice si es 'player' o 'admin'.
    """
    global next_player_number

    sid = request.sid
    role = None
    if isinstance(auth, dict):
        role = auth.get("role")

    # ADMIN: no se cuenta como jugador, no tiene cartón
    if role == "admin":
        print(f"[SOCKET] Admin conectado: {sid}")
        socketio.emit("players_count", {"count": len(players)})
        return

    # PLAYER: creamos cartilla y nombre
    print(f"[SOCKET] Jugador conectado: {sid}")

    card = BingoCard()
    player_name = f"Jugador {next_player_number}"
    next_player_number += 1

    players[sid] = {"card": card, "name": player_name}

    # Enviamos cartilla como texto (para parsearla en el cliente)
    emit("card", {
        "name": player_name,
        "text": card.to_string()
    })

    # Si hay historial, lo mandamos
    if drawn_numbers:
        emit("history", {"numbers": drawn_numbers})

    # Actualizar conteo de jugadores en el panel
    socketio.emit("players_count", {"count": len(players)})


@socketio.on("disconnect")
def handle_disconnect(reason):
    """Se dispara cuando alguien se desconecta."""
    sid = request.sid
    print(f"[SOCKET] Desconectado: {sid} | reason={reason}")

    if sid in players:
        del players[sid]
        socketio.emit("players_count", {"count": len(players)})


@socketio.on("start_game")
def handle_start_game():
    """
    Lo dispara solo el admin (botón 'Iniciar juego').
    Crea un hilo con el game_loop.
    """
    print("[ADMIN] start_game recibido, creando hilo del juego...")
    t = threading.Thread(target=game_loop, daemon=True)
    t.start()
    socketio.emit("game_started", {})


# Punto de entrada
if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)
