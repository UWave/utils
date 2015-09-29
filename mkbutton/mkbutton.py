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

    print("Making cart %0.d for storing show %s" % (nextShowCart, showname))

    c.execute("INSERT INTO CART(`NUMBER`, `TYPE`, `GROUP_NAME`, `TITLE`) VALUES (%s, 1, 'SHOWS', %s);", (nextShowCart, showname,))

    c.execute("SELECT NUMBER FROM CART WHERE `GROUP_NAME` = 'MACROS' AND NUMBER < 59999 ORDER BY NUMBER DESC LIMIT 1;")

    nextMacroCart = c.fetchone()[0] + 1
    macroCartName = "Record %s" % showname

    macros = "RS 1 0%0.d 1 7500000!TA f 1!SN now 1 0%0.d!PM 3!PX 1 050016!" % (nextShowCart,
                                                                             nextShowCart)

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
