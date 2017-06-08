"""Utility module."""

from __future__ import absolute_import
from __future__ import division

import os
import uiautomator

from . import log

def get_dev(device_name):
    """Get uiautomator device object."""
    serialno = os.environ.get(device_name)
    logger = logger('GETDEVICE')
    logger.info('%s @ %s', device_name, serialno)
    is_dev_connected(serialno)
    dev = uiautomator.Device(serialno)
    init_watchers(dev)
    return dev

def get_adb(device_name):
    """Get uiautomator adb object."""
    serialno = os.environ.get(device_name)
    adb = uiautomator.Adb(serialno)
    return adb

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


