#!/usr/bin/env python
"""Checks a list of jack ports that are supposed to be connected and ensures that they are."""
import jack
import os
import json
import logging
import sys


if "-d" in sys.argv:
    logging.basicConfig(level=logging.DEBUG)

client = jack.Client(os.path.basename(__file__))
conf = json.load(open("/etc/jackmon.conf"))

for p in conf['ports']:
    try:
        connections = client.get_connections(p[0])
        if p[1] not in connections:
            logging.warning("%s wasn't connected to %s! I've connected them", p[0], p[1])
            client.connect(p[0], p[1])
        else:
            logging.debug("%s already connected to %s", p[0], p[1])
    except jack.Error as e:
        logging.error("Error: {} for ports {} and {}".format(e, p[0], p[1]))
