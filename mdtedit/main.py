import argparse
import re

link_name = "[\[]?[^\[^\]]+[\]]?"
link_url = "https[s]?://[^\)]+"
mdlink_regex = f"\[{link_name}]\({link_url}\)"
mdlink_part_regex = f"\[({link_name})]\(({link_url})\)"


def colored(r: int, g: int, b: int, text: str) -> str:
    return "\033[38;2;{};{};{}m{}\033[38;2;255;255;255m".format(r, g, b, text)


def strip_markdown_links(text:str) -> str:
    """Strips down markdown links and replaces...."""
    print("Links found:\n---")
    for match in re.findall(mdlink_regex, text):
        print(match)
    colored_print = re.sub(mdlink_part_regex, colored(255,0,0,r'\1'), text)
    print("Changes made:\n---")
    print(colored_print)
    
    return re.sub(mdlink_part_regex, r'\1', text)


def remove_extra_whitespaces(text:str) -> str:
    """Removes trailing and extra whitespaces, and redundant whitespaces before a period or comma."""
    text = re.sub('[ ]+', ' ', text.strip())
    return re.sub('[ ]([,|.])', r'\1', text)


def remove_regex_matches(text:str, regex:str) -> str:
    """Removes searches of the following."""
    print("The following searches have been removed: ")
    colored_print = re.sub(f'({regex})', colored(255,0,0,r'\1'), text)
    print(colored_print)
    return re.sub(regex, '', text)


def run(args):
    if args.filename:
        with open(args.filename) as f:
            file = f.read()
            f.seek(0)
            if args.whitespaces:
                file = remove_extra_whitespaces(file)
            if args.remove_links:
                file = strip_markdown_links(file)
            if args.remove_regex:
                file = remove_regex_matches(file, args.remove_regex)
            f.write(file)
            f.truncate()

def main():
    """Process command line arguments and execute the given command.""" 
    parser = argparse.ArgumentParser(description="Markdown regex editor command line utility.")
    
    parser.add_argument('-f', '--filename', help='filename to parse', type=str, required=True)
    parser.add_argument('-l', '--remove-links', help='removes links and replaces it with the link name')
    parser.add_argument('-r', '--remove-regex', help='removes custom perl regex matches from the file', type=str, required=False)
    parser.add_argument('-w', '--whitespaces', help='removes extra whitespaces, and redundant whitespaces before a period or comma', action='store_true', required=False)
    
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()