# 🌊 Rippl

Rippl provides a centralized workflow for generating meshes and visualizations for your [finite element](https://en.wikipedia.org/wiki/Finite_element_method) simulations.
Designed to harmonize the power of [Gmsh](https://gmsh.info/) and [PyVista](https://docs.pyvista.org/), Rippl offers a relaxing environment to handle your pre- and post-processing needs.

## Usage

How to use Rippl can be found in the [examples](examples) directory.
For example, a rectangle with quadrilateral elements can be created using this [script](examples/rectangle/main.py).

## Installation

### Directly via GitHub

Go to your `uv` project and install `rippl`.

```bash
uv add git+https://github.com/janmirco/rippl.git
```

For future updates, simply run the following code block.

```bash
uv lock --upgrade
uv sync
```

### Locally in editable mode

1. Clone repository.

```bash
git clone https://github.com/janmirco/rippl.git
```

2. Go to your `uv` project and install `rippl` in editable mode.

```bash
uv add --editable <PATH_TO_HELLO_REPO>
```

## Software used

- Language: [Python](https://www.python.org/)
- Code execution: [GNU Make](https://www.gnu.org/software/make/)
- Package and project manager: [uv](https://docs.astral.sh/uv/)
- Python packages:
    - [Gmsh](https://gmsh.info/)
    - [NumPy](https://numpy.org/)
    - [PyVista](https://docs.pyvista.org/)
