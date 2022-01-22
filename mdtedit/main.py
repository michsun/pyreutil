import argparse
import re

from .utils import colored

link_name = "[\[]?[^\[^\]]+[\]]?"
link_url = "http[s]?://[^\)]+"
mdlink_regex = f"\[{link_name}]\({link_url}\)"
mdlink_parts_regex = f"\[({link_name})]\(({link_url})\)"

class MDTEdit:
    
    def __init__(self, text="", verbose=False):
        self.text : str = text
        self.verbose : bool = verbose
        
    def strip_markdown_links(self) -> str:
        """Returns the text with stripped markdown links replaced with the link name."""
        if self.verbose:
            print("\nLinks found: \n---")
            for match in re.findall(mdlink_regex, self.text):
                print(match)
            colored_print = re.sub(mdlink_parts_regex, colored(255,0,0,r'\1'), self.text)
            print("\nChanges made:\n---")
            print(colored_print)
        self.text = re.sub(mdlink_parts_regex, r'\1', self.text)
        return self.text
    
    def remove_extra_whitespaces(self) -> str:
        """Removes redundant whitespaces (leading, trailing, and spaces before a period, comma or bracket)."""
        if self.verbose:
            print("\nWhitespaces have been removed")
        self.text = re.sub('[ ]+', ' ', self.text.strip())
        self.text = re.sub('[ ]([,|.|\)])', r'\1', self.text)
        return self.text

    def remove_regex_matches(self, regex:str) -> str:
        """Removes regex matches in the given text."""
        if self.verbose:
            print("\nRegex matches to be removed:\n---")
            colored_print = re.sub(f'({regex})', colored(255,0,0,r'\1'), self.text)
            print(colored_print)
        self.text = re.sub(regex, '', self.text)
        return self.text


def from_file(filename: str) -> MDTEdit:
    """Creates a MDT object by reading a file"""
    f = open(filename, 'r')
    obj = MDTEdit(f.read())
    f.close()
    return obj

def run(args):
    if args.filename:
        file = from_file(args.filename)
        file.verbose = True
        
        if args.silence:
            file.verbose = False
            if not args.inplace:
                print("Warning: Changes have not been saved to file. Use '-i' to save changes inplace.")
        if args.remove_md_links:
            file.strip_markdown_links()
        if args.remove_whitespaces:
            file.remove_extra_whitespaces()
        if args.remove_regex:
            file.remove_regex_matches(args.remove_regex)
        if args.inplace:
            with open(args.filename, 'w') as f:
                f.write(file.text)

def main():
    """Process command line arguments and execute the given command.""" 
    parser = argparse.ArgumentParser(description="Markdown-Text editor command line utility.")
    
    parser.add_argument('-f', '--filename', help='filename to parse', type=str, required=True)
    parser.add_argument('-i', '--inplace', help='save changes to the existing file', action='store_true', required=False)
    parser.add_argument('-l', '--remove-md-links', help='removes markdown links and replaces it with the link name', action='store_true', required=False)
    parser.add_argument('-r', '--remove-regex', help='removes custom perl regex matches from the file', type=str, required=False)
    parser.add_argument('-w', '--remove-whitespaces', help='removes redundant whitespaces (leading, trailing, and spaces before a period or comma)', action='store_true', required=False)
    parser.add_argument('-s', '--silence', help='silences the output', action='store_true', required=False)
    
    args = parser.parse_args()
    run(args)

if __name__ == "__main__":
    main()