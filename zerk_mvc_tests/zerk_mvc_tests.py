#!/usr/bin/env python3
# Filename: zerk_mvc_tests.py
# Author: Greg M. Krsak
# License: MIT
# Contact: greg.krsak@gmail.com
#
# Zerk is an Interactive Fiction (IF) style interpreter, inspired by Infocom's
# Zork series. Zerk allows the use of custom maps, which are JSON-formatted.
#
# This file contains the unit tests and integration tests.
#

import unittest

# Unit tests
import ZerkModelTests
import ZerkViewTests
import ZerkControllerTests
import ZerkUserTests
# Integration tests
import ZerkIntegrationTests


# Unit tests (Model)
suite = unittest.TestLoader().loadTestsFromTestCase(ZerkModelTests.ZerkModelTests)
unittest.TextTestRunner(verbosity=2).run(suite)

# Unit tests (View)
suite = unittest.TestLoader().loadTestsFromTestCase(ZerkViewTests.ZerkViewTests)
unittest.TextTestRunner(verbosity=2).run(suite)

# Unit tests (Controller)
suite = unittest.TestLoader().loadTestsFromTestCase(ZerkControllerTests.ZerkControllerTests)
unittest.TextTestRunner(verbosity=2).run(suite)

# Unit tests (User)
suite = unittest.TestLoader().loadTestsFromTestCase(ZerkUserTests.ZerkUserTests)
unittest.TextTestRunner(verbosity=2).run(suite)

# Integration tests (Model, View, Controller, User)
suite = unittest.TestLoader().loadTestsFromTestCase(ZerkIntegrationTests.ZerkIntegrationTests)
unittest.TextTestRunner(verbosity=2).run(suite)
