import matplotlib as mpl
from matplotlib import cm, colors

import matplotlib_inline.backend_inline


def set_renderer(f="svg"):
    matplotlib_inline.backend_inline.set_matplotlib_formats(f)
