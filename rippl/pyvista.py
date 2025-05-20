import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pyvista as pv
import utly
from numpy.typing import NDArray


@dataclass
class Settings:
    """
    Settings for PyVista plotting.

    Note:
        After changing attributes
        - `color_smooth`
        - `transparent_background`
        you must call `sync()` to update dependent fields and global state.
    """

    transparent_background: bool = False
    color_smooth: bool = True
    n_colors: int = 256
    color_map: str = "turbo"
    color_limits_cutoff: float = 1.0e-10
    show_edges: bool = True
    scalar_bar_height: float = 0.1
    scalar_bar_width: float = 0.5
    scalar_bar_vertical: bool = False
    scalar_bar_shadow: bool = False
    scalar_bar_n_labels: int = 2
    scalar_bar_position_x: float = 0.25
    scalar_bar_position_y: float = 0.0
    show_axes: bool = True
    camera_position: str = "xy"
    screenshot_resolution: tuple[int, int] = (1024, 768)
    image_scale: int = 1
    export_png: bool = True
    export_svg: bool = False

    def __post_init__(self) -> None:
        self.sync()

    def sync(self) -> None:
        self.n_colors = 256 if self.color_smooth else 14
        pv.global_theme.transparent_background = self.transparent_background


class Manager:
    """Context manager for PyVista"""

    def __init__(self, output_dir: Path, mesh_data: dict | pv.UnstructuredGrid):
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
        if isinstance(self.mesh_data, pv.UnstructuredGrid):
            self.mesh = self.mesh_data
        else:
            self.mesh = pv.UnstructuredGrid(
                self._connectivity(),
                self._cell_type_array(),
                self.mesh_data["nodes"],
            )

    def plot(self, pv_set: Settings, quantity_name: str, plotter: Optional[pv.Plotter] = None) -> Optional[pv.Plotter]:
        """
        Function to plot using PyVista.

        Notes:
            - At beginning of this function, PyVistaSettings are updated using `sync()` method.
            - Use `quantity_name = "mesh"` for only plotting the mesh.
        """

        pv_set.sync()

        if quantity_name.lower() == "mesh":
            cmin = 0.0
            cmax = 0.0
        else:
            # Set proper color limits
            data = self.mesh[quantity_name]
            data = np.where(np.abs(data) < pv_set.color_limits_cutoff, 0.0, data)
            cmin = data.min()
            cmax = data.max()
            if np.isclose(cmin, cmax):
                center = 0.0 if np.isclose(cmin, 0.0) else cmin
                cmin = center - pv_set.color_limits_cutoff
                cmax = center + pv_set.color_limits_cutoff

        # Create plotter
        if plotter is None:
            return_plotter = False
            plotter = pv.Plotter(off_screen=True)
        elif isinstance(plotter, pv.Plotter):
            return_plotter = True
        else:
            raise ValueError("`plotter` must be a pyvista.Plotter instance or None.")
        plotter.add_mesh(
            self.mesh.cell_data_to_point_data(),
            scalars=None if quantity_name.lower() == "mesh" else quantity_name,
            n_colors=pv_set.n_colors,
            cmap=pv_set.color_map,
            clim=[cmin, cmax],
            show_edges=pv_set.show_edges,
            scalar_bar_args={
                "height": pv_set.scalar_bar_height,
                "width": pv_set.scalar_bar_width,
                "vertical": pv_set.scalar_bar_vertical,
                "title": quantity_name,
                "shadow": pv_set.scalar_bar_shadow,
                "n_labels": pv_set.scalar_bar_n_labels,
                "n_colors": pv_set.n_colors,
                "position_x": pv_set.scalar_bar_position_x,
                "position_y": pv_set.scalar_bar_position_y,
            },
        )
        if pv_set.show_axes:
            plotter.show_axes()
        plotter.camera_position = pv_set.camera_position
        plotter.window_size = pv_set.screenshot_resolution
        if pv_set.image_scale > 1:
            plotter.image_scale = pv_set.image_scale

        quantity_name = quantity_name.lower()
        quantity_name = quantity_name.replace(" ", "_")
        symbols_to_remove = "'\"()[]{}"
        quantity_name = quantity_name.translate(str.maketrans("", "", symbols_to_remove))

        if pv_set.export_png:
            quantity_png_file = self.output_dir / Path(f"{quantity_name}.png")
            plotter.screenshot(quantity_png_file)
            logging.info(f"Exported: {quantity_png_file}")
        if pv_set.export_svg:
            quantity_svg_file = self.output_dir / Path(f"{quantity_name}.svg")
            plotter.save_graphic(quantity_svg_file)
            logging.info(f"Exported: {quantity_svg_file}")

        if return_plotter:
            return plotter
        else:
            plotter.close()
