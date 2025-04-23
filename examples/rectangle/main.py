import rippl as rp


def main():
    with rp.gmsh.GmshManager(model_name="Rectangle") as gm:
        gm.create_rectangle(show_mesh=True)


if __name__ == "__main__":
    main()
