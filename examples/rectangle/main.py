import logging

import rippl as rp


def main():
    output_dir = rp.path.set_up()
    rp.log.set_up(output_dir)
    with rp.gmsh.GmshManager(output_dir=output_dir, model_name="Rectangle") as gm:
        gm.create_rectangle(num_elements_x=20, num_elements_y=20)
    logging.info(gm.mesh_data["nodes"])
    logging.info(gm.mesh_data["elements"])
    logging.info(gm.mesh_file)
    pv_mesh = rp.pyvista.get_mesh(gm.mesh_data)
    rp.pyvista.show_mesh(pv_mesh)


if __name__ == "__main__":
    main()
