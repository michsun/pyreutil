import argparse
import re
import os

from typing import List

from .utils import mutually_exclusive

class ReUtil:
    
    def __init__(self, verbose : bool = False):
        self.verbose : bool = verbose
        self.color_search : List[int] = [255,0,0]
        self.color_replace : List[int] = [0,255,0]
    
    @mutually_exclusive('replace', 'group')
    def search_and_replace(self, regex : str, text : str, replace : str = None, group : int = 0) -> str:
        """Searches through text and replaces with string."""
        if replace is None:
            return re.sub(regex, lambda m: m.group(group), text) 
        return re.sub(regex, replace, text) 
    
    def search(self, regex: str, text : str) -> int:
        """Returns the number of matches found in the text."""
        count = len(re.findall(regex, text))
        return count 
    
    def remove(self, regex : str, text : str) -> str:
        """Removes matches from a given text."""
        return re.sub(regex, '', text) 
    
    def save_changes(self, mode : str) -> None:
        modes = ['inplace', 'copy']
        if mode not in modes:
            raise Exception("Error: The mode {} is not valid. Input 'inplace' or 'copy'.")
        
    def colored_search(self, regex : str, text : str) -> str:
        """Returns string with regex matches colored."""
        return re.sub(regex, lambda m: self._colored(self.color_search, m.group()), text)
    
    @mutually_exclusive('replace', 'group')
    def colored_replace(self, regex : str, text : str, replace : str = None, group : int = 0) -> str:
        """Returns a string with the regex substitutes colored."""
        if group > 0:
            return re.sub(regex, lambda m: self._colored(self.color_replace, m.group(group)), text)
        return re.sub(regex, self._colored(self.color_replace, replace), text)
            
    def _colored(self, values : List[int], text : str) -> str:
        """Returns a colored version of the string."""
        r, g, b = values[0], values[1], values[2]
        return "\033[38;2;{};{};{}m{}\033[m".format(r, g, b, text)


