import unittest

from pyreutil.pyreutil import *

class TestReUtil(unittest.TestCase):
    
    def test_search_and_replace(self):
        regex_with_groups = "\[([\[]?[^\[^\]]+[\]]?)]\((http[s]?://[^\)]+)\)"
        sample_text = "In 1913,  [Ernst Zermelo](https://en.wikipedia.org/wiki/Ernst_Zermelo)  published *Über eine Anwendung der Mengenlehre auf die Theorie des Schachspiels* (*On an Application of Set Theory to the Theory of the Game of Chess*), which proved that the optimal chess strategy is  [strictly determined](https://en.wikipedia.org/wiki/Strictly_determined_game) . This paved the way for more general theorems. [[4]](https://en.wikipedia.org/wiki/Game_theory#cite_note-4) "
        
        self.assertRaises(TypeError, ReUtil().search_and_replace, regex=regex_with_groups, text=sample_text, replace="link", group=1)
        self.assertRaises(TypeError, ReUtil().search_and_replace, regex=regex_with_groups, text=sample_text)
        
        expected1 = "In 1913,  Ernst Zermelo  published *Über eine Anwendung der Mengenlehre auf die Theorie des Schachspiels* (*On an Application of Set Theory to the Theory of the Game of Chess*), which proved that the optimal chess strategy is  strictly determined . This paved the way for more general theorems. [4] "
        expected2 = "In 1913,  [link]  published *Über eine Anwendung der Mengenlehre auf die Theorie des Schachspiels* (*On an Application of Set Theory to the Theory of the Game of Chess*), which proved that the optimal chess strategy is  [link] . This paved the way for more general theorems. [link] "
        
        result1 = ReUtil().search_and_replace(regex_with_groups, sample_text, group=1)
        result2 = ReUtil().search_and_replace(regex_with_groups, sample_text, replace="[link]")
        self.assertEquals(expected1, result1)
        self.assertEquals(expected2, result2)
        
    # TODO
    def test_search(self):
        pass
    
    # TODO
    def test_remove(self):
        pass


class TestText(unittest.TestCase):
    
    def test_init(self):
        filename_sample = ['examples/sample1.md', 'examples/sample2.md', 'examples/sample3.txt']
        text_sample = [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum venenatis molestie quam, eu sodales lectus.",
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a dolor elit. Cras pellentesque erat eros, eu volutpat lacus fermentum id. Integer commodo dui ut placerat.",
            "Donec sed blandit nisl. Aenean blandit erat sit amet urna viverra hendrerit. Sed luctus nulla sit."
        ]
        self.assertRaises(TypeError, Text, text=text_sample, filenames=filename_sample)
        pass
    
    # TODO
    def test_strip_markdown_links(self):
        pass
    
    # TODO
    def test_remove_extra_whitespaces(self):
        pass


class TestPathnames(unittest.TestCase):
    
    # TODO
    def test_init(self):
        sample_pathnames = ['examples/sample1.md', 'examples/sample2.md', 'examples/sample3.txt']
        
        self.assertRaises(TypeError, Pathnames, path='doesnotexist.txt', pathnames=sample_pathnames)
        pass
   
if __name__ == "__main__":
    unittest.main()
        