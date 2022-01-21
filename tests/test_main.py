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
        
if __name__ == "__main__":
    unittest.main()
        