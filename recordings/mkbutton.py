#!/usr/bin/env python2
"""Simple script to create a show record button in Rivendell."""
import sys
import MySQLdb
from ConfigParser import SafeConfigParser
import os
import json

showname = ""

if len(sys.argv) > 1:
    showname = " ".join(sys.argv[1:])
else:
    showname = raw_input("Name of new show? ")

if showname == "":
    print("Please specify a show name")
    sys.exit(1)


def mkbutton(show):
    cfg = SafeConfigParser()
    cfg.read('/etc/rd.conf')

    db = MySQLdb.connect(host=cfg.get("mySQL", "Hostname"), user=cfg.get("mySQL", "Loginname"),
                         passwd=cfg.get("mySQL", "Password"), db=cfg.get("mySQL", "Database"))
    c = db.cursor()

    # Get the ID for the last SHOWS cart (we're that +1)
    c.execute("SELECT NUMBER FROM CART WHERE `GROUP_NAME` = 'SHOWS' ORDER BY NUMBER DESC LIMIT 1;")

    nextShowCart = c.fetchone()[0] + 1

    print("Making cart %0.d for storing show %s" % (nextShowCart, show))

    c.execute("INSERT INTO CART(`NUMBER`, `TYPE`, `GROUP_NAME`, `TITLE`) VALUES (%s, 1, 'SHOWS', %s);", (nextShowCart, show,))

    print("Making cut in cart %0.d" % nextShowCart)

    c.execute("INSERT INTO `CUTS` (`CUT_NAME`, `CART_NUMBER`, `EVERGREEN`, `DESCRIPTION`, `OUTCUE`, `ISRC`, `ISCI`, `LENGTH`, `ORIGIN_DATETIME`, `START_DATETIME`, `END_DATETIME`, `SUN`, `MON`, `TUE`, `WED`, `THU`, `FRI`, `SAT`, `START_DAYPART`, `END_DAYPART`, `ORIGIN_NAME`, `WEIGHT`, `LAST_PLAY_DATETIME`, `UPLOAD_DATETIME`, `PLAY_COUNTER`, `LOCAL_COUNTER`, `VALIDITY`, `CODING_FORMAT`, `SAMPLE_RATE`, `BIT_RATE`, `CHANNELS`, `PLAY_GAIN`, `START_POINT`, `END_POINT`, `FADEUP_POINT`, `FADEDOWN_POINT`, `SEGUE_START_POINT`, `SEGUE_END_POINT`, `SEGUE_GAIN`, `HOOK_START_POINT`, `HOOK_END_POINT`, `TALK_START_POINT`, `TALK_END_POINT`) VALUES('0%0.d_001', %0.d, 'N', 'Cut 001', '', '', '', 3808, '2000-01-01 00:00:00', NULL, NULL, 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', NULL, NULL, 'hill', 1, NULL, NULL, 0, 0, 2, 0, 44100, 128000, 2, 0, 0, 3808, -1, -1, -1, -1, -3000, -1, -1, -1, -1);" % (nextShowCart, nextShowCart))

    c.execute("SELECT NUMBER FROM CART WHERE `GROUP_NAME` = 'MACROS' AND NUMBER < 59999 ORDER BY NUMBER DESC LIMIT 1;")

    nextMacroCart = c.fetchone()[0] + 1
    macroCartName = "Record %s" % show

    macros = "".join([
        "RS 1 0%0.d 1 7500000!" % nextShowCart,  # Record on deck 1 to nextShowCart cut 1 for up to 7500000 ms (just over 2 hours)
        "TA 1!",  # Toggle the on air flag
        "SN now 1 0%0.d!" % nextShowCart,  # Set the current cart to now cart to nextShowCart
        "PM 3!",  # Set mode to manual (1 = LiveAssist, 2 = Auto, 3 = Manual)
        "LB %s!" % showname.replace("!", ""),  # Set the label in RDAirPlay to the show name
        "PX 1 050016!"])  # Insert cart 050016 (the "stop recording" cart) to the next position
    print("Making cart %0.d named %s" % (nextMacroCart, macroCartName))

    c.execute("INSERT INTO CART(`NUMBER`, `TYPE`, `GROUP_NAME`, `TITLE`, `MACROS`) VALUES (%s, 2, 'MACROS', %s, %s)", (nextMacroCart, macroCartName, macros))

    c.close()
    db.commit()

    with open('%s/.config/recorded_carts.json' % os.getenv("HOME")) as recorded_carts_file:
        existingcarts = json.load(recorded_carts_file)

    existingcarts['recorded_carts'][nextShowCart] = None

    with open('%s/.config/recorded_carts.json' % os.getenv("HOME"), 'w') as recorded_carts_file:
        json.dump(existingcarts, recorded_carts_file, sort_keys=True, indent=4,
                  separators=(',', ': '))
        print("Added cart %0.d to list of recorded carts" % nextShowCart)

if __name__ == "__main__":
    mkbutton(showname)
