from pathlib import Path

import numpy as np
import pyvista as pv
from numpy.typing import NDArray

import rippl as rp


class Manager:
    """Context manager for PyVista"""

    def __init__(self, output_dir: Path, mesh_data: dict):
        self.output_dir = output_dir
        self.mesh_data = mesh_data

    def __enter__(self):
        self.section = "PyVista Manager"
        rp.log.start(self.section)
        return self

    def __exit__(self, *_):
        rp.log.end(self.section)

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

        if self.mesh_data["num_nodes_per_element"] == 4:
            vtk_num = 9  # quadrilateral
        elif self.mesh_data["num_nodes_per_element"] == 8:
            vtk_num = 12  # hexahedral
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
        pl = pv.Plotter()
        pl.add_mesh(self.mesh, show_edges=True)
        pl.camera_position = "xy"
        pl.show()
