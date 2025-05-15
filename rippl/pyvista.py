from pathlib import Path

import numpy as np
import pyvista as pv
import utly
from numpy.typing import NDArray


class Manager:
    """Context manager for PyVista"""

    def __init__(self, output_dir: Path, mesh_data: dict):
        self.output_dir = output_dir
        self.mesh_data = mesh_data

    def __enter__(self):
        self.section = "PyVista Manager"
        utly.log.start(self.section)
        return self

    def __exit__(self, *_):
        utly.log.end(self.section)

    def _connectivity(self) -> NDArray[np.int64]:
        """Get vector containing the connectivity information for PyVista.UnstructuredGrid"""

        return np.hstack(
            [
                np.full(
                    (self.mesh_data["elements"].shape[0], 1),
                    self.mesh_data["num_nodes_per_element"],
                ),
                self.mesh_data["elements"],
            ],
        ).flatten()

    def _cell_type_array(self) -> NDArray[np.int64]:
        """
        Set array containing VTK cell type number

        See: https://vtk.org/doc/nightly/html/vtkCellType_8h_source.html
        """

        vtk_cell_types = {
            # Linear cells
            "VTK_QUAD": 9,
            "VTK_HEXAHEDRON": 12,
            # Quadratic, isoparametric cells
            "VTK_BIQUADRATIC_QUAD": 28,
            "VTK_TRIQUADRATIC_HEXAHEDRON": 29,
        }

        if self.mesh_data["num_nodes_per_element"] == 4:
            vtk_num = vtk_cell_types["VTK_QUAD"]
        elif self.mesh_data["num_nodes_per_element"] == 9:
            vtk_num = vtk_cell_types["VTK_BIQUADRATIC_QUAD"]
        elif self.mesh_data["num_nodes_per_element"] == 8:
            vtk_num = vtk_cell_types["VTK_HEXAHEDRON"]
        elif self.mesh_data["num_nodes_per_element"] == 27:
            vtk_num = vtk_cell_types["VTK_TRIQUADRATIC_HEXAHEDRON"]
        else:
            raise ValueError("Used cell type is not implemented!")

        return vtk_num * np.ones(self.mesh_data["num_elements"], dtype=np.int64)

    def import_mesh(self) -> None:
        self.mesh = pv.UnstructuredGrid(
            self._connectivity(),
            self._cell_type_array(),
            self.mesh_data["nodes"],
        )

    def show_mesh(self) -> None:
        self.plot(
            quantity_name_in_mesh=None,
            screenshot_name="mesh",
            show=True,
        )

    def export_mesh(self) -> None:
        self.plot(
            quantity_name_in_mesh=None,
            screenshot_name="mesh",
            show=False,
        )

    def plot(
        self,
        quantity_name_in_mesh: str,
        screenshot_name: str,
        transparent_background: bool = False,
        show: bool = True,
        color_smooth: bool = True,
        interpolate_centroid_data: bool = False,
        color_map: str = "turbo",
        show_edges: bool = True,
        scalar_bar_height: float = 0.1,
        scalar_bar_width: float = 0.5,
        scalar_bar_vertical: bool = False,
        scalar_bar_title: str = "Quantity",
        scalar_bar_shadow: bool = False,
        scalar_bar_n_labels: int = 2,
        scalar_bar_position_x: float = 0.25,
        scalar_bar_position_y: float = 0.0,
        show_axes: bool = True,
        camera_position: str = "xy",
        screenshot_resolution: tuple[int, int] = (1024, 768),
        image_scale: int = 1,
        export_png: bool = True,
        export_svg: bool = False,
    ) -> None:
        pv.global_theme.transparent_background = transparent_background
        plotter = pv.Plotter(off_screen=not show)
        n_colors = 256 if color_smooth else 14
        plotter.add_mesh(
            self.mesh.cell_data_to_point_data() if interpolate_centroid_data else self.mesh,
            scalars=quantity_name_in_mesh,
            n_colors=n_colors,
            cmap=color_map,
            show_edges=show_edges,
            scalar_bar_args={
                "height": scalar_bar_height,
                "width": scalar_bar_width,
                "vertical": scalar_bar_vertical,
                "title": scalar_bar_title,
                "shadow": scalar_bar_shadow,
                "n_labels": scalar_bar_n_labels,
                "n_colors": n_colors,
                "position_x": scalar_bar_position_x,
                "position_y": scalar_bar_position_y,
            },
        )
        if show_axes:
            plotter.show_axes()
        plotter.camera_position = camera_position
        if show:
            plotter.show()
        else:
            plotter.window_size = screenshot_resolution
            if image_scale > 1:
                plotter.image_scale = image_scale
            if export_png:
                plotter.screenshot(self.output_dir / Path(f"{screenshot_name}.png"))
            if export_svg:
                plotter.save_graphic(self.output_dir / Path(f"{screenshot_name}.svg"))
        plotter.close()
