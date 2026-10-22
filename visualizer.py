"""
Módulo de Visualización Gráfica (Fase 4).
Genera representaciones visuales del terreno, mapas de calor de riesgo y rutas calculadas.
"""

from typing import List, Tuple, Optional, Dict, Any

import matplotlib.pyplot as plt
import numpy as np

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
        """

        matriz = np.array(self.env.grid, dtype=float)

        # Configurar el mapa de calor y las celdas bloqueadas.
        matriz_riesgo = np.ma.masked_where(
            matriz == CellType.BLOQUEADO,
            matriz
        )

        colores = plt.get_cmap("YlOrRd").copy()
        colores.set_bad(color="#364152")

        figura, ax = plt.subplots(figsize=(10, 8))

        imagen = ax.imshow(
            matriz_riesgo,
            cmap=colores,
            vmin=1,
            vmax=10,
            interpolation="nearest"
        )

        barra = figura.colorbar(imagen, ax=ax)
        barra.set_label("Nivel de riesgo (1 = bajo, 10 = alto)")

        # Mostrar cuadrícula y coordenadas.
        ax.set_xticks(np.arange(self.env.cols))
        ax.set_yticks(np.arange(self.env.rows))
        ax.set_xticks(np.arange(-0.5, self.env.cols, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, self.env.rows, 1), minor=True)
        ax.grid(which="minor", color="white", linewidth=0.6)
        ax.tick_params(which="minor", bottom=False, left=False)

        # Marcar inicio y refugio.
        inicio_fila, inicio_columna = self.env.start
        meta_fila, meta_columna = self.env.goal

        ax.scatter(
            inicio_columna,
            inicio_fila,
            marker="o",
            s=150,
            color="green",
            edgecolors="white",
            linewidths=1.5,
            label="Inicio (Start)",
            zorder=5
        )

        ax.scatter(
            meta_columna,
            meta_fila,
            marker="*",
            s=250,
            color="blue",
            edgecolors="white",
            linewidths=1.5,
            label="Refugio (Goal)",
            zorder=5
        )

        ax.set_title(titulo)
        ax.set_xlabel("Columna")
        ax.set_ylabel("Fila")
        ax.legend(loc="upper right")
        ax.set_xlim(-0.5, self.env.cols - 0.5)
        ax.set_ylim(self.env.rows - 0.5, -0.5)

        figura.tight_layout()

        if guardar_en:
            figura.savefig(guardar_en, dpi=200, bbox_inches="tight")

        plt.show()
        plt.close(figura)

    def graficar_ruta(
        self,
        resultado: SearchResult,
        nombre_algoritmo: str = "Algoritmo de Búsqueda",
        guardar_en: Optional[str] = None
    ) -> None:
        """
        Superpone el camino encontrado por un algoritmo sobre la matriz del entorno.
        """

        matriz = np.array(self.env.grid, dtype=float)
        matriz_riesgo = np.ma.masked_where(
            matriz == CellType.BLOQUEADO,
            matriz
        )

        colores = plt.get_cmap("YlOrRd").copy()
        colores.set_bad(color="#364152")

        figura, ax = plt.subplots(figsize=(10, 8))

        imagen = ax.imshow(
            matriz_riesgo,
            cmap=colores,
            vmin=1,
            vmax=10,
            interpolation="nearest"
        )

        barra = figura.colorbar(imagen, ax=ax)
        barra.set_label("Nivel de riesgo (1 = bajo, 10 = alto)")

        # Marcar el inicio y el refugio.
        inicio_fila, inicio_columna = self.env.start
        meta_fila, meta_columna = self.env.goal

        ax.scatter(
            inicio_columna,
            inicio_fila,
            marker="o",
            s=150,
            color="green",
            edgecolors="white",
            linewidths=1.5,
            label="Inicio (Start)",
            zorder=5
        )

        ax.scatter(
            meta_columna,
            meta_fila,
            marker="*",
            s=250,
            color="blue",
            edgecolors="white",
            linewidths=1.5,
            label="Refugio (Goal)",
            zorder=5
        )

        # Dibujar la ruta calculada.
        if resultado.success and resultado.path:
            filas = [coordenada[0] for coordenada in resultado.path]
            columnas = [coordenada[1] for coordenada in resultado.path]

            ax.plot(
                columnas,
                filas,
                color="#00A6FF",
                linewidth=3,
                marker="o",
                markersize=4,
                label="Ruta encontrada",
                zorder=4
            )

            ax.set_title(
                f"Ruta de evacuación - {nombre_algoritmo}\n"
                f"Costo: {resultado.total_cost:.2f} | "
                f"Nodos expandidos: {resultado.expanded_nodes} | "
                f"Tiempo: {resultado.execution_time:.6f} s"
            )
        else:
            ax.set_title(f"Ruta de evacuación - {nombre_algoritmo}")

            ax.text(
                0.5,
                0.5,
                "No se encontró una ruta al refugio",
                transform=ax.transAxes,
                ha="center",
                va="center",
                fontsize=12,
                color="white",
                bbox={
                    "facecolor": "#B42318",
                    "alpha": 0.9,
                    "pad": 8
                }
            )

        ax.set_xlabel("Columna")
        ax.set_ylabel("Fila")
        ax.set_xticks(np.arange(self.env.cols))
        ax.set_yticks(np.arange(self.env.rows))
        ax.set_xticks(np.arange(-0.5, self.env.cols, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, self.env.rows, 1), minor=True)
        ax.grid(which="minor", color="white", linewidth=0.6)
        ax.tick_params(which="minor", bottom=False, left=False)
        ax.legend(loc="upper right")
        ax.set_xlim(-0.5, self.env.cols - 0.5)
        ax.set_ylim(self.env.rows - 0.5, -0.5)

        figura.tight_layout()

        if guardar_en:
            figura.savefig(guardar_en, dpi=200, bbox_inches="tight")

        plt.show()
        plt.close(figura)

    def graficar_comparativa_rutas(
        self,
        resultados_algoritmos: Dict[str, SearchResult],
        guardar_en: Optional[str] = None
    ) -> None:
        """
        Dibuja múltiples rutas encontradas por distintos algoritmos en una misma vista
        para comparar visualmente las decisiones de cada uno.
        """

        if not resultados_algoritmos:
            raise ValueError("Debes proporcionar resultados de búsqueda.")

        matriz = np.array(self.env.grid, dtype=float)
        matriz_riesgo = np.ma.masked_where(
            matriz == CellType.BLOQUEADO,
            matriz
        )

        colores_mapa = plt.get_cmap("YlOrRd").copy()
        colores_mapa.set_bad(color="#364152")

        figura, ax = plt.subplots(figsize=(12, 8))

        imagen = ax.imshow(
            matriz_riesgo,
            cmap=colores_mapa,
            vmin=1,
            vmax=10,
            interpolation="nearest"
        )

        barra = figura.colorbar(imagen, ax=ax)
        barra.set_label("Nivel de riesgo (1 = bajo, 10 = alto)")

        # Marcar el inicio y el refugio.
        inicio_fila, inicio_columna = self.env.start
        meta_fila, meta_columna = self.env.goal

        ax.scatter(
            inicio_columna,
            inicio_fila,
            marker="o",
            s=150,
            color="green",
            edgecolors="white",
            linewidths=1.5,
            label="Inicio (Start)",
            zorder=6
        )

        ax.scatter(
            meta_columna,
            meta_fila,
            marker="*",
            s=250,
            color="blue",
            edgecolors="white",
            linewidths=1.5,
            label="Refugio (Goal)",
            zorder=6
        )

        # Asignar un color diferente a cada algoritmo.
        paleta = plt.get_cmap("tab10").colors

        for indice, (nombre, resultado) in enumerate(
            resultados_algoritmos.items()
        ):
            color = paleta[indice % len(paleta)]

            if resultado.success and resultado.path:
                filas = [p[0] for p in resultado.path]
                columnas = [p[1] for p in resultado.path]

                ax.plot(
                    columnas,
                    filas,
                    color=color,
                    linewidth=2.5,
                    marker="o",
                    markersize=3,
                    label=(
                        f"{nombre} "
                        f"(costo: {resultado.total_cost:.2f})"
                    ),
                    zorder=4
                )
            else:
                ax.plot(
                    [],
                    [],
                    color=color,
                    linestyle="--",
                    linewidth=2,
                    label=f"{nombre} (sin ruta)"
                )

        ax.set_title("Comparación de rutas de evacuación")
        ax.set_xlabel("Columna")
        ax.set_ylabel("Fila")
        ax.set_xticks(np.arange(self.env.cols))
        ax.set_yticks(np.arange(self.env.rows))
        ax.set_xticks(np.arange(-0.5, self.env.cols, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, self.env.rows, 1), minor=True)
        ax.grid(which="minor", color="white", linewidth=0.6)
        ax.tick_params(which="minor", bottom=False, left=False)
        ax.legend(loc="best", fontsize=8)
        ax.set_xlim(-0.5, self.env.cols - 0.5)
        ax.set_ylim(self.env.rows - 0.5, -0.5)

        figura.tight_layout()

        if guardar_en:
            figura.savefig(guardar_en, dpi=200, bbox_inches="tight")

        plt.show()
        plt.close(figura)

    @staticmethod
    def graficar_metricas_barras(
        metricas_comparativas: List[Dict[str, Any]],
        guardar_en: Optional[str] = None
    ) -> None:
        """
        Genera gráficos de barras comparando tiempo de ejecución, nodos expandidos y costo total.
        """

        if not metricas_comparativas:
            raise ValueError("No hay métricas para comparar.")

        # Obtener el nombre de cada algoritmo.
        nombres = []

        for indice, metrica in enumerate(metricas_comparativas, start=1):
            nombre = (
                metrica.get("algoritmo")
                or metrica.get("nombre_algoritmo")
                or metrica.get("algorithm")
                or metrica.get("nombre")
                or f"Algoritmo {indice}"
            )
            nombres.append(str(nombre))

        # Definir las métricas que se van a comparar.
        metricas = [
            (
                "Tiempo de ejecución (s)",
                ("execution_time", "tiempo_ejecucion", "tiempo", "runtime")
            ),
            (
                "Nodos expandidos",
                (
                    "expanded_nodes",
                    "nodos_expandidos",
                    "nodos_explorados",
                    "nodos_visitados"
                )
            ),
            (
                "Costo total",
                ("total_cost", "costo_total", "costo", "cost")
            )
        ]

        figura, ejes = plt.subplots(1, 3, figsize=(15, 5))

        for ax, (titulo, claves) in zip(ejes, metricas):
            nombres_validos = []
            valores_validos = []

            for nombre, datos in zip(nombres, metricas_comparativas):
                valor = None

                for clave in claves:
                    if clave in datos and datos[clave] is not None:
                        try:
                            numero = float(datos[clave])

                            if np.isfinite(numero):
                                valor = numero
                                break
                        except (TypeError, ValueError):
                            continue

                if valor is not None:
                    nombres_validos.append(nombre)
                    valores_validos.append(valor)

            ax.set_title(titulo)
            ax.set_ylabel(titulo)
            ax.grid(axis="y", linestyle="--", alpha=0.35)
            ax.set_axisbelow(True)

            if valores_validos:
                barras = ax.bar(
                    nombres_validos,
                    valores_validos,
                    color="#3989D9",
                    edgecolor="#245B91"
                )

                ax.tick_params(axis="x", labelrotation=25)

                for barra, valor in zip(barras, valores_validos):
                    ax.annotate(
                        f"{valor:.3g}",
                        (
                            barra.get_x() + barra.get_width() / 2,
                            barra.get_height()
                        ),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha="center",
                        va="bottom",
                        fontsize=8
                    )
            else:
                ax.text(
                    0.5,
                    0.5,
                    "Métrica no disponible",
                    transform=ax.transAxes,
                    ha="center",
                    va="center"
                )

        figura.suptitle("Comparación del rendimiento de los algoritmos")
        figura.tight_layout(rect=(0, 0, 1, 0.92))

        if guardar_en:
            figura.savefig(guardar_en, dpi=200, bbox_inches="tight")

        plt.show()
        plt.close(figura)