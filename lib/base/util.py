"""Utility module."""

from __future__ import absolute_import
from __future__ import division

import functools
import importlib
import logging
import os
import random
import re
import string
import subprocess
import sys

import cv2
import uiautomator

import numpy
import psutil

from PIL import Image


def logger(tcname, devname='MAINRUN'):
    """Retrieve Python logger."""
    log = logging.getLogger(tcname)
    if not len(log.handlers):
        log.setLevel(logging.DEBUG)
        log_format = ' '.join(['%(asctime)s', ':', '[%(levelname)s]',
                               '[%(name)s]', '[%(devname)s]',
                               '[%(funcName)s]', '%(message)s'])
        log_formatter = logging.Formatter(log_format)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(log_formatter)
        log.addHandler(stream_handler)
        # file_handler = logging.FileHandler(log_dirpath, 'w')
        # file_handler.setLevel(logging.DEBUG)
        # file_handler.setFormatter(log_formatter)
        # log.addHandler(file_handler)
    return logging.LoggerAdapter(log, {'devname': devname})


def screendump_path():
    """Get the path to the screendump folder."""
    logpath = os.environ.get('LOG_PATH')
    if logpath is None:
        logpath = sys.path[0]
    dirpath = os.path.join(logpath, 'screendump')
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    return dirpath


def tempdump_path():
    """Get the path to the tempdump folder."""
    logpath = os.environ.get('LOG_PATH')
    if logpath is None:
        logpath = sys.path[0]
    dirpath = os.path.join(logpath, 'tempdump')
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    return dirpath


def res_path():
    """Get the path to the resources folder."""
    respath = os.path.join(sys.path[0], 'res')
    if not os.path.exists(respath):
        raise IOError('%s NOT FOUND.' % respath)
    return respath


def memoize(obj):
    """Memoize

    Citation - https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
    Description - Cache the returned object of a host function. If the  host
    function gets called at different call sites with the same argument, do not
    evaluate the body of the host function, just return the cached object.
    """
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        """Memoizer"""
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer


@memoize
def get_dev(devname):
    """Get uiautomator device object."""
    srl = os.environ.get(devname)
    log = logger('GETDEVICE')
    log.info('%s @ %s', devname, srl)
    is_dev_connected(srl)
    dev = uiautomator.Device(srl)
    init_watchers(dev)
    return dev


@memoize
def get_adb(devname):
    """Get uiautomator adb object."""
    srl = os.environ.get(devname)
    adb = uiautomator.Adb(srl)
    return adb


@memoize
def tcget(tcname, devname):
    """Retrieve TC object."""
    dev = get_dev(devname)
    adb = get_adb(devname)
    tcmd = importlib.import_module('lib.%s' % tcname.lower())
    tcob = getattr(tcmd, tcname)
    return tcob(dev, adb, tcname, devname)


def is_dev_connected(*args):
    """Check if all devices are attached."""
    proc = subprocess.Popen(
        'adb devices'.split(),
        stdout=subprocess.PIPE)
    output = proc.communicate()
    for arg in args:
        if arg not in output[0]:
            raise ValueError('Device NOT found.')


def uiauto_cleanup():
    """Stop UIAutomator & ADB server, and cleanup Python processes."""
    try:
        with open(os.devnull, 'w') as fnull:
            cmd = 'adb kill-server'
            proc = subprocess.Popen(cmd.split(), stdout=fnull, stderr=fnull)
            proc.communicate()
        crpid = str(os.getpid())
        for proc in psutil.process_iter():
            pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline'])
            pname = str(pinfo['name'])
            prcid = str(pinfo['pid'])
            pcmdl = str(pinfo['cmdline'])
            if ('python' in pname and
                    prcid != crpid and
                    'ami.py' not in pcmdl and
                    'arsserver.py' not in pcmdl):
                proc.kill()
    except BaseException:
        pass


