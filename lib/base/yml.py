"""Utility module."""

from __future__ import absolute_import
from __future__ import division

import os, sys
import yaml

class YML(object):
    def __init__(self, file):
        self._file=open(file)
        self._yml=yaml.load(self._file)

    def get(self, *args):
        ret = self._yml
        for arg in args:
            ret = ret[arg]
        return ret

    def set(self, value, *args):
        ret = self._yml
        for i in range(len(args)-1):
            ret = ret[args[i]]
        ret[args[len(args)-1]] = value

    def sum(self, section, yml=None):
        ret = 0
        if not isinstance(yml, dict): yml = self._yml
        for key in yml[section]:
            ret += int(yml[section][key])
        return ret

def test():
    print "-" * 100
    yml = YML("../../cfg/att-3glte-full.yaml")
    for section in yml.get(): print section, yml.sum(section)
    print yml.sum('Messaging')

    print "-" * 100
    yml = YML("../../cfg/mtbf.yaml")
    v = []
    v.append(yml.get())
    v.append(yml.get("MDevice"))
    v.append(yml.get('MDevice', "phone"))
    v.append(yml.get('Email', 'recipient', 'email'))
    v.append(yml.get('Email').get('recipient').get('email'))
    v.append(yml.get('Testing', 'network_switch'))
    v.append(yml.get('MultiMedia', 'music_time'))
    v.append(yml.get('MultiMedia').get('music_time'))
    for w in v: print w, type(w)
    print yml.sum('Messaging')
    #print yml.sum('recipient', yml.get('Messaging'))

    f=open("dump-mtbf.yaml","w")
    yaml.dump(yml,f)
    f.close

    print "-" * 100
    yml = YML("dump.yaml").get().get()
    print yml["Messaging"]

    print "-" * 100
    yml = YML("dump.yaml").get()
    print yml.get("Messaging")

    print "-" * 100
    yml = yaml.load(open("dump.yaml","r"))
    print yml.get("Messaging")

def obj():
    yaml_files = ["mtbf", "endurance", "req-mtbf-att", "app", "package"]
    objects = YML("../../cfg/object-template.yaml")
    for yaml_file in yaml_files:
        yml = YML("../../cfg/" + yaml_file + ".yaml")
        objects.set(yml, 'yaml', yaml_file)

    f=open("dump-objects.yaml","w")
    print yaml.dump(objects,f)
    f.close

if __name__ == '__main__':
    # test()
    obj()

