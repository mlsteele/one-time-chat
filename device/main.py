"""
Entry point for device.
"""

import rpcserver
import confirm

if __name__ == "__main__":
    print "Hello."
    print "Starting confirmation display process."
    csc = confirm.ConfirmScreenController(fullscreen=False)
    csc.start()
    print "Starting rpc server."
    rpcserver.app.run(host="0.0.0.0", port=9051, debug=False)

    print "Shutting down."
    csc.shutdown()
