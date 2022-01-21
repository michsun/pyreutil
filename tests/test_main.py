import unittest
from mdtedit.main import *

class TestMain(unittest.TestCase):
    
    def test_remove_extra_whitespaces(self):
        test_cases = [
            "Firstname    Lastname",
            "   leading and trailing   whitespaces   ",
            "   words ,     end of sentence .   "
        ]
        expected = [
            "Firstname Lastname",
            "leading and trailing whitespaces",
            "words, end of sentence."
        ]
        
        for i, case in enumerate(test_cases):
            result = remove_extra_whitespaces(case)
            self.assertEquals(result, expected[i])
    
    def test_strip_markdown_links(self):
        test_cases = [
            "[Link name](https://url.com/123#123)",
            "[[Double link]](http://randomurl.com)",
            "Lorem ipsum [Dolor](https://url.com/?-qwerty) voluptatem sequi nesciunt [Accusantium](https://another url.com) iure reprehenderit."
        ]
        expected = [
            "Link name",
            "[Double link]",
            "Lorem ipsum Dolor voluptatem sequi nesciunt Accusantium iure reprehenderit."
        ]
        for i, case in enumerate(test_cases):
            result = strip_markdown_links(case)
            self.assertEquals(result, expected[i])
            
    def test_remove_regex_matches(self):
        test_cases = [
            {'text': "surrounding [[24]] text",
             'regex': "\[\[[0-9]*\]\] " }
        ]
        expected = [
            "surrounding text"
        ]
        for i, case in enumerate(test_cases):
            result = remove_regex_matches(text=case['text'], regex=case['regex'])
            self.assertEquals(result, expected[i])
    
if __name__ == "__main__":
    unittest.main()
        