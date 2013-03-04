import unittest
import io

# Ref: http://stackoverflow.com/questions/1054271/how-to-import-a-python-class-that-is-in-a-directory-above
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from zerk_mvc.ZerkModel import ZerkModel
from zerk_mvc.ZerkView import ZerkView
from zerk_state import ZerkGameState


class ZerkViewTests(unittest.TestCase):
    
    def setUp(self):
        # Create a mock model instance
        self.mockModel = ZerkModel({})
        # Define the local console
        self.localOutput = sys.stdout
        # Create a view instance
        self.view = ZerkView(self.localOutput, self.mockModel)
    

    def test_CanDetermineCorrectIndefiniteArticleForWord(self):
        a = 'a'
        an = 'an'
        words = { a: [ 'sausage', 'taco' ], an: [ 'apple', 'orange' ] }
        for word in (words[a]):
            self.assertEqual(self.view.indefiniteArticleForWord(word), a)
        for word in (words[an]):
            self.assertEqual(self.view.indefiniteArticleForWord(word), an)
    

    def test_CanShowOutput(self):
        self.view.buffer.write('mock output\n')
        self.view.output.write(self.view.buffer.getvalue())
