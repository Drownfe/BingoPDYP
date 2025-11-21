# src/server/server.py

import socket
import threading
import random
import time
import os
import sys

# Ajustar sys.path para poder importar desde src/shared
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # carpeta src
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from shared.bingo_card import BingoCard  # ahora sí lo encuentra


HOST = "127.0.0.1"   # localhost
PORT = 5000          # puerto del servidor

# Lista de clientes conectados
clients = []
clients_lock = threading.Lock()

# Estado del juego
game_over = False
drawn_numbers = []   # números ya sorteados


def handle_client(conn, addr, card: BingoCard):
    """
    Hilo por cada cliente.
    - Envía la cartilla al cliente.
    - Escucha si el cliente canta BINGO.
    """
    global game_over

    try:
        print(f"[+] Nuevo cliente conectado: {addr}")

        # 1. Enviar cartilla al cliente
        card_str = card.to_string()
        # Protocolo simple: encabezado CARD, luego la cartilla, luego END_CARD
        conn.sendall(b"CARD\n")
        conn.sendall(card_str.encode("utf-8") + b"\nEND_CARD\n")

        # 2. Escuchar mensajes del cliente
        while not game_over:
            data = conn.recv(1024)
            if not data:
                # El cliente cerró conexión
                break

            msg = data.decode("utf-8").strip()
            print(f"[CLIENTE {addr}] -> {msg}")

            if msg == "BINGO":
                print(f"[!] El cliente {addr} canta ¡BINGO!")
                game_over = True

                # Avisar a todos quién ganó
                winner_msg = f"WINNER {addr}\n"
                with clients_lock:
                    for c in clients:
                        try:
                            c.sendall(winner_msg.encode("utf-8"))
                        except:
                            pass
                break

    except Exception as e:
        print(f"[!] Error con cliente {addr}: {e}")
    finally:
        print(f"[-] Cliente desconectado: {addr}")
        with clients_lock:
            if conn in clients:
                clients.remove(conn)
        conn.close()


def draw_numbers():
    """
    Hilo encargado de sacar balotas y enviarlas a todos los clientes.
    """
    global game_over, drawn_numbers

    # Números del 1 al 75 mezclados
    all_numbers = list(range(1, 76))
    random.shuffle(all_numbers)

    while not game_over and all_numbers:
        number = all_numbers.pop()
        drawn_numbers.append(number)

        # Determinar la letra según el rango
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

        msg = f"BALL {letter}{number}\n"
        print(f"[#] Enviando balota: {msg.strip()}")

        # Enviar la balota a todos los clientes conectados
        with clients_lock:
            for c in clients:
                try:
                    c.sendall(msg.encode("utf-8"))
                except:
                    pass

        # Pequeña pausa para que el juego no sea instantáneo
        time.sleep(1.5)

    print("[#] Fin de balotas o juego terminado.")


def main():
    global game_over

    # Crear socket del servidor
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[+] Servidor escuchando en {HOST}:{PORT}")

    # Hilo que se encarga de ir sacando las balotas
    draw_thread = threading.Thread(target=draw_numbers, daemon=True)
    draw_thread.start()

    try:
        # Aceptar clientes mientras el juego siga activo
        while not game_over:
            conn, addr = server.accept()

            # Agregar cliente a la lista global
            with clients_lock:
                clients.append(conn)

            # Crear cartilla para ese cliente
            card = BingoCard()

            # Crear hilo para manejar al cliente
            client_thread = threading.Thread(
                target=handle_client,
                args=(conn, addr, card),
                daemon=True
            )
            client_thread.start()

    except KeyboardInterrupt:
        print("\n[!] Servidor detenido manualmente.")
    finally:
        game_over = True
        server.close()
        with clients_lock:
            for c in clients:
                c.close()
        print("[*] Servidor cerrado.")


if __name__ == "__main__":
    main()
