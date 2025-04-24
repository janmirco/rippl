import numpy as np
import pyvista as pv
from numpy.typing import NDArray

import rippl as rp


def _connectivity(elements: NDArray[np.int64], num_nodes_per_element: np.int64) -> NDArray[np.int64]:
    """Get vector containing the connectivity information for PyVista.UnstructuredGrid"""

    return np.hstack(
        [
            np.full(
                (elements.shape[0], 1),
                num_nodes_per_element,
            ),
            elements,
        ],
    ).flatten()


def _cell_type_array(num_elements: int, cell_type: str = "quad") -> NDArray[np.int64]:
    """
    Set array containing VTK cell type number

    See: https://vtk.org/doc/nightly/html/vtkCellType_8h_source.html
    """

    vtk_num = 0
    if cell_type == "quad":
        vtk_num = 9
    elif cell_type == "hexa":
        vtk_num = 12
    else:
        raise ValueError("Used cell type is not implemented!")

    return vtk_num * np.ones(num_elements, dtype=np.int64)


def get_mesh(mesh_data: dict) -> pv.UnstructuredGrid:
    connectivity = rp.pyvista._connectivity(mesh_data["elements"], mesh_data["num_nodes_per_element"])
    cell_types = rp.pyvista._cell_type_array(mesh_data["num_elements"])
    return pv.UnstructuredGrid(connectivity, cell_types, mesh_data["nodes"])


def show_mesh(mesh: pv.UnstructuredGrid) -> None:
    pl = pv.Plotter()
    pl.add_mesh(mesh, show_edges=True)
    pl.camera_position = "xy"
    pl.show()
