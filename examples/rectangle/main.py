import logging

import rippl as rp


def main():
    # Set up output directory and logging
    output_dir = rp.path.set_up()
    rp.log.set_up(output_dir)

    # Create mesh using Gmsh
    with rp.gmsh.Manager(output_dir=output_dir, model_name="Rectangle") as gm:
        gm.create_rectangle(
            width=4.0,
            height=2.0,
            num_elements_x=36,
            num_elements_y=18,
        )

    # Access Gmsh manager's properties outside of `with` statement
    logging.info(gm.mesh_data["nodes"])
    logging.info(gm.mesh_data["elements"])
    logging.info(gm.mesh_file)

    # Import mesh data to create PyVista's `UnstructuredGrid`
    with rp.pyvista.Manager(output_dir=output_dir, mesh_data=gm.mesh_data) as pm:
        pm.import_mesh()

    # Access PyVista manager's properties outside of `with` statement
    logging.info(pm.mesh)
    pm.show_mesh()


if __name__ == "__main__":
    main()
