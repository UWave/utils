#!/usr/bin/python
import sys
sys.path.append("/opt/uwave/python-rivendell")
import rivendell
import os
import sys
import json
import datetime
from subprocess import call
import syslog
import raven
import emails
from emails.template import JinjaTemplate
import requests

config = json.load(open('%s/.config/recorded_carts.json' % os.getenv("HOME")))
sentry = raven.Client(config['dsn'])

recorded_carts = config['recorded_carts']
AUDIO_ROOT = os.environ.get('RIVENDELL_AUDIO_ROOT') or '/var/snd'
rd = rivendell.Host()
cut_files = os.listdir(AUDIO_ROOT)
print_debug = "-d" in sys.argv


def debug(msg, cart=None, debug=False):
    """Print a debug message either to the syslog or the stdout."""
    out = "[Cart -----] %s" % msg
    if cart is not None:
        out = "[Cart %0.d] %s" % (cart, msg)
    if(print_debug):
        print(out)
    if not debug:
        syslog.syslog(out)


def get_cut_fingerprint(cut):
    """Get a unique fingerprint for each cut (by file size and access time)."""
    try:
        stats = os.stat('%s/%s' % (AUDIO_ROOT, cut))
        return '%s-%s' % (stats.st_size, stats.st_mtime)
    except Exception:
        sentry.captureException()

# This monstrosity needs to be broken up into little functions
for cart_str in recorded_carts.keys():
    cart = int(cart_str)
    try:
        cart_prefix = '%06d' % (cart)
        cuts = [c for c in cut_files if c.startswith(cart_prefix)]
        if not cuts:
            debug("No cuts in this cart", cart, True)
            continue
        cuts.sort()
        fingerprint = get_cut_fingerprint(cuts[0])
        for cut in cuts[1:]:
            f = get_cut_fingerprint(cut)
            if f == fingerprint:
                debug("Looks like cut %s is duplicate of cut 001, nothing to do here" % cut, cart,
                      True)
                break
        else:
            debug("No duplicates, duplicating cut 001", cart)
            cart_obj = rd.get_cart(cart)
            cart_obj.get_cuts()
            orig_cut = cart_obj.cuts[0]
            new_cut = cart_obj.create_cut()
            new_cut.set_length(orig_cut.get_length())
            new_cut.set_description(datetime.datetime.today().strftime('%Y-%m-%d'))
            new_cut.set_valid_days(False, False, False, False, False, False, False)
            call(['cp', '--preserve=timestamps', orig_cut.get_path(), new_cut.get_path()])
            if type(recorded_carts[cart_str]) == dict:
                # Used for sending an email at the end
                notification_data = {
                    "show_name": cart_obj.title
                }

                for action, data in recorded_carts[cart_str].iteritems():
                    debug("Processing action %s" % action, cart)
                    notification_data[action] = data
                    if action == "debug":
                        debug(str(action), cart)
                    if action == "owncloud":
                        auth = tuple(config['owncloud']['auth'])
                        baseURL = config['owncloud']['baseURL']
                        folder = data['folder']
                        timeformat = "%Y-%m-%d_%H:%M:%S"
                        filename = "%s.wav" % datetime.datetime.today().strftime(timeformat)
                        with open(new_cut.get_path(), 'rb') as fh:
                            requests.put('%s/%s/%s' % (baseURL, folder, filename),
                                         auth=auth, data=fh.read())
                        download = "%s/download?path=%%2F&files=%s" % (data['share_link'],
                                                                       filename)
                        notification_data['owncloud']['download_url'] = download
                if "email" in recorded_carts[cart_str]:
                    from_address = config['email']['from']
                    if type(from_address) == list:
                        from_address = tuple(from_address)
                    to_address = recorded_carts[cart_str]['email']
                    template = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                            "email.html")
                    if "template" in config['email']:
                        template = config['email']['template']
                    if type(to_address) == list:
                        to_address = tuple(to_address)
                    smtp = None
                    if "smtp" in config['email']:
                        smtp = config['email']['smtp']
                    message = emails.html(subject=JinjaTemplate(config['email']['subject']),
                                          html=JinjaTemplate(open(template).read()),
                                          mail_from=from_address)
                    message.send(to=to_address, render=notification_data)
            # TODO: Other processing (e.g. converting to MP3, etc)
    except Exception:
        sentry.captureException()
