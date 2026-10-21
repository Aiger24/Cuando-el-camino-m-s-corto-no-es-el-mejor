"""
Módulo de Entorno y Escenarios para Simulación de Inundación (Fase 1).
Estructura base de la matriz de simulación.
"""

from typing import List, Tuple, Union, Optional
from enum import IntEnum


class CellType(IntEnum):
    BLOQUEADO = -1  # Intransitable / inundación severa / escombros
    LIBRE = 0       # Transitable / sin riesgo significativo
    RIESGO = 1      # Zona con riesgo o inundación parcial (1 a 10)


BLOQUEADO: int = CellType.BLOQUEADO
LIBRE: int = CellType.LIBRE
RIESGO_MIN: int = 1
RIESGO_MAX: int = 10


class GridEnvironment:
    """
    Representa el terreno cuadriculado para la simulación de evacuación ante inundación.
    """

    def __init__(
        self,
        size: int = 10,
        rows: Optional[int] = None,
        cols: Optional[int] = None,
        start: Tuple[int, int] = (0, 0),
        goal: Optional[Tuple[int, int]] = None
    ):
        num_rows = rows if rows is not None else size
        num_cols = cols if cols is not None else size

        if num_rows < 10 or num_cols < 10:
            raise ValueError(f"El tamaño de la cuadrícula debe ser de al menos 10x10. Recibido: {num_rows}x{num_cols}.")

        self.size = size
        self.rows = num_rows
        self.cols = num_cols

        self._validar_coordenada(start[0], start[1], "Posición de inicio (start)")
        self.start: Tuple[int, int] = start

        self.goal: Tuple[int, int] = goal if goal is not None else (self.rows - 1, self.cols - 1)
        self._validar_coordenada(self.goal[0], self.goal[1], "Posición del refugio (goal)")

        # Matriz principal del terreno: costo/riesgo base = 1.0 (transitable)
        self.grid: List[List[float]] = [
            [1.0 for _ in range(self.cols)] for _ in range(self.rows)
        ]

    def _validar_coordenada(self, r: int, c: int, etiqueta: str = "Coordenada") -> None:
        """Verifica que la coordenada se encuentre dentro de los límites."""
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            raise IndexError(f"{etiqueta} ({r}, {c}) fuera de los límites de la matriz [{self.rows}x{self.cols}].")

    def es_valida(self, r: int, c: int) -> bool:
        """Retorna True si (r, c) está dentro de los límites de la matriz."""
        return 0 <= r < self.rows and 0 <= c < self.cols

    def esta_bloqueada(self, r: int, c: int) -> bool:
        """Retorna True si la celda es intransitable (-1)."""
        return self.grid[r][c] == CellType.BLOQUEADO

    def obtener_costo(self, r: int, c: int) -> float:
        """Retorna el costo o nivel de riesgo asociado al transitar por (r, c)."""
        if self.esta_bloqueada(r, c):
            return float("inf")
        return self.grid[r][c]
