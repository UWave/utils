#!/usr/bin/env python
import ConfigParser
import MySQLdb
import os
import sys

parser = ConfigParser.ConfigParser()
parser.read("/etc/rd.conf")


dbopts = {'Hostname': 'localhost', 'Loginname': 'rduser', 'Password': None, 'Database': 'Rivendell'}
if parser.has_option("mySQL", "Hostname"):
    dbopts['Hostname'] = parser.get("mySQL", "Hostname")
if parser.has_option("mySQL", "Loginname"):
    dbopts['Loginname'] = parser.get("mySQL", "Loginname")
    if parser.has_option("mySQL", "Password"):
        dbopts['Password'] = parser.get("mySQL", "Password")
if parser.has_option("mySQL", "Database"):
    dbopts['Database'] = parser.get("mySQL", "Database")

db = MySQLdb.connect(dbopts['Hostname'], dbopts['Loginname'], dbopts['Password'],
                     dbopts['Database'])
cursor = db.cursor()

conditions = "FROM CUTS WHERE ORIGIN_DATETIME < DATE_SUB(NOW(), INTERVAL 2 YEAR) AND CART_NUMBER BETWEEN 80000 AND 90000;"

cursor.execute("SELECT CUT_NAME %s" % conditions)
for result in cursor.fetchall():
    try:
        os.remove("/var/snd/%s.wav" % result[0])
    except OSError:
        sys.stderr.write("OMG %s doesn't exist!\n" % result[0])

cursor.execute("DELETE %s" % conditions)