class Text(ReUtil):
    
    @mutually_exclusive('text', 'filenames')
    def __init__(self, text : List[str]=[], filenames : List[str] = [], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_filenames : List[str] = filenames
        self.original_text : List[str] = text
        self.text : List[str] = text
        if len(filenames) > 0:
            self.original_filenames = iterate_files(filenames) if isdir(filenames) else [ filenames ]
            for filepath in self.original_filenames:
                with open(filepath, 'r') as f:
                    self.original_text.append(f.read())
            self.text = self.original_text
    
    def search_and_replace(self, regex : str, replace : str) -> List[str]:
        new_text = []
        for txt in self.text:
            new = super().search_and_replace(regex, txt, replace=replace)
            if self.verbose:
                colored_search = self.colored_search(regex, txt)
                colored_replace = self.colored_replace(regex, txt, replace=replace)
                print(colored_search)
                print(colored_replace)
            new_text.append(new)
        self.text = new_text
        return self.text
    
    def search(self, regex : str) -> int:
        count = 0
        for txt in self.text:
            searches = super().search(regex, txt)
            if self.verbose:
                colored_search = self.colored_search(regex, txt)
                print(colored_search)
            count += searches
        print("{} matches found".format(count))
        return count
    
    def remove(self, regex : str) -> List[str]:
        """Returns a list of texts with the regex matches removed"""
        new_text = []
        if self.verbose:
            print("Removing searches...")
        for i, txt in enumerate(self.text):
            if self.verbose and self.original_filenames:
                print("Searching for matches to remove in '{}'...".format(self.original_filenames[i]))
            new = super().remove(regex, txt)
            count = super().search(regex, txt)
            if self.verbose:
                if count == 0:
                    print("No matches to '{}' were found.".format(regex))
                else:
                    colored_search = self.colored_search(regex, txt)
                    print(colored_search)
                    print("  {} matches to be removed were found".format(count))
            new_text.append(new)
        self.text = new_text
        return self.text
    
    def save_changes(self, mode : str = 'inplace') -> None:
        """Saves content changes to original files, or to a copy of the file(s)."""
        super().save_changes(mode)
        if len(self.original_filenames) != len(self.text):
            raise Exception("Error! Length of original and modified files are not the same.")
        if mode == 'inplace':
            for i in range(0, len(self.original_text)):
                with open(self.original_filenames[i], 'w') as f:
                    f.write(self.text[i])
        # TODO: Copys text to new files
        if mode == 'copy':
            pass
    
    # CUSTOM TEXT FUNCTIONS
    
    # TODO: Improve method removing whitespaces.
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
            print("Stripping markdown links in text...")
        for i, txt in enumerate(self.text):
            new = super().search_and_replace(mdlink_parts_regex, txt, group=1)
            count = ReUtil().search(mdlink_regex, txt)
            if self.verbose:
                if self.original_filenames:
                    print("Searching '{}'...".format(self.original_filenames[i]))
                if count == 0:
                    print("No links were found.")
                else:
                    colored_search = self.colored_search(mdlink_parts_regex, txt)
                    colored_replace = self.colored_replace(mdlink_parts_regex, txt, group=1)
                    print(colored_search)
                    print("  {} link(s) found".format(count))
                    print(colored_replace,'\n')
            new_text.append(new)
        self.text = new_text
        return self.text


class Pathnames(ReUtil):
    
    # TODO: rename class
    @mutually_exclusive('path', 'pathnames')
    def __init__(self, path : str = "", pathnames : List[str] = [], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_pathnames : List[str] = pathnames
        self.pathnames : List[str] = pathnames
        if path is not None:
            self.original_pathnames = iterate_files(path) if isdir(path) else [path]
            self.pathnames = self.original_pathnames
        
    def search_and_replace(self, regex : str, replace : str) -> List[str]:
        """Substitutes regex searches with a string replacement, returning a list of new pathnames."""
        new_names = []
        files_changed = 0
        for path in self.pathnames:
            head, tail = os.path.split(path)
            tail, ext = os.path.splitext(tail)
            new_tail = super().search_and_replace(regex, tail, replace=replace)
            if new_tail != tail:
                files_changed += 1
            colored_search = os.path.join(head, self.colored_search(regex,tail)+ext)
            colored_replace = os.path.join(head, self.colored_replace(regex,tail,replace=replace)+ext)
            if self.verbose:
                if colored_search == colored_replace:
                    print(colored_search)
                else:
                    print("{} ==> {}".format(colored_search, colored_replace))
            new_names.append(os.path.join(head, new_tail+ext))
        if self.verbose:
            print("  {}/{} filenames changed.".format(files_changed, len(self.pathnames)))
        self.pathnames = new_names
        return self.pathnames
    
    def search(self, regex : str) -> int:
        """Returns number of regex matches in the names."""
        count = 0
        for path in self.pathnames:
            head, tail = os.path.split(path)
            tail, ext = os.path.splitext(tail)
            # matches, colored_search = super().search(regex, tail)
            matches = super().search(regex, tail)
            if self.verbose:
                colored_search = self.colored_search(regex, tail)
                print(os.path.join(head,colored_search+ext))
            count += matches
        if self.verbose:
            print("{} matches found in {} filename(s).".format(count, len(self.pathnames)))
        return count
    
    def remove(self, regex : str) -> List[str]:
        """Returns a list of new pathnames with the regex search removed."""
        new_names = []
        for path in self.pathnames:
            head, tail = os.path.split(path)
            tail, ext = os.path.splitext(tail)
            # tail, colored_search = super().remove(regex, tail)
            tail = super().remove(regex, tail)
            if self.verbose:
                print("To be removed...")
                colored_search = self.colored_search(regex, tail)
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
    

def isdir(fullpath: str) -> bool:
    """Returns true if is a file, and false if otherwise (a directory)."""
    try:
        if os.path.exists(fullpath):
            if os.path.isdir(fullpath):
                return True
            return False
    except FileNotFoundError:
        print(f'{fullpath} does not exist.')


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
    parser = argparse.ArgumentParser(description="Text and filenames regex command line utility.")
    
    # Two Modes
    core = parser.add_mutually_exclusive_group()
    core.add_argument('-t', '--textfiles', help='text source', type=str, required=False)
    core.add_argument('-f', '--filenames', help='filenames source', type=str, required=False)
    # Global commands
    parser.add_argument('-i', '--inplace', help='save changes to the existing file', action='store_true', required=False)
    parser.add_argument('-r', '--replace', help='string to replace searches with. Must be used with -s --search', type=str, required=False)
    parser.add_argument('-rm', '--remove', help='removes custom perl regex matches from the file', type=str, required=False)
    parser.add_argument('-s', '--search', help='regex string to search for based on the given input', type=str, required=False)
    parser.add_argument('-si', '--silence', help='silences the output', action='store_true', required=False)
    # Exclusive to modifying contents
    parser.add_argument('-l', '--remove-md-links', help='removes markdown links and replaces it with the link name', action='store_true', required=False)
    parser.add_argument('-w', '--remove-whitespaces', help='removes redundant whitespaces (leading, trailing, and spaces before a period or comma)', action='store_true', required=False)
    
    for g in parser._action_groups:
        g._group_actions.sort(key=lambda x:x.dest)
    
    args = parser.parse_args()
    run(args)

if __name__ == "__main__":
    main()