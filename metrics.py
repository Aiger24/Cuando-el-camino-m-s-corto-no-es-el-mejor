"""
Módulo de Métricas y Validación de Pruebas (Fase 3).
Permite evaluar desempeño de algoritmos y verificar cumplimiento de escenarios.
"""

import math
from typing import List, Dict, Any, Optional
from environment import GridEnvironment, CellType
from search_algorithms import SearchResult, SearchAlgorithm


class MetricsEvaluator:
    """Clase encargada de evaluar, comparar y registrar métricas de búsqueda."""

    @staticmethod
    def validar_camino(env: GridEnvironment, resultado: SearchResult) -> Dict[str, Any]:
        """
        Verifica que el camino retornado sea válido:
        1. Comienza en env.start.
        2. Termina en env.goal.
        3. Todos los pasos son adyacentes y válidos.
        4. Ninguna celda del camino está en estado bloqueado (-1).

        TODO: Implementar validación paso a paso.
        """
        # Si no hay camino, no hay nada que validar
        if resultado is None or not resultado.path:
            return {"valido": False, "errores": ["El camino está vacío o es None"], "costo": None}

        camino = resultado.path
        errores = []

        # 1 y 2. Inicio y refugio
        if tuple(camino[0]) != env.start:
            errores.append(f"No empieza en el inicio {env.start}, empieza en {camino[0]}")
        if tuple(camino[-1]) != env.goal:
            errores.append(f"No termina en el refugio {env.goal}, termina en {camino[-1]}")

        # 3 y 4. Celdas dentro del mapa, no bloqueadas y pasos adyacentes
        for i, (r, c) in enumerate(camino):
            if not env.es_valida(r, c):
                errores.append(f"Celda fuera del mapa: {(r, c)}")
                continue
            if env.esta_bloqueada(r, c):
                errores.append(f"Cruza una celda bloqueada: {(r, c)}")
            if i > 0:
                fila_ant, col_ant = camino[i - 1]
                if abs(r - fila_ant) + abs(c - col_ant) != 1:
                    errores.append(f"Salto inválido entre {(fila_ant, col_ant)} y {(r, c)}")

        # Solo se calcula el costo si la ruta es válida
        costo = None
        if not errores:
            costo = MetricsEvaluator.calcular_costo_real(env, camino)

        return {"valido": len(errores) == 0, "errores": errores, "costo": costo}

    @staticmethod
    def calcular_costo_real(env: GridEnvironment, camino: List[tuple]) -> float:
        """
        Suma el costo acumulado de transitar las celdas de la ruta según el nivel de riesgo del terreno.
        TODO: Implementar cálculo de costo real acumulado.
        """
        # Se suma el costo de cada celda sin contar la de inicio.
        # Si la ruta está vacía, sale del mapa o cruza un bloqueo, devuelve infinito.
        if not camino:
            return float("inf")

        total = 0.0
        for r, c in camino[1:]:
            if not env.es_valida(r, c):
                return float("inf")
            total += env.obtener_costo(r, c)
        return total

    @staticmethod
    def comparar_algoritmos(
        algoritmos: List[SearchAlgorithm]
    ) -> List[Dict[str, Any]]:
        """
        Ejecuta múltiples algoritmos sobre el mismo entorno y recopila métricas:
        - Costo total
        - Nodos expandidos
        - Longitud del camino
        - Tiempo de ejecución

        TODO: Implementar ejecución y agregación de métricas.
        """
        # Una fila de métricas por algoritmo. Las claves coinciden con las que
        # espera visualizer.graficar_metricas_barras.
        tabla = []
        for algoritmo in algoritmos:
            fila = {
                "algoritmo": algoritmo.__class__.__name__,
                "exito": False,
                "costo_total": None,        # el que reporta el algoritmo
                "costo_real": None,         # el que recalcula el validador
                "costo_coincide": None,
                "nodos_expandidos": None,
                "longitud": None,
                "tiempo_ejecucion": None,
                "valido": False,
                "errores": [],
            }

            resultado = algoritmo.buscar()
            if resultado is None:
                fila["errores"].append("buscar() devolvió None (¿algoritmo sin implementar?)")
                tabla.append(fila)
                continue

            fila["exito"] = resultado.success
            fila["nodos_expandidos"] = resultado.expanded_nodes
            fila["tiempo_ejecucion"] = resultado.execution_time

            if resultado.success and resultado.path:
                validacion = MetricsEvaluator.validar_camino(algoritmo.env, resultado)
                fila["valido"] = validacion["valido"]
                fila["errores"] = validacion["errores"]
                fila["longitud"] = len(resultado.path)
                fila["costo_total"] = resultado.total_cost
                fila["costo_real"] = validacion["costo"]
                if validacion["costo"] is not None:
                    fila["costo_coincide"] = math.isclose(resultado.total_cost, validacion["costo"])

            tabla.append(fila)
        return tabla

    @staticmethod
    def imprimir_tabla(tabla: List[Dict[str, Any]]) -> None:
        """Imprime la tabla comparativa en consola."""
        print(f"{'Algoritmo':<22}{'Éxito':<7}{'Costo':<9}{'Longitud':<10}{'Nodos':<8}{'Tiempo (s)':<12}{'Válida':<7}")
        for f in tabla:
            tiempo = f"{f['tiempo_ejecucion']:.6f}" if f["tiempo_ejecucion"] is not None else "-"
            print(f"{f['algoritmo']:<22}{str(f['exito']):<7}{str(f['costo_total']):<9}"
                  f"{str(f['longitud']):<10}{str(f['nodos_expandidos']):<8}{tiempo:<12}{str(f['valido']):<7}")


class TestScenarioValidator:
    """Validador de pruebas obligatorias para los escenarios de simulación."""

    @staticmethod
    def validar_escenario_1(resultado: SearchResult) -> bool:
        """
        Verifica que en el Escenario 1 se encuentre una ruta válida y reporte costo finito.
        TODO: Implementar aserciones de prueba.
        """
        assert resultado is not None, "El algoritmo devolvió None"
        assert resultado.success, "Escenario 1: el algoritmo no encontró la ruta"
        assert resultado.path, "Escenario 1: success=True pero el camino está vacío"
        assert math.isfinite(resultado.total_cost), "Escenario 1: el costo no es finito"
        return True

    @staticmethod
    def validar_escenario_2(resultado_previo: SearchResult, resultado_nuevo: SearchResult) -> bool:
        """
        Verifica que en el Escenario 2 la ruta calculada sea diferente o tenga mayor costo
        debido al bloqueo de la ruta óptima anterior.
        TODO: Implementar aserciones de prueba.
        """
        assert resultado_nuevo is not None and resultado_nuevo.success, \
            "Escenario 2: no se encontró ruta tras el bloqueo"
        misma_ruta = resultado_previo.path == resultado_nuevo.path
        mas_cara = resultado_nuevo.total_cost > resultado_previo.total_cost
        assert (not misma_ruta) or mas_cara, \
            "Escenario 2: la ruta y el costo no cambiaron tras el bloqueo"
        return True

    @staticmethod
    def validar_escenario_3(resultado: SearchResult) -> bool:
        """
        Verifica que en el Escenario 3 el algoritmo reporte falla (success = False o path = None)
        debido a que el refugio está completamente aislado.
        TODO: Implementar aserciones de prueba.
        """
        assert resultado is not None, "Escenario 3: el algoritmo devolvió None en lugar de un resultado"
        assert not resultado.success, "Escenario 3: reporta éxito con el refugio aislado"
        assert not resultado.path, "Escenario 3: reporta un camino con el refugio aislado"
        return True