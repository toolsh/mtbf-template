"""Idol4 (6055U) Cricket Stability Documentation

Modules:
    * cfg.py - Parse configuration files in cfg directory.
    * util.py - Provide Package-wide utility functions.
    * common.py - Shared by the following sub-classes.
        * telephony.py
        * messaging.py
        * email.py
        * browser.py
        * storefront.py
        * pim.py
        * multimedia.py
        * multitasking.py
        * menunavigation.py
        * wifi.py
        * nfc.py

Scripts:
    * 01_Telephony.py
    * 02_Messaging.py
    * 03_Email.py
    * 04_Browser.py
    * 05_Storefront.py
    * 06_PIM.py
    * 07_MultiMedia.py
    * 08_MultiTasking.py
    * 09_MenuNavigation.py
    * 10_WiFi.py
    * 11_NFC.py

Author:
    Ji Park <j.park.cnt@alcatelonetouch.com>

Credits:
    Chengkun, Yue <chengkun.yue@tcl.com>
    The authors of Idol4 & Aspire projects.

Project:
    Idol4 (6055U) Cricket, Android v6.0.1, SDK v23

Adapted from Astra Cricket, Idol4 Cricket, and Aspire Cricket scripts.

Specifications:
    13340 AT&T Requirements v5.7 Chapter 40
    15595 AT&T Test Plan v3.8

Environment:
    Intel, Windows7 (32/64bit)
    Python v2.7.11 (Windows x86 MSI installer)

External Packages:
    UIAutomator v0.2.6 <https://github.com/xiaocong/uiautomator>
    NumPy v1.11.0 CP27 Win32 <http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy>
    OpenCV v3.1 CP27 Win32 <http://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv>

Coding Style:
    Google Python Style  <http://google.github.io/styleguide/pyguide.html>
    Flake8 <http://flake8.pycqa.org/en/latest/>
    Pylint <https://www.pylint.org/>
"""
