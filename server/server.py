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
            "status": self.status_code,
            "message": self.message,
        }

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route("/")
def home():
    return "otc server"

@app.route("/send", methods=["GET", "POST"])
def send():
    if request.method != "POST":
        raise APIException(400, "Message send requests must be HTTP POST.")

    message = request.get_data()

    # Echo tail is the last 10 bytes of the received message.
    # This exists for debugging.
    echo_tail = message[-10:]

    resdict = {
        "received": True,
        "echo_tail": echo_tail,
    }
    return jsonify(resdict)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9050, debug=True)
