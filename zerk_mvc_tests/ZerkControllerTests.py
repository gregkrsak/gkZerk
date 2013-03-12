# Filename: ZerkControllerTests.py
# Author: Greg M. Krsak
# License: MIT
# Contact: greg.krsak@gmail.com
#
# Zerk is an Interactive Fiction (IF) style interpreter, inspired by Infocom's
# Zork series. Zerk allows the use of custom maps, which are JSON-formatted.
#
# This file contains the tests for the MVC controller.
#

import unittest
import io

# Ref: http://stackoverflow.com/questions/1054271/how-to-import-a-python-class-that-is-in-a-directory-above
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from zerk_mvc.ZerkModel import ZerkModel
from zerk_mvc.ZerkController import ZerkController


class ZerkControllerTests(unittest.TestCase):
  
    """
    Tests for the MVC controller.
    """
  
    def setUp(self):
        # Define a mock input
        self.mockInput = io.StringIO('mock input')
        # Create a mock model instance
        self.mockModel = ZerkModel({})
        # Create a controller instance
        self.controller = ZerkController(self.mockInput, self.mockModel)


    def test_CanReceiveInputFromStream(self):
        """
        Can receive waiting input.
        """
        self.assertEqual('mock input', self.controller.waitForInput())
