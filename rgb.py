def rgb(r, g, b):
    """
    This is, at present, a very simple wrapper function for RGB values,
    to allow for clarity in distinguishing color component tuples from
    other numerical data.

    In truth, though, it's mainly so I can use the 'pigments' plugin for atom
    and view the exact color shades in-line with the code that generates them.
    """
    return (r, g, b)
