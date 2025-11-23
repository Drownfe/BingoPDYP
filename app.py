import random
import time
import threading
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

# ====================================================
# CONFIGURACIÓN DEL SERVIDOR
# ====================================================

app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading")

# ====================================================
# ESTADO GLOBAL DEL JUEGO
# ====================================================

players = {}            # sid -> {"name": "Jugador X", "card": BingoCard}
player_count = 0        # contador incremental
drawn_numbers = []      # historial de balotas
balls_remaining = []    # balotas aún por salir
game_running = False    # juego corriendo?
winner = None           # ganador actual
draw_thread = None      # hilo de sorteo
stop_thread = False     # matar hilo cuando reinicia

# ====================================================
# MODELO DE CARTÓN
# ====================================================

class BingoCard:
    def __init__(self):
        self.grid = self.generate_grid()

    def generate_grid(self):
        grid = [[0]*5 for _ in range(5)]

        ranges = {
            0: range(1,16),
            1: range(16,31),
            2: range(31,46),
            3: range(46,61),
            4: range(61,76)
        }

        for col in range(5):
            nums = random.sample(list(ranges[col]), 5)
            for row in range(5):
                grid[row][col] = nums[row]

        grid[2][2] = 0
        return grid

    def to_string(self):
        rows = ["B  I  N  G  O"]
        for row in self.grid:
            line = ""
            for n in row:
                line += "* " if n == 0 else f"{n} "
            rows.append(line.strip())
        return "\n".join(rows)

# ====================================================
# RUTAS
# ====================================================

@app.route("/")
def main_page():
    return render_template("index.html")

@app.route("/admin")
def admin_page():
    return render_template("admin.html")

# ====================================================
# SOCKETS: CONEXIÓN
# ====================================================

@socketio.on("connect")
def handle_connect(auth=None):
    global player_count
    sid = request.sid

    role = auth["role"] if auth else None

    # ADMIN
    if role == "admin":
        print("[ADMIN CONNECTED]", sid)
        emit("admin_status", {
            "running": game_running,
            "drawn": drawn_numbers,
            "players": len(players)
        })
        return

    # JUGADOR
    player_count += 1
    name = f"Jugador {player_count}"

    card = BingoCard()
    players[sid] = {
        "name": name,
        "card": card
    }

    print(f"[PLAYER CONNECT] {name} ({sid})")

    emit("card", {
        "name": name,
        "text": card.to_string()
    })

    socketio.emit("players_count", {"count": len(players)})

# ====================================================
# SOCKETS: DESCONEXIÓN
# ====================================================

@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    if sid in players:
        print("[PLAYER DISCONNECT]", sid)
        del players[sid]
        socketio.emit("players_count", {"count": len(players)})

# ====================================================
# HILO DEL SORTEO
# ====================================================

def draw_balls():
    global game_running, winner, stop_thread, balls_remaining

    print("[DRAW] INICIANDO SORTEO...")

    while game_running and not stop_thread and len(balls_remaining) > 0:

        num = balls_remaining.pop(0)
        drawn_numbers.append(num)

        if 1 <= num <= 15: letter = "B"
        elif 16 <= num <= 30: letter = "I"
        elif 31 <= num <= 45: letter = "N"
        elif 46 <= num <= 60: letter = "G"
        else: letter = "O"

        token = f"{letter}{num}"
        print("[DRAW]", token)

        socketio.emit("ball", {"letter": letter, "number": num})

        if winner:
            print("[DRAW] GANADOR DETECTADO.")
            return

        time.sleep(2)

    print("[DRAW] FIN DEL SORTEO.")
    socketio.emit("game_over", {"message": "No quedan más balotas."})
    game_running = False

# ====================================================
# ADMIN: INICIAR JUEGO
# ====================================================

@socketio.on("admin_start")
def admin_start():
    global game_running, drawn_numbers, balls_remaining
    global winner, draw_thread, stop_thread

    if game_running:
        emit("admin_error", {"message": "Ya está corriendo."})
        return

    print("[ADMIN] Iniciando juego...")

    drawn_numbers = []
    winner = None
    stop_thread = False
    game_running = True
    balls_remaining = list(range(1,76))
    random.shuffle(balls_remaining)

    draw_thread = threading.Thread(target=draw_balls)
    draw_thread.start()

    socketio.emit("admin_status", {"running": True})

# ====================================================
# ADMIN: REINICIAR JUEGO
# ====================================================

@socketio.on("reset_game")
def reset_game():
    global game_running, winner, drawn_numbers, balls_remaining, stop_thread

    print("[ADMIN] Reiniciando juego completamente...")

    stop_thread = True
    game_running = False
    winner = None
    drawn_numbers = []
    balls_remaining = []

    # Primero limpiar UI en todos
    socketio.emit("reset")

    # Luego enviar nuevos cartones
    for sid, pdata in players.items():
        newc = BingoCard()
        pdata["card"] = newc

        socketio.emit("card", {
            "name": pdata["name"],
            "text": newc.to_string()
        }, room=sid)

    socketio.emit("admin_status", {
        "running": False,
        "drawn": [],
        "players": len(players)
    })

    print("[ADMIN] Reinicio completo.")

# ====================================================
# JUGADOR CANTA BINGO
# ====================================================

@socketio.on("bingo")
def player_bingo():
    global winner, game_running

    sid = request.sid
    if sid not in players:
        return

    name = players[sid]["name"]

    if not winner:
        winner = name
        game_running = False
        print("[WINNER]", name)

        socketio.emit("winner", {
            "message": f"🎉 ¡{name} ha ganado el Bingo!"
        })

        socketio.emit("game_over", {"message": "Fin del juego."})


# ====================================================
# EJECUCIÓN
# ====================================================

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
