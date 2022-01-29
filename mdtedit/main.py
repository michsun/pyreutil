import argparse
import re
import os

from typing import List

from .utils import colored

link_name = "[\[]?[^\[^\]]+[\]]?"
link_url = "http[s]?://[^\)]+"
mdlink_regex = f"\[{link_name}]\({link_url}\)"
mdlink_parts_regex = f"\[({link_name})]\(({link_url})\)"

class ReUtil:
    def __init__(self, verbose=False):
        self.verbose : bool = verbose
        self.color0 : List[int] = [255,0,0]
        self.color1 : List[int] = [0,255,0]
    
    def search_and_replace(self, regex : str, replace : str, text : str) -> str:
        """Searches through text and replaces with string."""
        if self.verbose:
            search_text = re.sub(regex, lambda m: self.colored(self.color0, m.group()), self.text)
            replace_text = re.sub(regex, self.colored(self.color1, replace), self.text)
            print(search_text)
            print(replace_text)
        return re.sub(regex, replace, self.text)
    
    def search(self, regex: str, text : str) -> int:
        """Returns the number of matches found in the text."""
        count = len(re.findall(regex, text))
        if self.verbose:
            colored_search = re.sub(regex, lambda m: self.colored(self.color0, m.group()), text)
            print(colored_search)
        return count
    
    def remove(self, regex : str, text : str) -> str:
        """Removes matches from a given text."""
        if self.verbose:
            print("Regex matches to be removed...")
            colored_search = re.sub(f'({regex})', colored(255,0,0,r'\1'), self.text)
            print(colored_search, '\n')
        return re.sub(regex, '', text)
            
    def colored(self, values : List[int], text : str) -> str:
        """Returns a colored version of the string."""
        # return "\033[38;2;{};{};{}m{}\033[38;2;255;255;255m".format(r, g, b, text)
        r, g, b = values[0], values[1], values[2]
        return "\033[38;2;{};{};{}m{}\033[m".format(r, g, b, text)

class MDTEdit:
    
    def __init__(self, text="", verbose=False, *args, **kwargs):
        self.text : str = text
        self.verbose : bool = verbose
    
    # Main function
    def search_and_replace_text(self, regex : str, replace : str) -> str:
        """Searches through regex and replaces"""
        if self.verbose:
            search_text = re.sub(regex, lambda m: colored(255,0,0,m.group()), self.text)
            replace_text = re.sub(regex, colored(0,255,0,replace), self.text)
            print(search_text)
            print(replace_text)
        new_text = re.sub(regex, replace, self.text)
        return new_text
    
    # Main function
    def remove_regex_matches(self, regex:str) -> str:
        """Removes regex matches in the given text."""
        if self.verbose:
            print("Regex matches to be removed...")
            colored_print = re.sub(f'({regex})', colored(255,0,0,r'\1'), self.text)
            print(colored_print, '\n')
        self.text = re.sub(regex, '', self.text)
        return self.text
    
    # Custom function
    def remove_extra_whitespaces(self) -> str:
        """Removes redundant whitespaces (leading, trailing, and spaces before a period, comma or bracket)."""
        if self.verbose:
            print("Removing whitespaces...")
        self.text = re.sub('[ ]+', ' ', self.text.strip())
        self.text = re.sub('[ ]([,|.|\)])', r'\1', self.text)
        return self.text
    
    # Custom/saved regex function
    def strip_markdown_links(self) -> str:
        """Returns the text with stripped markdown links replaced with the link name."""
        if self.verbose:
            search_text = re.sub(mdlink_parts_regex, lambda m: colored(255,0,0,m.group()), self.text)
            replace_text = re.sub(mdlink_parts_regex, lambda m: colored(0,255,0,m.group(1)), self.text)
            print("Finding markdown links in text...")
            print(search_text, '\n')
            print(" {} link(s) found".format(len(re.findall(mdlink_parts_regex, self.text))))
            print(replace_text, '\n')
        self.text = re.sub(mdlink_parts_regex, r'\1', self.text)
        return self.text
    

####################
# FILENAME FUNCTIONS

def rename_files(old : List[str], new : List[str]) -> None: 
    """Renames files."""
    if len(old) != len(new):
        raise Exception("The length of the new and filenames are not the same.")
    for i, old_path in enumerate(old):
        os.rename(old_path, new[i])