def init_watchers(dev):
    """Initialize all the watchers."""

    dev.watchers.remove()

    dev.watcher('not_responding').when(
        textMatches='(?i).*%s.*' % re.escape('responding')
    ).click(textMatches='(?i).*%s.*' % re.escape('ok'))

    dev.watcher('unfortunately').when(
        textMatches='(?i).*%s.*' % re.escape('unfortunately')
    ).click(textMatches='(?i).*%s.*' % re.escape('ok'))

    dev.watcher('remind_me_later').when(
        textMatches='(?i).*%s.*' % re.escape('remind me later')
    ).click(textMatches='(?i).*%s.*' % re.escape('remind me later'))

    dev.watcher('pkginstaller').when(
        resourceIdMatches='(?i).*%s.*' % re.escape('permission_allow_button')
    ).click(textMatches='(?i).*%s.*' % re.escape('allow'))

    dev.watcher('radio').when(
        textMatches='(?i).*%s.*' % re.escape('Plug in Earphone')
    ).click(textMatches='(?i).*%s.*' % re.escape('Continue'))

    dev.watcher('compass').when(
        textMatches='(?i).*%s.*' % re.escape('Exit')
    ).when(
        resourceIdMatches='(?i).*%s.*' % re.escape('alertTitle')
    ).click(text='Yes')

    dev.watcher('internet_not_available').when(
        textMatches='(?i).*%s.*' % re.escape('Internet not available via')
    ).click(textMatches='(?i).*%s.*' % re.escape('Cancel'))

    dev.watcher('smart_suite').when(
        textMatches='(?i).*%s.*' % re.escape('Exit')
    ).click(text='OK')

    dev.watcher('retransmit').when(
        textMatches='(?i).*%s.*' % re.escape('Re-transmit')
    ).click(textMatches='(?i).*%s.*' % re.escape('OK'))

    txt = 'Update apps automatically when on Wi-Fi?'
    dev.watcher('storefront-update').when(
        textMatches='(?i).*%s.*' % re.escape(txt)
    ).click(textMatches='(?i).*%s.*' % re.escape('Not now'))

    txt = 'Your message will be discarded'
    dev.watcher('msg-discard').when(
        textMatches='(?i).*%s.*' % re.escape(txt)
    ).click(textMatches='(?i).*%s.*' % re.escape('OK'))

    txt = 'Due to Connectivity Issue'
    dev.watcher('msg-connectivity-issue-direct-tv').when(
        textMatches='(?i).*%s.*' % re.escape(txt)
    ).click(textMatches='(?i).*%s.*' % re.escape('OK'))

    dev.watcher('ad1').when(
        textMatches='(?i).*%s.*' % re.escape('NO THANKS')
    ).click(textMatches='(?i).*%s.*' % re.escape('NO THANKS'))

    dev.watcher('storefront_skip').when(
        textMatches='(?i).*%s.*' % re.escape('Complete account setup')
    ).click(textMatches='(?i).*%s.*' % re.escape('SKIP'))

    dev.watchers.run()


def _gen_id_watcher(dev, id1, id2):
    """Generate a watcher that matches ID."""
    name = ''.join(random.sample(string.ascii_letters, 12))
    dev.watcher(name).when(resourceId=id1).click(resourceId=id2)


def _gen_id_txt_watcher(dev, id1, txt1):
    """Generate a watcher to check for ID and then click on UI obj by text."""
    name = ''.join(random.sample(string.ascii_letters, 12))
    txt1 = '(?i)%s.*' % re.escape(txt1)
    dev.watcher(name).when(resourceId=id1).click(textMatches=txt1)


def img_comp(bip, sip):
    """
    bip = Big image path.
    sip = Small image path.
    Guess where the small image sip is in the big image bip, crop the guessed
    location from the big image bip, and then compare the cropped image to the
    small image sip.
    """
    # pylint: disable=I0011,E1101
    res = _img_comparison(bip, sip)
    # log = logger('IMGCOMP')
    # log.info('Similarity level: {:.2f}%'.format(float(res) * 100.0))
    return res > numpy.float64(0.976)


def _img_search(bip, sip):
    """Search for sip on bip.

    Citation: Adapted from code on http://stackoverflow.com/
    """
    # pylint: disable=I0011,E1101
    shot = cv2.imread(bip, 0).copy()
    imgfind = cv2.imread(sip, 0)
    width, height = imgfind.shape[:: -1]
    mtempl = cv2.matchTemplate(shot, imgfind, cv2.TM_CCOEFF_NORMED)
    _, _, _, tleft = cv2.minMaxLoc(mtempl)
    bright = (tleft[0] + width, tleft[1] + height)
    cropshot = shot[tleft[1]: bright[1], tleft[0]: bright[0]]
    img1 = Image.fromarray(cropshot)
    img2 = Image.fromarray(imgfind)
    return (img1, img2)


def _img_comparison(bip, sip):
    """Compare sip to bip.

    Citation: Code adapted from http://stackoverflow.com/
    """
    # pylint: disable=I0011,E0632
    img1, img2 = _img_search(bip, sip)
    img1.save(bip.split('.')[0] + '_img1_cropped.png', 'PNG')
    img2.save(bip.split('.')[0] + '_img2_imgtofind.png', 'PNG')
    vectors = []
    norms = []
    for image in [img1, img2]:
        vector = []
        for pixel_tuple in image.getdata():
            vector.append(numpy.average(pixel_tuple))
        vectors.append(vector)
        norms.append(numpy.linalg.norm(vector, 2))
    vecta, vectb = vectors
    a_norm, b_norm = norms
    return numpy.dot(vecta / a_norm, vectb / b_norm)


def genid(pkg, uiid):
    """Given UI object pkg and ui res id generate complete resID"""
    return ''.join([pkg, ':id/', uiid])


def pze(value, singular):
    """Pluralize"""
    return singular if value == 1 else singular + 's'


def reqrate(tcname):
    """Return the pass rate for a test case."""
    reqrates = {
        'Telephony': .95,
        'Messaging': .95,
        'Email': .95,
        'Browser': .95,
        'Storefront': .95,
        'PIM': .99,
        'MultiMedia': .95,
        'MultiTasking': .99,
        'MenuNavigation': .99,
        'WiFi': .99,
        'NFC': .99,
        'VoLTE': .95,
        'SMSOverIP': .95,
    }
    return reqrates[tcname]


def repunct(line):
    """Replace punctuations with delimiter.

    Citation: Code adapted from http://stackoverflow.com/
    """
    puncts = string.punctuation
    spaces = ' ' * len(string.punctuation)
    ttable = string.maketrans(puncts, spaces)
    line = ''.join(str(line).strip().translate(ttable).split())
    return line
