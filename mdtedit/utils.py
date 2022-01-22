

def colored(r: int, g: int, b: int, text: str) -> str:
    """Returns a colored version of the string."""
    return "\033[38;2;{};{};{}m{}\033[38;2;255;255;255m".format(r, g, b, text)