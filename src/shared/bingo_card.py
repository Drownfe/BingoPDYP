# src/shared/bingo_card.py
import random


class BingoCard:
    """
    Representa una cartilla de Bingo 5x5 con los rangos clásicos:
    B: 1-15, I: 16-30, N: 31-45, G: 46-60, O: 61-75.

    - La casilla central (fila 2, columna 2) se marca como libre.
    - Tiene métodos para marcar números y verificar si hay BINGO
      por fila o por columna.
    """

    def __init__(self):
        # Matriz 5x5 con los números de la cartilla
        self.grid = self._generate_card()
        # Matriz 5x5 de booleanos para indicar qué casillas están marcadas
        self.marked = [[False] * 5 for _ in range(5)]
        # Casilla central libre
        self.marked[2][2] = True

    def _generate_column(self, start, end, count=5):
        """Genera 'count' números únicos dentro del rango [start, end]."""
        return random.sample(range(start, end + 1), count)

    def _generate_card(self):
        """
        Genera la cartilla completa:
        - 5 columnas con los rangos B, I, N, G, O
        - Luego se transpone a filas para formar la matriz 5x5.
        """
        # Columnas según el Bingo clásico
        columns = [
            self._generate_column(1, 15),    # B
            self._generate_column(16, 30),   # I
            self._generate_column(31, 45),   # N
            self._generate_column(46, 60),   # G
            self._generate_column(61, 75),   # O
        ]

        # Transponer columnas → filas
        grid = [[columns[col][row] for col in range(5)] for row in range(5)]

        # Casilla central puede ser 0 o "libre"
        grid[2][2] = 0
        return grid

    def mark_number(self, number: int):
        """
        Marca el número en la cartilla si existe.
        """
        for i in range(5):
            for j in range(5):
                if self.grid[i][j] == number:
                    self.marked[i][j] = True

    def has_bingo(self) -> bool:
        """
        Retorna True si hay:
        - Una fila completa marcada, o
        - Una columna completa marcada.
        """
        # Revisar filas
        for i in range(5):
            if all(self.marked[i][j] for j in range(5)):
                return True

        # Revisar columnas
        for j in range(5):
            if all(self.marked[i][j] for i in range(5)):
                return True

        return False

    def to_string(self) -> str:
        """
        Convierte la cartilla a un texto amigable para mostrar
        o enviar por socket.
        """
        lines = []
        header = " B   I   N   G   O"
        lines.append(header)
        for i in range(5):
            row_str = []
            for j in range(5):
                val = self.grid[i][j]
                if val == 0:
                    # Casilla central libre
                    cell = " * "
                else:
                    cell = f"{val:2d}"
                row_str.append(cell)
            lines.append("  ".join(row_str))
        return "\n".join(lines)
