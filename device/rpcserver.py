#!/usr/bin/env python
import rpcmethods
from flask import Flask, request, jsonify
import os
import inspect
import traceback

app = Flask(__name__)

@app.route("/runrpc", methods=["POST"])
def runrpc():
    call = request.json

    try:
        method = getattr(rpcmethods, call["method"])
    except AttributeError:
        return jsonify({"error": "no such rpc method"})

    # Only allow methods of rpcmethods to be called.
    if not inspect.isfunction(method):
        return jsonify({"error": "requested rpc value is not a method"})

    try:
        result = method(*call["args"], **call["kwargs"])
        print "ran rpc: ", call["method"]
        return jsonify({"return": result})
    except Exception as exc:
        traceback.print_exc()
        return jsonify({"error": "rpc call threw an exception"})


if __name__ == "__main__":
    debug = os.environ.get("DEBUG", False) == "true"
    print "debug", "on" if debug else "off"
    app.run(host="0.0.0.0", port=9051, debug=debug)
