import argparse
import re
import os

from typing import List

from .utils import colored, mutually_exclusive

class ReUtil:
    
    def __init__(self, verbose : bool = False):
        self.verbose : bool = verbose
        self.color_search : List[int] = [255,0,0]
        self.color_replace : List[int] = [0,255,0]
    
    @mutually_exclusive('replace', 'group')
    def search_and_replace(self, regex : str, text : str, replace : str = None, group : int = 0) -> tuple:
        """Searches through text and replaces with string."""
        search_text = ""
        replace_text = ""
        if self.verbose:
            search_text = re.sub(regex, lambda m: self.colored(self.color_search, m.group()), text)
            if replace is None:
                replace_text = re.sub(regex, lambda m: self.colored(self.color_replace, m.group(group)), text)
            else:
                replace_text = re.sub(regex, self.colored(self.color_replace, replace), text)
        if replace is None:
            return re.sub(regex, lambda m: m.group(group), text), search_text, replace_text
        return re.sub(regex, replace, text), search_text, replace_text
    
    def search(self, regex: str, text : str) -> tuple:
        """Returns the number of matches found in the text."""
        count = len(re.findall(regex, text))
        colored_search = ""
        if self.verbose:
            colored_search = re.sub(regex, lambda m: self.colored(self.color_search, m.group()), text)
        return count, colored_search
    
    def remove(self, regex : str, text : str) -> tuple:
        """Removes matches from a given text."""
        colored_search = ""
        if self.verbose:
            colored_search = re.sub(f'({regex})', colored(255,0,0,r'\1'), text)
        return re.sub(regex, '', text), colored_search
    
    def save_changes(self, mode : str) -> None:
        modes = ['inplace', 'copy']
        if mode not in modes:
            raise Exception("Error: The mode {} is not valid. Input 'inplace' or 'copy'.")
            
    def colored(self, values : List[int], text : str) -> str:
        """Returns a colored version of the string."""
        # return "\033[38;2;{};{};{}m{}\033[38;2;255;255;255m".format(r, g, b, text)
        r, g, b = values[0], values[1], values[2]
        return "\033[38;2;{};{};{}m{}\033[m".format(r, g, b, text)


