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
        "RS 1 0%0.d 1 7500000!" % nextShowCart,
        "TA f 1!",
        "SN now 1 0%0.d!" % nextShowCart,
        "PM 3!",
        "LB %s!" % showname.replace("!", ""),
        "PX 1 050016!"])
    print("Making cart %0.d named %s" % (nextMacroCart, macroCartName))

    c.execute("INSERT INTO CART(`NUMBER`, `TYPE`, `GROUP_NAME`, `TITLE`, `MACROS`) VALUES (%s, 2, 'MACROS', %s, %s)", (nextMacroCart, macroCartName, macros))

    c.close()
    db.commit()

    with open('%s/.config/recorded_carts.json' % os.getenv("HOME")) as recorded_carts_file:
        existingcarts = json.load(recorded_carts_file)

    existingcarts.append(nextShowCart)

    with open('%s/.config/recorded_carts.json' % os.getenv("HOME"), 'w') as recorded_carts_file:
        json.dump(existingcarts, recorded_carts_file)
        print("Added cart %0.d to list of recorded carts" % nextShowCart)

if __name__ == "__main__":
    mkbutton(showname)
