"""Common Library
"""

from __future__ import absolute_import
from __future__ import division

import os
import re
import time

from datetime import datetime

from . import cfg
from . import util


class Common(object):
    """Common Library

    Attributes:
        adb (uiautomator.Adb): UIAutomator Adb.
        dev (uiautomator.Device): UIAutomator Device.
        devname (str): MDEVICE or SDEVICE.
        log (logging): Python logging.
        pkgset (str): Package name for Settings.
        setact (str): Activity name for Settings.
        tcname (str): Name of the test case.
    """

    def __init__(self, dev, adb, tcname, devname):
        """Summary

        Args:
            dev (uiautomator.Device): UIAutomator Device.
            adb (uiautomator.Adb): UIAutomator Adb.
            tcname (str): Name of the test case.
            devname (str): MDEVICE or SDEVICE.
        """
        self.log = util.logger(tcname, devname)
        self.tcname = tcname
        self.devname = devname
        self.dev = dev
        self.adb = adb
        self.pkgset = 'com.android.settings'
        self.setact = '.TestingSettings'

    def _screendump_tcdir(self):
        """Create a directory in the screendump folder titled as the TC name.
        """
        sdpath = util.screendump_path()
        sdtcdir = os.path.join(sdpath, self.tcname.lower())
        if not os.path.exists(sdtcdir):
            os.makedirs(sdtcdir)
        return sdtcdir

    def _is_keyboard_shown(self):
        """Check if the keyboard is currently displayed on the screen.
        """
        cmd = 'shell dumpsys input_method'
        res = self.adb.cmd(*cmd.split()).communicate()[0]
        if 'mInputShown=true' in res:
            return True
        return False

    def _is_locked(self):
        """Check if the DUT's screen is currently locked.
        """
        regex = re.compile('mShowingLockscreen=(true|false)')
        cmd = 'shell dumpsys window policy'
        res = self.adb.cmd(*cmd.split()).communicate()[0]
        sres = regex.search(res)
        if sres is not None:
            if sres.group(1) == 'true':
                return True
        return False

    def _is_screen_on(self):
        """Check if the DUT's screen is current ON or OFF.
        """
        regex = re.compile('mScreenOnFully=(true|false)')
        cmd = 'shell dumpsys window policy'
        res = self.adb.cmd(*cmd.split()).communicate()[0]
        sres = regex.search(res)
        if sres is not None:
            if sres.group(1) == 'true':
                return True
        return False

    def _service_state(self):
        """Get the network service state of the DUT.
        """
        cmd = 'shell dumpsys telephony.registry'
        res = self.adb.cmd(*cmd.split()).communicate()[0]
        if 'mServiceState=0' in res:
            return 'InService'
        if 'mServiceState=1' in res:
            return 'OutOfService'
        if 'mServiceState=2' in res:
            return 'EmergencyOnly'
        if 'mServiceState=3' in res:
            return 'NetworkOff'
        return None

    def _data_state(self):
        """Get the state of the DUT's data connection.
        """
        cmd = 'shell dumpsys telephony.registry'
        res = self.adb.cmd(*cmd.split()).communicate()[0]
        if 'mDataConnectionState=0' in res:
            return 'Disconnected'
        if 'mDataConnectionState=1' in res:
            return 'Connecting'
        if 'mDataConnectionState=2' in res:
            return 'Connected'
        if 'mDataConnectionState=3' in res:
            return 'Suspended'
        return None

    def _is_network_valid(self, network):
        """Check if the specified network is valid.

        Args:
            network (str): 2G, 3G, LTE, 3GLTE, or 2G3GLTE.
        """
        valid = ['2G', '3G', 'LTE', '3GLTE', '2G3GLTE']
        if network in valid:
            return True
        self.log.warning('%s is an invalid network.', network)
        self.log.warning('Use one of the following network types: %s', valid)
        return False

    def _network_phoneinfo_view(self):
        """Access the phone information view.
        """
        phtxt = 'Phone information'
        phtob = self.dev(text=phtxt)
        pinid = util.genid(self.pkgset, 'ping_test')
        pinob = self.dev(resourceId=pinid)
        if phtob.wait.exists(timeout=3000):
            phtob.click.wait()
            return True
        elif not pinob.wait.exists(timeout=2000):
            self.backto_homescreen()
            self.start_activity(self.pkgset, self.setact)
            if phtob.wait.exists(timeout=2000):
                phtob.click()
                return True
        self.log.warning('Failed to view network phone info.')
        return False

    def _network_prefmenu_view(self):
        """Scroll down and open the preferred network menu.
        """
        scrlob = self.dev(scrollable=True)
        if scrlob.exists:
            scrlob.fling.toBeginning()
            prefid = util.genid(self.pkgset, 'preferredNetworkType')
            scrlob.scroll.to(resourceId=prefid)
            prefob = self.dev(resourceId=prefid)
            if prefob.wait.exists(timeout=2000):
                prefob.click.wait()
                return True
        self.log.warning('Failed to open pref network menu.')
        return False

    def _network_pref_select(self, netopts, network):
        """Select pref network on pref network menu.

        Args:
            netopts (dict): Mapping of network to network name.
            network (str): 2G, 3G, LTE, 3GLTE, or 2G3GLTE.
        """
        self.log.info('Select %s.', netopts[network])
        lviewid = 'android.widget.ListView'
        lviewob = self.dev(className=lviewid, scrollable=True)
        if lviewob.wait.exists(timeout=4000):
            lviewob.fling.toBeginning()
            lviewob = self.dev(className=lviewid, scrollable=True)
            lviewob.scroll.to(text=netopts[network])
            self.dev(text=netopts[network]).click()
            return True
        self.log.warning('Failed to select pref network.')
        return False

    def _network_state(self, network):
        """Get the current network state of the DUT.

        Args:
            network (str): 2G, 3G, LTE, 3GLTE, or 2G3GLTE.
        """
        ssline = None
        cmd = 'shell dumpsys telephony.registry'
        res = self.adb.cmd(*cmd.split()).communicate()[0].splitlines()
        for line in res:
            if 'mServiceState' in line:
                ssline = line.lower().strip()
                break
        is_2g = any(x in ssline for x in ['edge', 'gsm', 'gprs', '1xrtt'])
        states3g = ['umts', 'hspap', 'evdo', 'hsupa', 'hsdpa', 'hspa']
        is_3g = any(x in ssline for x in states3g)
        is_lte = 'lte' in ssline
        nets = {
            '2G': is_2g,
            '3G': is_3g,
            'LTE': is_lte,
            '2G3G': is_2g or is_3g,
            '3GLTE': is_3g or is_lte,
            '2G3GLTE': is_2g or is_3g or is_lte,
        }
        return nets[network]

    def network_switch(self, network):
        """Switch the DUT's network.

        Args:
            network (str): 2G, 3G, LTE, 3GLTE, or 2G3GLTE.
        """
        if not cfg.cget('NetworkSwitch', 'allow', 'bool'):
            return True
        if not self._is_network_valid(network):
            self.backto_homescreen()
            return False
        netopts = {
            '2G': 'GSM only',
            '3G': 'WCDMA only',
            'LTE': 'LTE only',
            '3GLTE': 'LTE/GSM auto (PRL)',
            '2G3GLTE': 'LTE/GSM auto (PRL)'
        }
        self.log.info('Switch network to %s.', network)
        self.start_activity(self.pkgset, self.setact)
        self._network_phoneinfo_view()
        self._network_prefmenu_view()
        self._network_pref_select(netopts, network)
        self.log.info('Wait for %s connection.', network)
        if not self.network_check(network):
            return False
        self.log.info('Now connected to %s.', network)
        self.backto_homescreen()
        return True

    def network_check(self, network):
        """Check the service, network, and the data connection of the DUT.

        Args:
            network (str): 2G, 3G, LTE, 3GLTE, or 2G3GLTE.
        """
        if not cfg.cget('NetworkSwitch', 'allow', 'bool'):
            return True
        if not self._is_network_valid(network):
            self.backto_homescreen()
            return False
        for _ in xrange(60):
            if self._service_state() == 'InService':
                break
            time.sleep(1)
        else:
            self.log.warning('Failed detect any service')
            return False
        for _ in xrange(60):
            if self._network_state(network):
                break
            time.sleep(1)
        else:
            self.log.warning('Failed get %s service.', network)
            return False
        for _ in xrange(60):
            if self._data_state() == 'Connected':
                break
            time.sleep(1)
        else:
            self.log.warning('Failed connect to network.')
            return False
        return True

    def call_state(self):
        """Get the call state of the DUT.

        Returns:
            ret (str): Idle, Ringing, or InCall
        """
        cmd = 'shell dumpsys telephony.registry'
        res = self.adb.cmd(*cmd.split()).communicate()[0]
        ret = None
        if 'mCallState=0' in res:
            ret = 'Idle'
        if 'mCallState=1' in res:
            ret = 'Ringing'
        if 'mCallState=2' in res:
            ret = 'InCall'
        return ret

    def start_activity(self, pkg, act):
        """Start an app.

        Args:
            pkg (str): Package name of the app.
            act (str): Activity name.
        """
        cmd = 'shell am start -n %s/%s' % (pkg, act)
        self.adb.cmd(*cmd.split()).communicate()
        if self.is_pkg(pkg, 7):
            return True
        return False

    def get_current_pkg(self):
        """Get the current package."""
        command = 'shell dumpsys window windows'
        result = self.adb.cmd(*command.split()).communicate()[0].splitlines()
        lines1 = []
        for line in result:
            if 'mCurrentFocus' in line or 'mFocusedApp' in line:
                lines1.append(line.strip())
        target_line = ''
        for line in lines1:
            if 'ActivityRecord' in line:
                temp = line.split('ActivityRecord')
                if len(temp) > 1:
                    target_line = temp[1]
                    break
        pkg_name = ''
        for line in target_line.split():
            if '/' in line:
                pkg_name = line.split('/')[0]
        return pkg_name

    def is_pkg(self, pkg, timeout, keyword=None):
        """Check if the current pkg shown on the DUT is the exptected pkg.

        Args:
            pkg (str): The expected package name.
            timeout (int): Time out if the app was not running.
        """
        for _ in xrange(timeout):
            if self.get_current_pkg() == pkg:
                return True
            if self.dev.info['currentPackageName'] == pkg:
                return True
            if keyword is not None:
                if self.dev(textMatches='(?i).*%s.*' % keyword):
                    return True
                if self.dev(descriptionMatches='(?i).*%s.*' % keyword):
                    return True
            time.sleep(1)
        return False

    def file_num(self, path, ext):
        """Get the quantity of files on the path with the specified extension.

        Args:
            path (str): Path to the files on the DUT.
            ext (str): File extension of the target files.
        """
        cmd = 'shell ls %s' % path
        res = self.adb.cmd(*cmd.split()).communicate()[0]
        return len([x for x in res.splitlines() if ext in x])

    def file_names(self, path, ext):
        """Get the names of the files on the path with the specified extension.

        Args:
            path (str): Path to the files on the DUT.
            ext (str): File extension of the target files.
        """
        cmd = 'shell ls {0}'.format(path)
        out = self.adb.cmd(*cmd.split()).communicate()[0]
        return [x.strip() for x in out.splitlines() if ext in x]

    def data_reset(self):
        """Reset the DUT's data connection.

        This is similar to turning the airplane mode on and off.
        """
        dcmd = 'shell svc data disable'
        self.adb.cmd(*dcmd.split()).communicate()
        for _ in xrange(7):
            if self._data_state() == 'Disconnected':
                break
            time.sleep(1)
        ecmd = 'shell svc data enable'
        self.adb.cmd(*ecmd.split()).communicate()
        if self.network_check('2G3GLTE'):
            return True
        return False

    def ap_mode_reset(self):
        """Toggle airplane mode on and off.

        ON COMMAND:

            adb shell settings put global airplane_mode_on 1

        OFF COMMAND:

            adb shell settings put global airplane_mode_on 0

        """
        dcmd = 'shell settings put global airplane_mode_on 0'
        self.adb.cmd(*dcmd.split()).communicate()
        for _ in xrange(7):
            if self._data_state() == 'Disconnected':
                break
            time.sleep(1)
        ecmd = 'shell settings put global airplane_mode_on 1'
        self.adb.cmd(*ecmd.split()).communicate()
        if self.network_check('2G3GLTE'):
            return True
        return False

    def screendump(self):
        """Take a screenshot and the UI hierarchy dump of the DUT.
        """
        curtime = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        sdtcdir = self._screendump_tcdir()
        ssfile = '%s_%s.png' % (self.devname, curtime)
        sspath = os.path.join(sdtcdir, ssfile)
        self.dev.screenshot(sspath)
        dpfile = '%s_%s.xml' % (self.devname, curtime)
        dppath = os.path.join(sdtcdir, dpfile)
        self.dev.dump(filename=dppath, compressed=False, pretty=True)
        self.log.info('[Screen] %s', sspath)
        self.log.info('[Dump] %s', dppath)

    def screenshot(self):
        """Take a screenshot of the DUT.

        Returns:
            sspath (str): Path to the screenshot.
        """
        curtime = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        tpddir = util.tempdump_path()
        ssfile = '%s_%s_%s.png' % (self.tcname, self.devname, curtime)
        sspath = os.path.join(tpddir, ssfile)
        self.dev.screenshot(sspath)
        for _ in xrange(7):
            if os.path.exists(sspath):
                return sspath
            time.sleep(1)
        return None

    def is_homescreen(self):
        """Check if the DUT is currently on the homescreen."""
        for _ in xrange(3):
            if self.dev(description='ALL APPS').wait.exists(timeout=1000):
                return True
        return False

    def backto_homescreen(self, timeout=7):
        """Go back to the homescreen.

        Args:
            timeout (int, optional): Time out if it couldn't go to homescreen.
        """
        self.log.info('Back to homescreen.')
        for _ in xrange(timeout):
            if self.is_homescreen():
                return True
            self.dev.press.back()
            if self.is_pkg('com.android.browser', 1):
                self.pkg_force_stop('com.android.browser')
        self.log.warning('Failed to go back to homescreen.')

        return False

    def recent_apps_show(self):
        """Show the recent apps view."""
        recentsid = util.genid('com.android.systemui', 'recents_view')
        self.dev.wait.update()
        if self.dev(resourceId=recentsid).wait.exists(timeout=3000):
            return True
        for _ in xrange(2):
            self.dev.wait.update()
            self.dev.press.recent()
            self.dev.wait.update()
            if self.dev(resourceId=recentsid).wait.exists(timeout=12000):
                return True
        return False

    def screen_turn_on(self):
        """Turn the DUT's screen on if off, and then unlock if locked."""
        if not self._is_screen_on():
            self.log.info('Turn on the screen.')
            self.dev.wakeup()
        for _ in xrange(7):
            if self._is_screen_on():
                break
            time.sleep(1)
        else:
            self.log.warning('Failed to turn on the screen.')
            return False
        if self._is_locked():
            lockid = util.genid('com.android.systemui', 'lock_icon')
            lockob = self.dev(resourceId=lockid)
            if lockob.exists:
                dispw = self.dev.info['displayWidth']
                disph = self.dev.info['displayHeight']
                lockob = self.dev(resourceId=lockid)
                if lockob.exists:
                    lockob.drag.to(x=dispw / 2, y=disph / 2, steps=5)
                    lockob = self.dev(resourceId=lockid)
                    if lockob.wait.gone(timeout=2000):
                        return True
                else:
                    self.log.warning('Failed to unlock the display')
                    return False
        return True

    def keyboard_close(self):
        """Close the keyboard if it is shown on the DUT's screen.
        """
        for _ in xrange(3):
            if not self._is_keyboard_shown():
                return True
            self.dev.press.back()
            self.dev.wait.update()
            time.sleep(1)
        cmd = 'shell input keyevent 111'
        self.adb.cmd(*cmd.split()).communicate()
        if not self._is_keyboard_shown():
            return True
        self.log.warning('Failed to close the keyboard.')
        return False

    def recent_apps_clear(self):
        """Clear all the recent apps on the DUT."""
        self.recent_apps_show()
        if self.dev(text='Your recent screens appear here').exists:
            self.backto_homescreen()
            return True
        if self.dev(description='Clear all').wait.exists(timeout=3000):
            self.log.info('Clear recent apps.')
            self.dev.wait.update()
            if self.dev(description='Clear all').exists:
                self.dev(description='Clear all').click.wait()
                if self.dev(description='Clear all').wait.gone(timeout=24000):
                    return True
        self.log.warning('Failed to clear recent apps.')
        return False

    def pkg_force_stop(self, pkg):
        """Force stop a package.

        Args:
            pkg (str): Package name of the app.
        """
        cmd = 'shell am force-stop %s' % pkg
        self.adb.cmd(*cmd.split()).communicate()
        if not self.is_pkg(pkg, 2):
            return True
        return False

    def press_enter(self):
        """Press the enter key from the keyboard.
        """
        if self._is_keyboard_shown():
            self.dev.wait.update()
            dwd = self.dev.info['displayWidth']
            dht = self.dev.info['displayHeight']
            self.dev.click(int(dwd * .92), int(dht * .95))
            self.dev.wait.update()

    def _launch_mobile_network_settings(self):
        """Launch the mobile network settings menu."""
        phone_pkg = 'com.android.phone'
        mobile_network_settings = '.MobileNetworkSettings'
        self.start_activity(phone_pkg, mobile_network_settings)
        if not self.is_pkg(phone_pkg, 3):
            self.log.warning('Failed to Open Mobile Network Settings.')
            return False
        self.dev.wait.update()
        return True

    def trigger_ims(self, state):
        """Trigger IMS ON/OFF."""
        self.log.info('Triggering IMS.')
        if not self._launch_mobile_network_settings():
            return False
        ims_switch_id = util.genid('android', 'switchWidget')
        ims_switch_off_state = self.dev(resourceId=ims_switch_id, text='OFF')
        ims_switch_on_state = self.dev(resourceId=ims_switch_id, text='ON')
        if state:
            if ims_switch_off_state.wait.exists(timeout=2000):
                ims_switch_off_state.click.wait()
                if ims_switch_on_state.wait.exists(timeout=2000):
                    self.backto_homescreen()
                    return True
            self.backto_homescreen()
            return False
        if ims_switch_on_state.wait.exists(timeout=2000):
            ims_switch_on_state.click.wait()
            if ims_switch_off_state.wait.exists(timeout=2000):
                self.backto_homescreen()
                return True
        self.backto_homescreen()
        return False
