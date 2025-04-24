import logging
from pathlib import Path

import gmsh
import numpy as np

import rippl as rp


class Manager:
    """Context manager for Gmsh initialization, meshing, finalization, and more"""

    def __init__(
        self,
        output_dir: Path,
        model_name: str = "Rippl mesh",
        mesh_file_name: str = "mesh.msh",
        debug_mode: bool = False,
    ):
        self.output_dir = output_dir
        self.mesh_file = self.output_dir / Path(mesh_file_name)

        self.model = gmsh.model
        self.model_name = model_name
        self.debug_mode = debug_mode

    def __enter__(self):
        self.section = "Gmsh Manager"
        rp.log.start(self.section)
        gmsh.initialize()
        self.model.add(self.model_name)
        logging.info(f"Model name: {self.model_name}")
        gmsh.option.set_number("General.Terminal", self.debug_mode)
        gmsh.option.set_number("General.Tooltips", self.debug_mode)
        return self

    def __exit__(self, *_):
        gmsh.finalize()
        rp.log.end(self.section)

    def get_model_name(self) -> str:
        return self.model.get_current()

    def show_geometry(
        self,
        points: bool = True,
        lines: bool = True,
        surfaces: bool = True,
        point_numbers: bool = False,
        line_numbers: bool = False,
        surface_numbers: bool = False,
    ) -> None:
        """Open GUI to show created geometry"""

        gmsh.option.set_number("Geometry.Points", points)
        gmsh.option.set_number("Geometry.Lines", lines)
        gmsh.option.set_number("Geometry.Surfaces", surfaces)
        gmsh.option.set_number("Geometry.PointNumbers", point_numbers)
        gmsh.option.set_number("Geometry.LineNumbers", line_numbers)
        gmsh.option.set_number("Geometry.SurfaceNumbers", surface_numbers)
        gmsh.fltk.run()

    def show_mesh(
        self,
        node_numbers: bool = False,
        element_numbers: bool = False,
        element_surfaces: bool = True,
    ) -> None:
        """Open GUI to show created mesh"""

        gmsh.open(self.mesh_file.as_posix())
        gmsh.option.set_number("Geometry.Points", False)
        gmsh.option.set_number("Geometry.Lines", False)
        gmsh.option.set_number("Geometry.Surfaces", False)
        gmsh.option.set_number("Mesh.SurfaceFaces", element_surfaces)
        gmsh.option.set_number("Mesh.PointNumbers", node_numbers)
        gmsh.option.set_number("Mesh.SurfaceNumbers", element_numbers)
        gmsh.fltk.run()

    def mesh(
        self,
        dim: int = 3,
        mesh_size: float | bool = False,
        recombine_all: bool = True,
        quasi_structured: bool = False,
        element_order: int = 1,
        smoothing: int = 100,
        transfinite_automatic: bool = False,
    ) -> None:
        """Mesh created geometry with sane defaults"""

        if mesh_size:
            gmsh.option.set_number("Mesh.MeshSizeFromPoints", False)
            gmsh.option.set_number("Mesh.MeshSizeMin", mesh_size)
            gmsh.option.set_number("Mesh.MeshSizeMax", mesh_size)
        gmsh.option.set_number("Mesh.RecombineAll", recombine_all)
        if quasi_structured:
            gmsh.option.set_number("Mesh.Algorithm", 11)  # quasi-structured
        gmsh.option.set_number("Mesh.ElementOrder", element_order)
        gmsh.option.set_number("Mesh.Smoothing", smoothing)
        if transfinite_automatic:
            self.model.mesh.set_transfinite_automatic()
        self.model.mesh.generate(dim=dim)

        # Save mesh
        gmsh.write(self.mesh_file.as_posix())

        # Get nodes
        node_tags, node_coords, _ = self.model.mesh.get_nodes()
        node_tags -= 1
        nodes = node_coords.reshape(-1, 3)
        num_nodes = nodes.shape[0]
        logging.info(f"Number of nodes: {num_nodes}")

        # Get elements
        element_types, _, element_node_tags_list = self.model.mesh.get_elements(dim=dim)
        if (element_types.shape[0] != 1) or (element_types[0] not in [3, 5]):
            raise NotImplementedError(f"Currently only supporting quadrilateral and hexahedral elements. Mesh needs to be changed. element_types = {[self.model.mesh.get_element_properties(i)[0] for i in element_types]}")
        if element_types[0] == 3:  # quadrilateral elements
            num_nodes_per_element = 4
        if element_types[0] == 5:  # hexahedral elements
            num_nodes_per_element = 8
        elements = np.int64(element_node_tags_list[0].reshape(-1, num_nodes_per_element) - 1)  # for compatibility with PyVista, make sure to use int64 (by default, you get uint64 here)
        num_elements = elements.shape[0]
        logging.info(f"Number of elements: {num_elements}")

        # Store mesh data
        self.mesh_data = {
            "nodes": nodes,
            "elements": elements,
            "num_nodes": num_nodes,
            "num_nodes_per_element": num_nodes_per_element,
            "num_elements": num_elements,
        }

    def create_rectangle(
        self,
        width: float = 1.0,
        height: float = 1.0,
        num_elements_x: int = 10,
        num_elements_y: int = 10,
        show_geometry: bool = False,
        show_mesh: bool = False,
    ) -> None:
        section = "Rectangle"
        rp.log.start(section)

        # Add basic geometric entities
        x, y, z = 0.0, 0.0, 0.0  # position of bottom left point of rectangle
        p1 = self.model.geo.add_point(x, y, z)
        p2 = self.model.geo.add_point(x + width, y, z)
        p3 = self.model.geo.add_point(x + width, y + height, z)
        p4 = self.model.geo.add_point(x, y + height, z)
        c1 = self.model.geo.add_line(p1, p2)
        c2 = self.model.geo.add_line(p2, p3)
        c3 = self.model.geo.add_line(p3, p4)
        c4 = self.model.geo.add_line(p4, p1)
        curve_loop = self.model.geo.add_curve_loop([c1, c2, c3, c4])  # ordered list of connected curves, a sign being associated with each curve (depending on the orientation of the curve to form a loop)
        plane = self.model.geo.add_plane_surface([curve_loop])  # list of curve loops

        # Set node distribution on curves (nodes = elements + 1)
        self.model.geo.mesh.set_transfinite_curve(c1, num_elements_x + 1)  # bottom edge
        self.model.geo.mesh.set_transfinite_curve(c3, num_elements_x + 1)  # top edge
        self.model.geo.mesh.set_transfinite_curve(c2, num_elements_y + 1)  # right edge
        self.model.geo.mesh.set_transfinite_curve(c4, num_elements_y + 1)  # left edge

        # Apply transfinite rule to surface
        self.model.geo.mesh.set_transfinite_surface(plane)

        # Synchronize and visualize geometry
        self.model.geo.synchronize()  # needs to be called before any use of functions outside of the GEO kernel
        if show_geometry:
            self.show_geometry()

        # Generate mesh
        self.mesh(
            dim=2,
            mesh_size=False,
            recombine_all=True,
            quasi_structured=False,
            element_order=1,
            smoothing=100,
            transfinite_automatic=False,
        )
        if show_mesh:
            self.show_mesh()

        self.model.add_physical_group(2, [plane])

        rp.log.end(section)
