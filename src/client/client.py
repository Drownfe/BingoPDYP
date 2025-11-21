# src/client/client.py

import socket
import threading
import os
import sys

# Ajustar sys.path para importar desde src/shared
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # carpeta src
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from shared.bingo_card import BingoCard


HOST = "127.0.0.1"
PORT = 5000


def listen_server(sock: socket.socket, card: BingoCard):
    """
    Hilo encargado de escuchar continuamente los mensajes del servidor.
    Procesa:
    - Cartilla recibida
    - Balotas (BALL B12)
    - GANADOR (WINNER ...)
    """

    buffer = ""
    received_card = False

    while True:
        data = sock.recv(1024)
        if not data:
            print("[!] Conexión cerrada por el servidor.")
            break

        buffer += data.decode("utf-8")

        # Procesar línea por línea
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()

            if not line:
                continue

            # Recibiendo inicio de cartilla
            if line == "CARD":
                # recibir la cartilla completa hasta END_CARD
                card_text = ""

                # Esperar hasta que venga END_CARD
                while "END_CARD" not in buffer:
                    more = sock.recv(1024)
                    if not more:
                        break
                    buffer += more.decode()

                # Ahora buffer contiene al menos END_CARD
                card_text, buffer = buffer.split("END_CARD", 1)
                card_text = card_text.strip()

                card.set_from_string(card_text)
                received_card = True

                print("\n=== TU CARTILLA ===")
                card.show()

            # Recibiendo balotas
            elif line.startswith("BALL"):
                if not received_card:
                    continue

                # Ejemplo: BALL B12
                parts = line.split()
                if len(parts) == 2:
                    token = parts[1]          # B12
                    number = int(token[1:])  # 12

                    print(f"[#] Llegó balota: {token}")

                    card.mark_number(number)
                    card.show()

                    if card.has_bingo():
                        print("🎉 ¡¡BINGO!! 🎉")
                        sock.sendall(b"BINGO\n")

            # Anuncio de ganador
            elif line.startswith("WINNER"):
                print(f"\n🟢 El servidor anuncia: {line}")
                print("Juego finalizado.\n")
                return


def main():
    print("[*] Iniciando cliente...")

    # Crear socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    print(f"[+] Conectado al servidor en {HOST}:{PORT}")

    # Crear la cartilla local
    card = BingoCard()

    # Hilo para escuchar al servidor
    listener = threading.Thread(target=listen_server, args=(sock, card))
    listener.start()

    listener.join()
    sock.close()
    print("[*] Cliente finalizado.")


if __name__ == "__main__":
    main()
