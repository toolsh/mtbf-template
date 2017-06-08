"""Test Case module."""

from __future__ import absolute_import
from __future__ import division

import os
import importlib
import yaml

from . import uia 

def get(testcase, device_name):
    """Retrieve TC object."""
    dev = get_dev(device_name)
    adb = get_adb(device_name)
    testcase_module = importlib.import_module('lib.%s' % testcase.lower())
    testcase_object = getattr(testcase_module, testcase)
    return testcase_object(dev, adb, testcase, device_name)


