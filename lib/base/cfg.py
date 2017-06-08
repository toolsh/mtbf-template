"""Configuration Module"""

import os
import sys

from ConfigParser import SafeConfigParser


def cget(section, key, vtype=None):
    """Retrieve values from common.ini."""
    ccfg = SafeConfigParser()
    ccfgpath = os.path.join(sys.path[0], 'cfg', 'common.ini')
    if not os.path.isfile(ccfgpath):
        raise IOError('%s NOT FOUND.' % ccfgpath)
    ccfg.read(ccfgpath)
    if vtype is None:
        return ccfg.get(section, key)
    elif vtype == 'bool':
        return ccfg.getboolean(section, key)
    elif vtype == 'float':
        return ccfg.getfloat(section, key)
    elif vtype == 'int':
        return ccfg.getint(section, key)


def sread():
    """Read the stability config file."""
    ttype = cget('Default', 'test_type')
    ntype = cget('Default', 'network_type')
    scfg = SafeConfigParser()
    scfgfile = '%s_%s.ini' % (ttype, ntype)
    scfgpath = os.path.join(sys.path[0], 'cfg', scfgfile)
    if not os.path.isfile(scfgpath):
        raise IOError('%s NOT FOUND.' % scfgpath)
    scfg.read(scfgpath)
    return scfg


def stui(section, key):
    """Get the total iterations for a test unit."""
    scfg = sread()
    return scfg.getint(section, key)


def stci(section):
    """Get the total iterations for a test case."""
    scfg = sread()
    return sum([int(x[1]) for x in scfg.items(section)])


def aget(section, key):
    """Return package name for app name."""
    acfg = SafeConfigParser()
    acfgpath = os.path.join(sys.path[0], 'cfg', 'apps.ini')
    if not os.path.isfile(acfgpath):
        raise IOError('%s NOT FOUND.' % acfgpath)
    acfg.read(acfgpath)
    return acfg.get(section, key)


def agetall(section):
    """Get dictionary key-value pairs of app names and/or package names."""
    acfg = SafeConfigParser()
    acfgpath = os.path.join(sys.path[0], 'cfg', 'apps.ini')
    if not os.path.isfile(acfgpath):
        raise IOError('%s NOT FOUND.' % acfgpath)
    acfg.read(acfgpath)
    return acfg.items(section)
