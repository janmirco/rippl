import logging
from pathlib import Path

import gmsh
import numpy as np


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
        gmsh.initialize()
        self.model.add(self.model_name)
        logging.info(f"Model name: {self.model_name}")
        gmsh.option.set_number("General.Terminal", self.debug_mode)
        gmsh.option.set_number("General.Tooltips", self.debug_mode)
        return self

    def __exit__(self, *_):
        gmsh.finalize()

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

        gmsh.option.set_number("Geometry.Points", False)
        gmsh.option.set_number("Geometry.Lines", False)
        gmsh.option.set_number("Geometry.Surfaces", False)
        gmsh.option.set_number("Mesh.SurfaceFaces", element_surfaces)
        gmsh.option.set_number("Mesh.PointNumbers", node_numbers)
        gmsh.option.set_number("Mesh.SurfaceNumbers", element_numbers)
        gmsh.fltk.run()

    def export_mesh(self) -> None:
        gmsh.write(self.mesh_file.as_posix())

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

        if self.mesh_file.exists():
            gmsh.open(self.mesh_file.as_posix())
        else:
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

        # Get nodes
        node_tags, node_coords, _ = self.model.mesh.get_nodes()
        node_tags -= 1
        nodes = node_coords.reshape(-1, 3)
        num_nodes = nodes.shape[0]
        logging.info(f"Number of nodes: {num_nodes}")

        # Get elements
        element_types, _, element_node_tags_list = self.model.mesh.get_elements(dim=dim)
        if element_types.shape[0] != 1:
            raise NotImplementedError(f"Currently not supporting multiple element types. element_types = {[self.model.mesh.get_element_properties(i)[0] for i in element_types]}")
        if element_types[0] == 3:
            num_nodes_per_element = 4  # bi-linear quadrilateral elements
        elif element_types[0] == 5:
            num_nodes_per_element = 8  # tri-linear hexahedral elements
        elif element_types[0] == 10:
            num_nodes_per_element = 9  # bi-quadratic quadrilateral elements
        elif element_types[0] == 12:
            num_nodes_per_element = 27  # tri-quadratic hexahedral elements
        else:
            raise NotImplementedError(f"Currently only supporting quadrilateral and hexahedral elements. Mesh needs to be changed. element_types = {[self.model.mesh.get_element_properties(i)[0] for i in element_types]}")

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

    def create_dogbone(
        self,
        width: float = 75.0,
        gauge: float = 50.0,
        height: float = 10.0,
        height_inner: float = 5.0,
        show_geometry: bool = False,
        dim: int = 2,
        mesh_size: bool = 1.0,
        recombine_all: bool = True,
        quasi_structured: bool = True,
        element_order: int = 1,
        smoothing: int = 100,
        transfinite_automatic: bool = False,
        show_mesh: bool = False,
    ) -> None:
        # Add basic geometric entities
        x, y, z = 0.0, 0.0, 0.0  # position of bottom left point of rectangle
        rec = self.model.occ.add_rectangle(x, y, z, width, height)
        radius = (height - height_inner) / 2.0
        gauge_start = (width - gauge) / 2.0
        cyl1 = self.model.occ.add_cylinder(x + gauge_start, y, z - 0.5, 0.0, 0.0, 1.0, radius)
        cyl2 = self.model.occ.add_cylinder(x + width - gauge_start, y, z - 0.5, 0.0, 0.0, 1.0, radius)
        cyl3 = self.model.occ.add_cylinder(x + gauge_start, y + height, z - 0.5, 0.0, 0.0, 1.0, radius)
        cyl4 = self.model.occ.add_cylinder(x + width - gauge_start, y + height, z - 0.5, 0.0, 0.0, 1.0, radius)
        box1 = self.model.occ.add_box(x + gauge_start, y, z - 0.5, gauge, radius, 1.0)
        box2 = self.model.occ.add_box(x + gauge_start, y + height, z - 0.5, gauge, -radius, 1.0)
        plane = self.model.occ.cut(
            [(2, rec)],
            [
                (3, cyl1),
                (3, cyl2),
                (3, cyl3),
                (3, cyl4),
                (3, box1),
                (3, box2),
            ],
        )[0][0][1]

        # Synchronize and visualize geometry
        self.model.occ.synchronize()  # needs to be called before any use of functions outside of the GEO kernel
        if show_geometry:
            self.show_geometry()

        # Generate mesh
        self.mesh(
            dim=dim,
            mesh_size=mesh_size,
            recombine_all=recombine_all,
            quasi_structured=quasi_structured,
            element_order=element_order,
            smoothing=smoothing,
            transfinite_automatic=transfinite_automatic,
        )
        if show_mesh:
            self.show_mesh()

        self.model.add_physical_group(dim, [plane])

    def create_rectangle(
        self,
        width: float = 1.0,
        height: float = 1.0,
        num_elements_x: int = 10,
        num_elements_y: int = 10,
        show_geometry: bool = False,
        dim: int = 2,
        mesh_size: bool = False,
        recombine_all: bool = True,
        quasi_structured: bool = False,
        element_order: int = 1,
        smoothing: int = 100,
        transfinite_automatic: bool = False,
        show_mesh: bool = False,
    ) -> None:
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
        logging.info(f"Number of elements in x-direction: {num_elements_x}")
        logging.info(f"Number of elements in y-direction: {num_elements_y}")

        # Apply transfinite rule to surface
        self.model.geo.mesh.set_transfinite_surface(plane)

        # Synchronize and visualize geometry
        self.model.geo.synchronize()  # needs to be called before any use of functions outside of the GEO kernel
        if show_geometry:
            self.show_geometry()

        # Generate mesh
        self.mesh(
            dim=dim,
            mesh_size=mesh_size,
            recombine_all=recombine_all,
            quasi_structured=quasi_structured,
            element_order=element_order,
            smoothing=smoothing,
            transfinite_automatic=transfinite_automatic,
        )
        if show_mesh:
            self.show_mesh()

        self.model.add_physical_group(dim, [plane])
