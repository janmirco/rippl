import logging

import rippl as rp


def main():
    with rp.gmsh.GmshManager(model_name="Rectangle") as gm:
        gm.create_rectangle(num_elements_x=2, num_elements_y=2)
        logging.info(gm.nodes)
        logging.info(gm.elements)
        logging.info(gm.mesh_file)
        pv_mesh = gm.pyvista_mesh()
        logging.info(pv_mesh)


if __name__ == "__main__":
    main()
