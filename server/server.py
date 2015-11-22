from flask import Flask, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
import wtforms
import base64

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

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
def home():
    return "One Time Chat API Server"

class SendForm(wtforms.Form):
    recipient_uid = wtforms.StringField("recipient_uid")
    sender_uid = wtforms.StringField("sender_uid")
    contents = wtforms.StringField("contents")

@app.route("/send", methods=["GET", "POST"])
def send():
    """
    Send a message to a user.
    Places the message in that users's mailbox.
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
def getmessages():
    """
    Get all messages destined for a certain user.
    Only returns messages since a certain message reference number.
    """
    # ID of the user receiving the message.
    uid = request.args.get("uid")
    # The reference number of the last-seen message.
    last_seen = request.args.get("last_seen")

    if not uid:
        raise APIException(400, "getmessages missing required field: uid")
    if not last_seen:
        raise APIException(400, "getmessages missing required field: last_seen")

    # TODO(miles): use last seen
    messages = (db.session.query(Message)
                .filter(Message.recipient_uid == uid)
                .filter(Message.ref > last_seen)
                .order_by(Message.ref).all())

    resdict = {
        # ID of the user the messages were sent to.
        "recipient_uid": uid,
        # How many messages in this response.
        "count": len(messages),
        # Array of messages.
        "messages": [m.serialize() for m in messages],
        # Whether this response includes all known messages after last_seen.
        "complete": True,
    }
    return jsonify(resdict)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9050, debug=True)
