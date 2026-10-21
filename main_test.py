"""
Archivo de Pruebas Preliminares e Integración Modular.
Verifica la correcta conexión, importación y estructura de clases entre los módulos:
- environment.py (Fase 1)
- search_algorithms.py (Fase 2)
- metrics.py (Fase 3)
- visualizer.py (Fase 4)
"""

import sys

# 1. Verificación de Importaciones
try:
    from environment import (
        GridEnvironment,
        CellType,
        obtener_escenario,
        crear_escenario_1,
        crear_escenario_2,
        crear_escenario_3
    )
    from search_algorithms import (
        SearchResult,
        SearchAlgorithm,
        BreadthFirstSearch,
        DepthFirstSearch,
        DijkstraSearch,
        AStarSearch,
        GreedyBestFirstSearch,
        heuristic_manhattan,
        heuristic_euclidean
    )
    from metrics import (
        MetricsEvaluator,
        TestScenarioValidator
    )
    from visualizer import (
        EnvironmentVisualizer
    )
    print("[OK] Todos los módulos se importaron correctamente sin errores de sintaxis ni dependencias circulares.")
except ImportError as e:
    print(f"[ERROR] Error al importar módulos: {e}")
    sys.exit(1)


def test_interconexion():
    """Prueba de instanciación e interconexión básica entre módulos."""
    print("\n--- Probando interconexión de componentes ---")
    
    # 1. Cargar entorno (Fase 1)
    env = obtener_escenario(1)
    assert env.rows >= 10 and env.cols >= 10, "El entorno debe ser al menos 10x10"
    print(f"[OK] Entorno cargado exitosamente: {env.rows}x{env.cols}, Start: {env.start}, Goal: {env.goal}")

    # 2. Instanciar algoritmos de búsqueda conectados al entorno (Fase 2)
    bfs = BreadthFirstSearch(env)
    dfs = DepthFirstSearch(env)
    dijkstra = DijkstraSearch(env)
    astar = AStarSearch(env, heuristic_fn=heuristic_manhattan)
    greedy = GreedyBestFirstSearch(env, heuristic_fn=heuristic_euclidean)
    print(f"[OK] Algoritmos instanciados e interconectados con el entorno: "
          f"{[algo.__class__.__name__ for algo in [bfs, dfs, dijkstra, astar, greedy]]}")

    # 3. Instanciar evaluador de métricas y validadores (Fase 3)
    evaluador = MetricsEvaluator()
    validador = TestScenarioValidator()
    print("[OK] Clases de métricas y validación instanciadas correctamente.")

    # 4. Instanciar visualizador conectado al entorno (Fase 4)
    visualizador = EnvironmentVisualizer(env)
    print("[OK] Visualizador conectado correctamente al entorno.")

    print("\n>>> ARQUITECTURA BASE LISTA: Todos los módulos están vinculados y preparados para implementación por fases. <<<")


if __name__ == "__main__":
    test_interconexion()
