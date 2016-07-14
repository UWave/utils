#!/usr/bin/env python
"""Checks a list of jack ports that are supposed to be connected and ensures that they are."""
import jack
import os
import json

client = jack.Client(os.path.basename(__file__))
conf = json.load(open("/etc/jackmon.conf"))

for p in conf['ports']:
    try:
        client.connect(p[0], p[1])
    except jack.Error as e:
        print("Error: {} for ports {} and {}".format(e, p[0], p[1]))