def search_and_replace_filenames(filepaths: List[str], search : str, replace : str) -> List[str]:
    """Substitutes regex searches with a string replacement, returning a list of new filenames."""
    new_names = []
    for fullpath in filepaths:
        head, tail = os.path.split(fullpath)
        tail, ext = os.path.splitext(tail)
        # TODO: verbosity control
        colored_search = re.sub(search, lambda m: colored(255,0,0,m.group()), tail) + ext
        colored_replace = re.sub(search, colored(0,255,0,replace), tail) + ext
        if colored_search == colored_replace:
            print(colored_search)
        else:
            print("{} ==> {}".format(colored_search, colored_replace))
        
        tail = re.sub(search, replace, tail)
        new_names.append(os.path.join(head, tail+ext))
    return new_names

def search_filenames(filepaths: List[str], search : str) -> None:
    """Substitutes..."""
    count = 0
    for fullpath in filepaths:
        head, tail = os.path.split(fullpath)
        tail, ext = os.path.splitext(tail)
        count += len(re.findall(search, tail))
        colored_search = re.sub(search, lambda m: colored(255,0,0,m.group()), tail) + ext
        print(colored_search)
    print(f"{count} matches found in {len(filepaths)} filename(s).")

# Main functions
def from_file(filename: str) -> MDTEdit:
    """Creates a MDT object by reading a file"""
    f = open(filename, 'r')
    obj = MDTEdit(f.read())
    f.close()
    return obj

# CLI Function
def isdir(fullpath: str) -> bool:
    """Returns true if is a file, and false if otherwise (a directory)."""
    try:
        if os.path.exists(fullpath):
            if os.path.isdir(fullpath):
                return True
            return False
    except FileNotFoundError:
        print(f'{fullpath} does not exist.')

# CLI Function
def iterate_files(directory: str) -> List:
    """Iterates over the files in the given directory and returns a list of found files."""
    files = []
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        fullpath = os.path.join(directory, filename)
        if (isdir(fullpath)):
            files += iterate_files(fullpath)
        else:
            files.append(fullpath)
    return files


def run(args) -> None:
    if args.textfiles:
        text_files = [args.textfiles] if not isdir(args.textfiles) else iterate_files(args.textfiles)
        
        for filename in text_files:
            file = from_file(filename)
            file.verbose = True
            
            if args.silence:
                file.verbose = False
                if not args.inplace:
                    print("Warning: Changes have not been saved to file. Use '-i' to save changes inplace.")
            if args.remove_md_links:
                file.strip_markdown_links()
            if args.remove_whitespaces:
                file.remove_extra_whitespaces()
            if args.remove:
                file.remove_regex_matches(args.remove_regex)
            if args.inplace:
                with open(filename, 'w') as f:
                    f.write(file.text)
    if args.filenames:
        filepaths = [args.filenames] if not isdir(args.filenames) else iterate_files(args.filenames)
            
        if args.replace and not args.search:
            raise Exception("Unable to perform replacement as no search input has been given.")
        if args.search and not args.replace:
            search_filenames(filepaths, args.search)
        if args.search and args.replace:
            new_filepaths = search_and_replace_filenames(filepaths, args.search, args.replace)
            if not args.inplace:
                print("Warning : Changes have not been saved. Used -i or --inplace to save changes permanently.")
            if args.inplace:
                rename_files(filepaths, new_filepaths)
            

def main() -> None:
    """Process command line arguments and execute the given command.""" 
    parser = argparse.ArgumentParser(description="Markdown-Text editor command line utility.")
    
    # Two Modes
    parser.add_argument('-f', '--filenames', help='modifying the filenames', type=str, required=False)
    parser.add_argument('-t', '--textfiles', help='filename or a directory to parse', type=str, required=False)
    
    parser.add_argument('-i', '--inplace', help='save changes to the existing file', action='store_true', required=False)
    parser.add_argument('-l', '--remove-md-links', help='removes markdown links and replaces it with the link name', action='store_true', required=False)
    parser.add_argument('-r', '--replace', help='string to replace searches with. Must be used with -s --search', type=str, required=False)
    parser.add_argument('-rm', '--remove', help='removes custom perl regex matches from the file', type=str, required=False)
    parser.add_argument('-s', '--search', help='regex string to search for based on the given input', type=str, required=False)
    parser.add_argument('-si', '--silence', help='silences the output', action='store_true', required=False)
    parser.add_argument('-w', '--remove-whitespaces', help='removes redundant whitespaces (leading, trailing, and spaces before a period or comma)', action='store_true', required=False)
    
    args = parser.parse_args()
    run(args)

if __name__ == "__main__":
    main()