import gmsh


def start(model_name, debug_mode=False):
    gmsh.initialize()
    gmsh.model.add(model_name)
    gmsh.option.set_number("General.Terminal", debug_mode)
    gmsh.option.set_number("General.Tooltips", debug_mode)


def end():
    gmsh.finalize()
