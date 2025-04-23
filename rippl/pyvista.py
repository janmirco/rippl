import numpy as np
from numpy.typing import NDArray


def connectivity(elements: NDArray[np.int64], num_nodes_per_element: np.int64) -> NDArray[np.int64]:
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


def cell_type_array(num_elements: int, cell_type: str = "quad") -> NDArray[np.int64]:
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
