# src/shared/bingo_card.py

import random


class BingoCard:
    """
    Representa una cartilla de Bingo estándar 5x5.

    - Cada columna tiene un rango:
        B:  1–15
        I: 16–30
        N: 31–45
        G: 46–60
        O: 61–75
    - La casilla del centro es libre (*).
    - has_bingo() SOLO verifica filas y columnas completas,
      tal como pide el documento del proyecto.
    """

    def __init__(self):
        # grid: matriz 5x5 con los números de la cartilla
        self.grid = self._generate_grid()

        # marked: misma forma 5x5 pero con True/False
        self.marked = [[False for _ in range(5)] for _ in range(5)]

        # Casilla central libre, la marcamos desde el inicio
        self.marked[2][2] = True

    # -------------------------------------------------
    # Generación de la cartilla
    # -------------------------------------------------

    def _generate_column(self, start: int, end: int) -> list:
        """
        Devuelve 5 números únicos aleatorios entre start y end (incluidos).
        Cada columna del Bingo usa un rango distinto.
        """
        numbers = list(range(start, end + 1))
        random.shuffle(numbers)
        return numbers[:5]

    def _generate_grid(self) -> list:
        """
        Genera la matriz 5x5 completa de la cartilla.
        Columnas:
            0 -> B (1–15)
            1 -> I (16–30)
            2 -> N (31–45)
            3 -> G (46–60)
            4 -> O (61–75)
        Centro (2,2) se pondrá luego como 0 (libre).
        """
        # Generar columnas por rango
        col_B = self._generate_column(1, 15)
        col_I = self._generate_column(16, 30)
        col_N = self._generate_column(31, 45)
        col_G = self._generate_column(46, 60)
        col_O = self._generate_column(61, 75)

        # Construimos fila por fila
        grid = []
        for row_idx in range(5):
            row = [
                col_B[row_idx],
                col_I[row_idx],
                col_N[row_idx],
                col_G[row_idx],
                col_O[row_idx],
            ]
            grid.append(row)

        # Casilla del centro libre -> la ponemos como 0
        grid[2][2] = 0
        return grid

    # -------------------------------------------------
    # Operaciones sobre la cartilla
    # -------------------------------------------------

    def mark_number(self, number: int) -> None:
        """
        Marca el número en la cartilla (si existe).
        Recorre la matriz y pone marked[i][j] = True donde coincida.
        """
        for i in range(5):
            for j in range(5):
                if self.grid[i][j] == number:
                    self.marked[i][j] = True

    def has_bingo(self) -> bool:
        """
        Devuelve True si la cartilla tiene BINGO según las reglas del documento:

        1. Todos los números de una FILA han salido (fila completa marcada).
        2. Todos los números de una COLUMNA han salido (columna completa marcada).

        NO revisa diagonales ni cartón completo, solo filas/columnas.
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

    # -------------------------------------------------
    # Representación en texto (para enviar al cliente)
    # -------------------------------------------------

    def to_string(self) -> str:
        """
        Devuelve una representación en texto plano de la cartilla:

        B  I  N  G  O
        1  16 31 46 61
        ...

        La casilla libre del centro se muestra como '*'.
        Este formato es el que luego parsea client.js.
        """
        header = "B  I  N  G  O"
        lines = [header]

        for i in range(5):
            row_vals = []
            for j in range(5):
                value = self.grid[i][j]
                if i == 2 and j == 2:
                    # centro libre
                    row_vals.append("*")
                else:
                    row_vals.append(str(value))
            lines.append(" ".join(row_vals))

        return "\n".join(lines)