class Text(ReUtil):
    
    @mutually_exclusive('text', 'filenames')
    def __init__(self, text : List[str]=[], filenames : List[str] = [], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_filenames = filenames
        self.original_text = text
        self.text = text
        if len(filenames) > 0:
            self.original_filenames = iterate_files(filenames) if isdir(filenames) else [ filenames ]
            for filepath in self.original_filenames:
                with open(filepath, 'r') as f:
                    self.original_text.append(f.read())
            self.text = self.original_text
    
    def search_and_replace(self, regex : str, replace : str) -> List[str]:
        new_text = []
        for txt in self.text:
            new, colored_search, colored_replace = super().search_and_replace(regex, txt, replace=replace)
            if self.verbose:
                print(colored_search)
                print(colored_replace)
            new_text.append(new)
        self.text = new_text
        return self.text
    
    def search(self, regex : str) -> int:
        count = 0
        for txt in self.text:
            searches, colored_search = super().search(regex, txt)
            if self.verbose:
                print(colored_search)
            count += searches
        print("{} matches found".format(count))
        return count
    
    def remove(self, regex : str) -> List[str]:
        """Returns a list of texts with the regex matches removed"""
        new_text = []
        if self.verbose:
            print("Remving the following searches...")
        for i, txt in enumerate(self.text):
            new, colored_search = super().remove(regex, txt)
            if self.verbose:
                if self.original_filenames:
                    print("Searches to be removed in '{}'...".format(self.original_filenames[i]))
                print(colored_search,'\n')
            new_text.append(new)
        self.text = new_text
        return self.text
    
    def save_changes(self, mode : str = 'inplace') -> None:
        """Saves content changes to original files, or to a copy of the file(s)."""
        super().save_changes(mode)
        if len(self.original_filenames) != len(self.text):
            raise Exception("Error! Length of original and modified files are not the same.")
        # TODO: Saves change to the original files
        if mode == 'inplace':
            for i in range(0, len(self.original_text)):
                with open(self.original_filenames[i], 'w') as f:
                    f.write(self.text[i])
        # TODO: Copys text to new files
        if mode == 'copy':
            pass
    
    # CUSTOM TEXT FUNCTIONS
    
    # TODO: Method of counting whitespaces.
    def remove_extra_whitespaces(self) -> str:
        """Removes redundant whitespaces (leading, trailing, and spaces before a period, comma or bracket)."""
        if self.verbose:
            print("Removing whitespaces...")
        for txt in self.text:
            txt = re.sub('[ ]+', ' ', txt.strip())
            txt = re.sub('[ ]([,|.|\)])', r'\1', txt)
        return self.text
    
    def strip_markdown_links(self) -> List[str]:
        """Returns the text with stripped markdown links replaced with the link name."""
        link_name = "[\[]?[^\[^\]]+[\]]?"
        link_url = "http[s]?://[^\)]+"
        mdlink_regex = f"\[{link_name}]\({link_url}\)"
        mdlink_parts_regex = f"\[({link_name})]\(({link_url})\)"
        
        new_text = []
        if self.verbose:
            print("Finding and stripping markdown links in text...")
        for i, txt in enumerate(self.text):
            new, colored_search, colored_replace = super().search_and_replace(mdlink_parts_regex, txt, group=1)
            count, _ = ReUtil().search(mdlink_regex, txt)
            if self.verbose:
                if self.original_filenames:
                    print("Searching '{}'...".format(self.original_filenames[i]))
                print(colored_search)
                print("  {} link(s) found".format(count))
                print(colored_replace,'\n')
            new_text.append(new)
        self.text = new_text
        return self.text
    

class Pathnames(ReUtil):
    
    # TODO: rename 'pathnames' to 'filepaths'
    @mutually_exclusive('path', 'pathnames')
    def __init__(self, path : str = None, pathnames : List[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_pathnames = pathnames
        self.pathnames = pathnames
        if path is not None:
            self.original_pathnames = iterate_files(path) if isdir(path) else [path]
            self.pathnames = self.original_pathnames
        
    def search_and_replace(self, regex : str, replace : str) -> List[str]:
        """Substitutes regex searches with a string replacement, returning a list of new pathnames."""
        new_names = []
        for path in self.pathnames:
            head, tail = os.path.split(path)
            tail, ext = os.path.splitext(tail)
            tail, colored_search, colored_replace = super().search_and_replace(regex, tail, replace=replace)
            colored_search = os.path.join(head, colored_search+ext)
            colored_replace = os.path.join(head, colored_replace+ext)
            if self.verbose:
                if colored_search == colored_replace:
                    print(colored_search)
                else:
                    print("{} ==> {}".format(colored_search, colored_replace))
            new_names.append(os.path.join(head, tail+ext))
        self.pathnames = new_names
        return self.pathnames
    
    def search(self, regex : str) -> int:
        """Returns number of regex matches in the names."""
        count = 0
        for path in self.pathnames:
            head, tail = os.path.split(path)
            tail, ext = os.path.splitext(tail)
            matches, colored_search = super().search(regex, tail)
            if self.verbose:
                print(os.path.join(head,colored_search+ext))
            count += len(matches)
        print("{} matches found in {} filename(s).".format(count, len(self.pathnames)))
        return count
    
    def remove(self, regex : str) -> List[str]:
        """Returns a list of new pathnames with the regex search removed."""
        new_names = []
        for path in self.pathnames:
            head, tail = os.path.split(path)
            tail, ext = os.path.splitext(tail)
            tail, colored_search = super().remove(regex, tail)
            if self.verbose:
                print("To be removed...")
                print(os.path.join(head, colored_search+ext))
            new_names.append(os.path.join(head,tail+ext))
        self.pathnames = new_names
        return self.pathnames
    
    def save_changes(self, mode : str = 'inplace') -> None:
        """Saves the filename changes inplace (renames input paths), or creates a copy."""
        super().save_changes(mode)
        if len(self.original_pathnames) != len(self.pathnames):
            raise Exception("Error! Length of original and modified filenames are not the same.")
        if self.verbose:
            print("Saving changes inplace...")
        if mode is 'inplace':
            for i in range(0, len(self.original_pathnames)):
                os.rename(self.original_pathnames[i], self.pathnames[i])
        
        if mode is 'copy':
            # TODO: implement copy method
            pass
    

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
        texts = Text(filenames=args.textfiles, verbose=not args.silence)
        # Built-in regex functions
        if args.remove_md_links:
            texts.strip_markdown_links()
        if args.remove_whitespaces:
            texts.remove_extra_whitespaces()
        # Core functions
        if args.remove:
            texts.remove(args.remove)
        if args.replace and not args.search:
            raise Exception("No search input has been given to replace.")
        if args.search and not args.replace:
            texts.search(args.search)
        if args.search and args.replace:
            texts.search_and_replace(args.search, args.replace)
        if not args.inplace:
            print("Warning: Changes have not been saved. Use -i or --inplace to save changes permanently.")
        if args.inplace:
            texts.save_changes()
    
    if args.filenames:
        paths = Pathnames(path=args.filenames, verbose=not args.silence)
        if args.remove:
            paths.remove(args.remove)
        if args.replace and not args.search:
            raise Exception("No search input has been given to replace.")
        if args.search and not args.replace:
            paths.search(args.search)
        if args.search and args.replace:
            paths.search_and_replace(args.search, args.replace)
            if not args.inplace:
                print("Warning: Changes have not been saved. Use -i or --inplace to save changes permanently.")
        if args.inplace:
            paths.save_changes()

def main() -> None:
    """Process command line arguments and execute the given command.""" 
    parser = argparse.ArgumentParser(description="Markdown-Text editor command line utility.")
    
    # Two Modes
    # TODO: Modify to mutually exclusive arguments
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