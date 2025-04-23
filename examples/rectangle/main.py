import logging

import rippl as rp


def main():
    output_dir = rp.path.set_up()
    rp.log.set_up(output_dir)
    with rp.gmsh.GmshManager(output_dir, model_name="Rectangle") as gm:
        model_name = gm.get_model_name()
        logging.info(f"{model_name = }")
        gm.create_rectangle(show_mesh=True)


if __name__ == "__main__":
    main()
