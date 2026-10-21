"""
Módulo de Algoritmos de Búsqueda y Costos (Fase 2 - Integrante 2).

Costo de entrar a una celda: 1 + peso_riesgo * (nivel - 1)
  peso_riesgo = 0 -> solo distancia; peso_riesgo > 0 -> se penalizan zonas de riesgo.
Si no hay ruta, ningún algoritmo lanza excepción: devuelve success=False y un status.
"""

import heapq
import math
import time
from collections import deque
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

from environment import GridEnvironment

Coord = Tuple[int, int]

STATUS_OK = "RUTA_ENCONTRADA"
STATUS_UNREACHABLE = "REFUGIO_INACCESIBLE"
STATUS_BAD_START = "INICIO_INVALIDO"


@dataclass
class SearchResult:
    path: Optional[List[Coord]]   # start -> goal; None si no hay ruta
    total_cost: float             # costo ponderado por riesgo
    expanded_nodes: int           # nodos procesados
    execution_time: float         # segundos
    success: bool
    status: str = ""
    message: str = ""
    generated_nodes: int = 0      # nodos insertados en la frontera
    steps: int = 0                # longitud de la ruta
    risk_total: float = 0.0       # suma de (nivel - 1) a lo largo de la ruta
    algorithm: str = ""


def heuristic_manhattan(a: Coord, b: Coord) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def heuristic_euclidean(a: Coord, b: Coord) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


class SearchAlgorithm:
    nombre = "SearchAlgorithm"

    def __init__(self, env: GridEnvironment, peso_riesgo: float = 1.0):
        if peso_riesgo < 0:
            raise ValueError("peso_riesgo debe ser >= 0 (si no, A* deja de ser óptimo).")
        self.env = env
        self.peso_riesgo = peso_riesgo

    def calcular_costo_paso(self, origen: Coord, destino: Coord) -> float:
        r, c = destino
        if self.env.esta_bloqueada(r, c):
            return float("inf")
        return 1.0 + self.peso_riesgo * (self.env.grid[r][c] - 1.0)

    def costo_de_ruta(self, ruta: List[Coord]) -> float:
        return sum(self.calcular_costo_paso(a, b) for a, b in zip(ruta, ruta[1:]))

    def riesgo_de_ruta(self, ruta: List[Coord]) -> float:
        return sum(self.env.grid[r][c] - 1.0 for r, c in ruta[1:])

    def _validar_extremos(self) -> Optional[SearchResult]:
        sr, sc = self.env.start
        gr, gc = self.env.goal
        if self.env.esta_bloqueada(sr, sc):
            return self._fallo(STATUS_BAD_START, "El punto inicial está bloqueado")
        if self.env.esta_bloqueada(gr, gc):
            return self._fallo(STATUS_UNREACHABLE, "El refugio está bloqueado")
        return None

    def _fallo(self, status: str, mensaje: str, expandidos: int = 0,
               generados: int = 0, t0: Optional[float] = None) -> SearchResult:
        return SearchResult(
            path=None, total_cost=float("inf"), expanded_nodes=expandidos,
            execution_time=(time.perf_counter() - t0) if t0 is not None else 0.0,
            success=False, status=status, message=mensaje,
            generated_nodes=generados, algorithm=self.nombre,
        )

    def _exito(self, padre: Dict[Coord, Optional[Coord]], expandidos: int,
               generados: int, t0: float) -> SearchResult:
        ruta = [self.env.goal]
        while padre[ruta[-1]] is not None:
            ruta.append(padre[ruta[-1]])
        ruta.reverse()
        return SearchResult(
            path=ruta, total_cost=self.costo_de_ruta(ruta), expanded_nodes=expandidos,
            execution_time=time.perf_counter() - t0, success=True, status=STATUS_OK,
            message="Ruta encontrada", generated_nodes=generados, steps=len(ruta) - 1,
            risk_total=self.riesgo_de_ruta(ruta), algorithm=self.nombre,
        )

    def buscar(self) -> SearchResult:
        raise NotImplementedError("Debe implementarse en una subclase específica.")