"""
Módulo de Entorno y Escenarios para Simulación de Inundación (Fase 1).
Implementación completa del modelo de datos del terreno, modificaciones dinámicas
y generación de escenarios para evacuación.
"""

from typing import List, Tuple, Union, Optional
from enum import IntEnum


# ==========================================
# DEFINICIONES Y TIPOS DE CELDAS
# ==========================================

class CellType(IntEnum):
    BLOQUEADO = -1  # Intransitable / inundación severa / escombros
    LIBRE = 0       # Transitable / sin riesgo significativo
    RIESGO = 1      # Zona con riesgo o inundación parcial (1 a 10)


# Constantes globales directas para fácil acceso
BLOQUEADO: int = CellType.BLOQUEADO
LIBRE: int = CellType.LIBRE
RIESGO_MIN: int = 1
RIESGO_MAX: int = 10


# ==========================================
# CLASE DE ENTORNO EN CUADRÍCULA
# ==========================================

class GridEnvironment:
    """
    Representa el terreno cuadriculado para la simulación de evacuación ante inundación.

    Atributos principales:
    - grid: Matriz numérica bidimensional donde cada celda almacena:
            -1 (BLOQUEADO / Intransitable)
             1 a 10 (Nivel de riesgo / costo de tránsito, donde 1 es riesgo mínimo/libre)
    - start: Coordenada inicial del agente (r, c).
    - goal: Coordenada del refugio (r, c).
    - size: Dimensión de la cuadrícula (por defecto 10x10).
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

        # Validar coordenadas de inicio y refugio
        self._validar_coordenada(start[0], start[1], "Posición de inicio (start)")
        self.start: Tuple[int, int] = start

        self.goal: Tuple[int, int] = goal if goal is not None else (self.rows - 1, self.cols - 1)
        self._validar_coordenada(self.goal[0], self.goal[1], "Posición del refugio (goal)")

        # Matriz principal del terreno: costo/riesgo base = 1.0 (transitable)
        # Valores: -1 = Bloqueado, 1 a 10 = Costo / Nivel de Riesgo
        self.grid: List[List[float]] = [
            [1.0 for _ in range(self.cols)] for _ in range(self.rows)
        ]

    # -------------------------------------------------------------
    # Métodos de validación y acceso
    # -------------------------------------------------------------

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
        """
        Retorna el costo o nivel de riesgo asociado al transitar por (r, c).
        Si la celda está bloqueada, retorna infinito.
        """
        if self.esta_bloqueada(r, c):
            return float("inf")
        return self.grid[r][c]

    # Propiedades de compatibilidad
    @property
    def grid_type(self) -> List[List[int]]:
        """Mapeo del estado de cada celda: -1 (Bloqueado), 0 (Libre), 1 (Riesgo > 1)."""
        matriz_tipos = []
        for r in range(self.rows):
            fila = []
            for c in range(self.cols):
                val = self.grid[r][c]
                if val == CellType.BLOQUEADO:
                    fila.append(int(CellType.BLOQUEADO))
                elif val > 1.0:
                    fila.append(int(CellType.RIESGO))
                else:
                    fila.append(int(CellType.LIBRE))
            matriz_tipos.append(fila)
        return matriz_tipos

    @property
    def risk_level(self) -> List[List[float]]:
        """Retorna la matriz de niveles de riesgo/costos."""
        return self.grid

    # -------------------------------------------------------------
    # Métodos de modificación dinámica
    # -------------------------------------------------------------

    def _normalizar_coordenadas(
        self, coordenadas: Union[Tuple[int, int], List[Tuple[int, int]]]
    ) -> List[Tuple[int, int]]:
        """Permite que los métodos reciban una tupla (r, c) o una lista [(r, c), ...]."""
        if isinstance(coordenadas, tuple) and len(coordenadas) == 2 and isinstance(coordenadas[0], int):
            return [coordenadas]
        return list(coordenadas)

    def bloquear_zona(self, coordenadas: Union[Tuple[int, int], List[Tuple[int, int]]]) -> None:
        """
        Cambia el estado de una celda o lista de celdas a bloqueadas (-1).
        """
        for r, c in self._normalizar_coordenadas(coordenadas):
            if self.es_valida(r, c):
                self.grid[r][c] = float(CellType.BLOQUEADO)

    def modificar_riesgo(
        self,
        coordenadas: Union[Tuple[int, int], List[Tuple[int, int]]],
        nuevo_nivel: float
    ) -> None:
        """
        Actualiza el costo/riesgo de una celda o región específica (rango 1 a 10).
        """
        if not (RIESGO_MIN <= nuevo_nivel <= RIESGO_MAX):
            raise ValueError(f"El nivel de riesgo debe estar entre {RIESGO_MIN} y {RIESGO_MAX}. Recibido: {nuevo_nivel}")

        for r, c in self._normalizar_coordenadas(coordenadas):
            if self.es_valida(r, c):
                self.grid[r][c] = float(nuevo_nivel)

    def aislar_refugio(self, incluir_diagonales: bool = True) -> None:
        """
        Bloquea todas las celdas adyacentes al refugio (goal)
        para simular un escenario de refugio completamente inaccesible.
        """
        gr, gc = self.goal
        deltas = [
            (-1, 0), (1, 0), (0, -1), (0, 1)  # Arriba, abajo, izquierda, derecha
        ]
        if incluir_diagonales:
            deltas.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])

        adyacentes = []
        for dr, dc in deltas:
            nr, nc = gr + dr, gc + dc
            if self.es_valida(nr, nc) and (nr, nc) != self.start:
                adyacentes.append((nr, nc))

        self.bloquear_zona(adyacentes)

    def obtener_vecinos(
        self,
        pos: Union[Tuple[int, int], int],
        *args: int,
        permitir_diagonales: bool = False
    ) -> List[Tuple[int, int]]:
        """
        Devuelve las celdas vecinas válidas (arriba, abajo, izquierda, derecha)
        que no estén bloqueadas ni fuera de los límites.
        Acepta tanto pos=(r, c) como obtener_vecinos(r, c).
        """
        if isinstance(pos, tuple):
            r, c = pos
        else:
            r = pos
            c = args[0]

        movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # 4 direcciones cardinales
        if permitir_diagonales:
            movimientos.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])

        vecinos = []
        for dr, dc in movimientos:
            nr, nc = r + dr, c + dc
            if self.es_valida(nr, nc) and not self.esta_bloqueada(nr, nc):
                vecinos.append((nr, nc))
        return vecinos

    def mostrar_mapa(self) -> str:
        """
        Función auxiliar en texto formateado para visualizar rápidamente la matriz,
        el inicio (S) y el refugio (G) por consola.
        """
        filas_str = []
        for r in range(self.rows):
            fila = []
            for c in range(self.cols):
                if (r, c) == self.start:
                    fila.append(" S ")
                elif (r, c) == self.goal:
                    fila.append(" G ")
                elif self.esta_bloqueada(r, c):
                    fila.append("[X]")
                elif self.grid[r][c] > 1.0:
                    fila.append(f"~{int(self.grid[r][c])}~")
                else:
                    fila.append(" . ")
            filas_str.append("".join(fila))

        mapa_texto = "\n".join(filas_str)
        print(mapa_texto)
        return mapa_texto


# ==========================================
# GENERACIÓN DE ESCENARIOS PREDEFINIDOS
# ==========================================

def crear_escenario_1(size: int = 10, rows: Optional[int] = None, cols: Optional[int] = None) -> GridEnvironment:
    """
    Escenario 1: Terreno normal con rutas de riesgo variable.
    - Contiene zonas con agua de riesgo moderado (4) y corrientes severas (8).
    - Derrumbes bloqueados dispersos.
    - Existen rutas transitables alternativas con menor costo.
    """
    env = GridEnvironment(size=size, rows=rows, cols=cols)

    # Derrumbes fijos
    derrumbes = [(1, 3), (2, 3), (3, 3), (6, 6), (7, 6)]
    env.bloquear_zona(derrumbes)

    # Zonas de riesgo variable (inundación parcial)
    inundacion_moderada = [(3, 4), (4, 4), (5, 4), (4, 5)]
    env.modificar_riesgo(inundacion_moderada, nuevo_nivel=4)

    corriente_peligrosa = [(5, 5), (6, 5), (7, 5)]
    env.modificar_riesgo(corriente_peligrosa, nuevo_nivel=8)

    return env


def crear_escenario_2(size: int = 10, rows: Optional[int] = None, cols: Optional[int] = None) -> GridEnvironment:
    """
    Escenario 2: Ruta óptima bloqueada en una celda clave.
    - Basado en el Escenario 1.
    - Se bloquea la ruta óptima anterior mediante colapso del paso clave central,
      forzando al agente a rodear la zona o calcular una ruta alterna.
    """
    env = crear_escenario_1(size=size, rows=rows, cols=cols)

    # Bloqueo crítico en el cuello de botella
    paso_critico = [(4, 5), (5, 5), (5, 6), (5, 7), (5, 8)]
    env.bloquear_zona(paso_critico)

    return env


def crear_escenario_3(size: int = 10, rows: Optional[int] = None, cols: Optional[int] = None) -> GridEnvironment:
    """
    Escenario 3: Refugio totalmente aislado.
    - Se aísla por completo el refugio bloqueando todas las celdas adyacentes.
    - Permite verificar el manejo de rutas inexistentes o fallos de alcance.
    """
    env = crear_escenario_1(size=size, rows=rows, cols=cols)
    env.aislar_refugio(incluir_diagonales=True)
    return env


def obtener_escenario(
    id_escenario: int,
    size: int = 10,
    rows: Optional[int] = None,
    cols: Optional[int] = None
) -> GridEnvironment:
    """
    Función de fábrica para devolver cualquiera de los 3 escenarios listos para usar.
    """
    escenarios = {
        1: crear_escenario_1,
        2: crear_escenario_2,
        3: crear_escenario_3
    }
    if id_escenario not in escenarios:
        raise ValueError(f"Escenario {id_escenario} no válido. Opciones disponibles: 1, 2, 3.")

    return escenarios[id_escenario](size=size, rows=rows, cols=cols)


if __name__ == "__main__":
    print("=== REVISIÓN DE ESCENARIOS DE ENTORNO ===")
    for num in [1, 2, 3]:
        print(f"\n--- ESCENARIO {num} ---")
        entorno = obtener_escenario(num)
        entorno.mostrar_mapa()
