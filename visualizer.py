"""
Módulo de Visualización Gráfica (Fase 4).
Genera representaciones visuales del terreno, mapas de calor de riesgo y rutas calculadas.
"""

from typing import List, Tuple, Optional, Dict, Any
from environment import GridEnvironment, CellType
from search_algorithms import SearchResult


class EnvironmentVisualizer:
    """Clase para renderizado gráfico del mapa y rutas de evacuación."""

    def __init__(self, env: GridEnvironment):
        self.env = env

    def graficar_terreno(
        self,
        titulo: str = "Mapa de Riesgo y Terreno de Inundación",
        guardar_en: Optional[str] = None
    ) -> None:
        """
        Dibuja el mapa de calor según el nivel de riesgo y marca los bloques intransitables,
        el inicio (Start) y el refugio (Goal).
        
        TODO: Implementar usando matplotlib / seaborn (imshow / heatmap).
        """
        # TODO: Configurar figura, colormap para riesgo (1 a 10) y celdas bloqueadas
        pass

    def graficar_ruta(
        self,
        resultado: SearchResult,
        nombre_algoritmo: str = "Algoritmo de Búsqueda",
        guardar_en: Optional[str] = None
    ) -> None:
        """
        Superpone el camino encontrado por un algoritmo sobre el mapa de riesgo.
        
        TODO: Trazar coordenadas del camino sobre la matriz del entorno.
        """
        # TODO: Dibujar línea de trayectoria y puntos intermedios
        pass

    def graficar_comparativa_rutas(
        self,
        resultados_algoritmos: Dict[str, SearchResult],
        guardar_en: Optional[str] = None
    ) -> None:
        """
        Dibuja múltiples rutas encontradas por distintos algoritmos en una misma vista
        o en subplots para comparar visualmente las decisiones de cada uno.
        
        TODO: Configurar subplots o superposición de múltiples trayectorias con diferentes colores.
        """
        # TODO: Implementar visualización comparativa de rutas
        pass

    @staticmethod
    def graficar_metricas_barras(
        metricas_comparativas: List[Dict[str, Any]],
        guardar_en: Optional[str] = None
    ) -> None:
        """
        Genera gráficos de barras comparando tiempo de ejecución, nodos expandidos y costo total.
        
        TODO: Implementar diagramas de barras con matplotlib.
        """
        # TODO: Crear gráficos de barras de métricas comparativas
        pass
