#!/usr/bin/env python
"""
OTC Pad Device.
Entry point for device code.

Usage:
  main.py [<port>] [--no-display] [--debug]

Options:
  --no-display    Don't initialize the display.
  --debug         Run the rpc server in debug mode (don't do this on secure device)
"""
from docopt import docopt

import rpcserver
import rpcmethods
import confirm
import otc_log
import logging

if __name__ == "__main__":
    arguments = docopt(__doc__)
    port = arguments["<port>"]
    port = int(port) if port else 9051
    display_enabled = not arguments["--no-display"]
    debug = arguments["--debug"]

    if display_enabled:
        print "Starting confirmation display process."
        csc = confirm.ConfirmScreenController(fullscreen=False)
        rpcmethods.csc = csc
        csc.start()
    else:
        print "Starting dummy confirmer. (Always says yes)"
        csc = confirm.DummyConfirmScreenController()
        rpcmethods.csc = csc

    print "Starting rpc server."
    print "Debug mode", "on." if debug else "off."
    rpcserver.app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)

    print "Shutting down."
    if csc:
        csc.shutdown()

