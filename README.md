# 🌊 Rippl

⚠️ Currently, still WIP! ⚠️

Rippl provides a seamless, calm workflow for generating precise meshes and visualizations for your [finite element](https://en.wikipedia.org/wiki/Finite_element_method) simulations.
Designed to harmonize the power of Gmsh and PyVista, Rippl offers a relaxing and reliable environment to handle your pre- and post-processing needs.

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
