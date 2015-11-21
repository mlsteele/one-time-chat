from flask import Flask, request, jsonify
import base64

app = Flask(__name__)

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

@app.route("/send", methods=["GET", "POST"])
def send():
    """
    Send a message to a user.
    Places the message in that users's mailbox.
    """
    if request.method != "POST":
        raise APIException(400, "Message send requests must be HTTP POST.")

    # TODO(miles): this will actually be a form in a sec.
    message = request.get_data()

    # Echo tail is the last 10 bytes of the received message.
    # This exists for debugging.
    echo_tail = message[-10:]

    resdict = {
        "received": True,
        "echo_tail": echo_tail,
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

    # TODO(miles): remove dummy data
    messages = ["hi", "there"]
    last_message_counter = 5

    resdict = {
        # ID of the user the messages were sent to.
        "receiver_uid": uid,
        # How many messages in this response.
        "count": len(messages),
        # Array of messages.
        "messages": messages,
        # Whether this response includes all known messages after last_seen.
        "complete": True,
        # The reference number of the last message shown.
        "last_ref": last_message_counter,
    }
    return jsonify(resdict)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9050, debug=True)
