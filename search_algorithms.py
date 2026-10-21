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



class BreadthFirstSearch(SearchAlgorithm):
    """BFS: minimiza pasos; NO considera el riesgo al decidir."""
    nombre = "BFS"

    def buscar(self) -> SearchResult:
        t0 = time.perf_counter()
        err = self._validar_extremos()
        if err:
            return err
        start, goal = self.env.start, self.env.goal
        padre = {start: None}
        cola = deque([start])
        expandidos, generados = 0, 1
        while cola:
            actual = cola.popleft()
            expandidos += 1
            if actual == goal:
                return self._exito(padre, expandidos, generados, t0)
            for v in self.env.obtener_vecinos(actual):
                if v not in padre:
                    padre[v] = actual
                    cola.append(v)
                    generados += 1
        return self._fallo(STATUS_UNREACHABLE, "No existe ruta transitable hasta el refugio",
                           expandidos, generados, t0)


class DijkstraSearch(SearchAlgorithm):
    """Dijkstra / costo uniforme: óptimo respecto al costo ponderado por riesgo."""
    nombre = "Dijkstra"

    def buscar(self) -> SearchResult:
        t0 = time.perf_counter()
        err = self._validar_extremos()
        if err:
            return err
        start, goal = self.env.start, self.env.goal
        g = {start: 0.0}
        padre = {start: None}
        cerrados = set()
        frontera = [(0.0, start)]
        expandidos, generados = 0, 1
        while frontera:
            costo, actual = heapq.heappop(frontera)
            if actual in cerrados:
                continue
            cerrados.add(actual)
            expandidos += 1
            if actual == goal:
                return self._exito(padre, expandidos, generados, t0)
            for v in self.env.obtener_vecinos(actual):
                nuevo = costo + self.calcular_costo_paso(actual, v)
                if nuevo < g.get(v, float("inf")):
                    g[v] = nuevo
                    padre[v] = actual
                    heapq.heappush(frontera, (nuevo, v))
                    generados += 1
        return self._fallo(STATUS_UNREACHABLE, "No existe ruta transitable hasta el refugio",
                           expandidos, generados, t0)
    
class AStarSearch(SearchAlgorithm):
    """A*: f = g + h. Con heurística admisible da el mismo costo que Dijkstra."""
    nombre = "A*"

    def __init__(self, env: GridEnvironment,
                 heuristic_fn: Callable[[Coord, Coord], float] = heuristic_manhattan,
                 peso_riesgo: float = 1.0):
        super().__init__(env, peso_riesgo)
        self.heuristic_fn = heuristic_fn

    def buscar(self) -> SearchResult:
        t0 = time.perf_counter()
        err = self._validar_extremos()
        if err:
            return err
        start, goal = self.env.start, self.env.goal
        g = {start: 0.0}
        padre = {start: None}
        cerrados = set()
        frontera = [(self.heuristic_fn(start, goal), 0.0, start)]
        expandidos, generados = 0, 1
        while frontera:
            _, costo, actual = heapq.heappop(frontera)
            if actual in cerrados:
                continue
            cerrados.add(actual)
            expandidos += 1
            if actual == goal:
                return self._exito(padre, expandidos, generados, t0)
            for v in self.env.obtener_vecinos(actual):
                nuevo = costo + self.calcular_costo_paso(actual, v)
                if nuevo < g.get(v, float("inf")):
                    g[v] = nuevo
                    padre[v] = actual
                    heapq.heappush(frontera, (nuevo + self.heuristic_fn(v, goal), nuevo, v))
                    generados += 1
        return self._fallo(STATUS_UNREACHABLE, "No existe ruta transitable hasta el refugio",
                           expandidos, generados, t0)


class GreedyBestFirstSearch(SearchAlgorithm):
    """Voraz: f = h. Rápido, pero ignora costo acumulado y riesgo."""
    nombre = "Greedy"

    def __init__(self, env: GridEnvironment,
                 heuristic_fn: Callable[[Coord, Coord], float] = heuristic_manhattan,
                 peso_riesgo: float = 1.0):
        super().__init__(env, peso_riesgo)
        self.heuristic_fn = heuristic_fn

    def buscar(self) -> SearchResult:
        t0 = time.perf_counter()
        err = self._validar_extremos()
        if err:
            return err
        start, goal = self.env.start, self.env.goal
        padre = {start: None}
        vistos = {start}
        frontera = [(self.heuristic_fn(start, goal), start)]
        expandidos, generados = 0, 1
        while frontera:
            _, actual = heapq.heappop(frontera)
            expandidos += 1
            if actual == goal:
                return self._exito(padre, expandidos, generados, t0)
            for v in self.env.obtener_vecinos(actual):
                if v not in vistos:
                    vistos.add(v)
                    padre[v] = actual
                    heapq.heappush(frontera, (self.heuristic_fn(v, goal), v))
                    generados += 1
        return self._fallo(STATUS_UNREACHABLE, "No existe ruta transitable hasta el refugio",
                           expandidos, generados, t0)


class DepthFirstSearch(SearchAlgorithm):
    """DFS: devuelve la primera ruta que encuentra; suele ser larga y arriesgada."""
    nombre = "DFS"

    def buscar(self) -> SearchResult:
        t0 = time.perf_counter()
        err = self._validar_extremos()
        if err:
            return err
        start, goal = self.env.start, self.env.goal
        padre = {start: None}
        pila = [start]
        visitados = set()
        expandidos, generados = 0, 1
        while pila:
            actual = pila.pop()
            if actual in visitados:
                continue
            visitados.add(actual)
            expandidos += 1
            if actual == goal:
                return self._exito(padre, expandidos, generados, t0)
            for v in reversed(self.env.obtener_vecinos(actual)):
                if v not in visitados:
                    padre[v] = actual
                    pila.append(v)
                    generados += 1
        return self._fallo(STATUS_UNREACHABLE, "No existe ruta transitable hasta el refugio",
                           expandidos, generados, t0)

    
def ejecutar_todos(env: GridEnvironment, peso_riesgo: float = 1.0) -> Dict[str, SearchResult]:
    """Corre las cinco estrategias sobre el mismo entorno (para métricas y visualización)."""
    algoritmos = [
        BreadthFirstSearch(env, peso_riesgo),
        DepthFirstSearch(env, peso_riesgo),
        DijkstraSearch(env, peso_riesgo),
        AStarSearch(env, heuristic_manhattan, peso_riesgo),
        GreedyBestFirstSearch(env, heuristic_manhattan, peso_riesgo),
    ]
    return {a.nombre: a.buscar() for a in algoritmos}