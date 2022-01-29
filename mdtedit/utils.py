

def colored(r: int, g: int, b: int, text: str) -> str:
    """Returns a colored version of the string."""
    # return "\033[38;2;{};{};{}m{}\033[38;2;255;255;255m".format(r, g, b, text)
    return "\033[38;2;{};{};{}m{}\033[m".format(r, g, b, text)


# def main():
#     import re
#     import os
    
#     sample = "directory/subdirectory/file-name-123.txt"
#     search = "-"
#     replace = "_"
    
#     head, tail = os.path.split(sample)
#     tail, ext = os.path.splitext(tail)
    
#     print(os.path.join(head, tail+ext))
    
#     matches = re.findall(search, sample)
#     for match in matches:
#         print(match)
#     colored_text = re.sub(search, lambda m: colored(255,0,0,m.group()) + colored(0,255,0,replace), sample)
#     print(colored_text)


# if __name__ == "__main__":
#     main()