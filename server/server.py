#!/usr/bin/env python
"""
OTC Chat Client.

Usage:
  server.py [<port>]
"""
from docopt import docopt
from flask import Flask, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.autodoc import Autodoc
import wtforms
import base64

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
auto = Autodoc(app)

def interact():
    """Drop to an interactive REPL."""
    import code, inspect
    frame = inspect.currentframe()
    prevlocals = frame.f_back.f_locals
    replvars = globals().copy()
    replvars.update(prevlocals)
    code.InteractiveConsole(locals=replvars).interact()

class Message(db.Model):
    __tablename__ = "message"
    # Reference number for the message.
    ref = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    # User ID of the recipient.
    recipient_uid = db.Column(db.String(128), nullable=False, index=True)
    # User ID of the sender.
    sender_uid = db.Column(db.String(128), nullable=False)
    contents = db.Column(db.LargeBinary)
    # When the message entry was created on the server.
    created_at = db.Column(db.DateTime, default=db.func.now())

    def serialize(self):
        return {
            "ref": self.ref,
            "recipient_uid": self.recipient_uid,
            "sender_uid": self.sender_uid,
            "contents": self.contents,
        }

    def __repr__(self):
        return "<Message {} for {}>".format(self.ref, self.recipient_uid)

db.create_all()

class APIException(Exception):
    def __init__(self, status_code, message):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        return {
            "error": self.status_code,
            "message": self.message,
        }

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route("/")
@auto.doc()
def home():
    """Default page with documentation listing.
    """
    return auto.html()

@app.route("/check")
@auto.doc()
def check():
    """Check that the server is up.
    
    Returns {"status": "ok"}
    """
    resdict = {
        "status": "ok",
    }
    return jsonify(resdict)

class SendForm(wtforms.Form):
    recipient_uid = wtforms.StringField("recipient_uid")
    sender_uid = wtforms.StringField("sender_uid")
    contents = wtforms.StringField("contents")

@app.route("/send", methods=["POST"])
@auto.doc()
def send():
    """
    Send a message to a user.
    Places the message in that users's mailbox.
    
    Takes a POST form:
    - recipient_uid: Who the message is for.
    - sender_uid: Who is sending the message.
    - contents: The contents of the message.
    
    Returns json with keys:
    - received: true
    - echo_tail: The last 10 bytes of the received message (for debugging).
    - ref: The ref number of the created message.
    """
    if request.method != "POST":
        raise APIException(400, "Message send requests must be made via HTTP POST.")
    form = SendForm(request.form)
    if not form.validate():
        raise APIException(400, "Invalid form.")

    # Add a message to the db.
    message = Message()
    message.recipient_uid = form.recipient_uid.data
    message.sender_uid = form.sender_uid.data
    message.contents = form.contents.data
    db.session.add(message)
    db.session.commit()

    print "message sent ({}) -> ({})".format(
        message.sender_uid,
        message.recipient_uid)

    # Echo tail is the last 10 bytes of the received message.
    # This exists for debugging.
    echo_tail = message.contents[-10:]

    resdict = {
        "received": True,
        "echo_tail": echo_tail,
        "ref": message.ref,
    }
    return jsonify(resdict)

@app.route("/getmessages", methods=["GET"])
@auto.doc()
def getmessages():
    """
    Get all messages destined for a certain user.
    Only returns messages starting at a certain message reference number.
    
    Takes GET query parameters:
    - recipient_uid: Who the messages are for.
    - start_ref: The first ref to receive (inclusive, minimum 0).
    - maxcount: (Optional) maximum number of messages to return.

    Returns json with keys:
    - recipient_uid
    - count: How many messages are in the response.
    - messages: List of messages contents (strings).
    - complete: Whether all messages since start_ref were returned.
                (Always true if maxcount is not provided)
    """
    # ID of the user receiving the message.
    recipient_uid = request.args.get("recipient_uid")
    # The reference number of the last-seen message.
    start_ref = request.args.get("start_ref")
    # The maximum number of messages to return (optional).
    maxcount = request.args.get("maxcount")
    maxcount = int(maxcount) if maxcount != None else None

    if not recipient_uid:
        raise APIException(400, "getmessages missing required field: recipient_uid")
    if not start_ref:
        raise APIException(400, "getmessages missing required field: start_ref")

    messages = (db.session.query(Message)
                .filter(Message.recipient_uid == recipient_uid)
                .filter(Message.ref >= start_ref)
                .order_by(Message.ref).all())

    if maxcount != None and len(messages) > maxcount:
        complete = False
        messages = messages[:maxcount]
    else:
        complete = True

    resdict = {
        # ID of the user the messages were sent to.
        "recipient_uid": recipient_uid,
        # How many messages in this response.
        "count": len(messages),
        # Array of messages.
        "messages": [m.serialize() for m in messages],
        # Whether this response includes all known messages starting from start_ref.
        "complete": complete,
    }
    return jsonify(resdict)

@app.route("/getnextref", methods=["GET"])
@auto.doc()
def getnextref():
    """
    Get the next ref for a recipient.
    This is the smallest ref number which has not yet been seen by the server.

    Takes GET query parameters:
    - recipient_uid: Who to query for.

    Returns json with keys:
    - nextref: smallest ref number which has not yet been seen by the server.
    """
    # ID of the user receiving the message.
    recipient_uid = request.args.get("recipient_uid")

    if not recipient_uid:
        raise APIException(400, "getmessages missing required field: recipient_uid")

    messages = (db.session.query(Message)
                .filter(Message.recipient_uid == recipient_uid)
                .order_by(Message.ref.desc())
                .limit(1).all())

    nextref = 0
    if len(messages) > 0:
        nextref = messages[0].ref + 1

    resdict = {
        "nextref": nextref,
    }
    return jsonify(resdict)

if __name__ == "__main__":
    arguments = docopt(__doc__)
    port = arguments["<port>"]
    port = int(port) if port else 9050

    print "OTC Server starting..."
    print "Server port:", port
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
