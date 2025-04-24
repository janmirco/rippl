import logging

import rippl as rp


def main():
    output_dir = rp.path.set_up()
    rp.log.set_up(output_dir)
    with rp.gmsh.GmshManager(output_dir=output_dir, model_name="Rectangle") as gm:
        gm.create_rectangle(num_elements_x=20, num_elements_y=20)
        logging.info(gm.nodes)
        logging.info(gm.elements)
        logging.info(gm.mesh_file)
        gm.show_pyvista_mesh()


if __name__ == "__main__":
    main()
