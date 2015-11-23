import requests
import sys


class OTC_Client(object):
    # A client is initialized with the address of the server it intends to
    # connect to.

    def __init__(self, server_address, device_address):
        if not server_address.startswith("http://"):
            server_address = "http://" + server_address
        self.server_address = server_address
        self.user_id = self.get_user_id()
        self.connect()

    def send(self, message, target):
        payload = {
            "recipient_uid": target,
            "sender_uid": self.user_id,
            "contents": message,
        }
        res = requests.post(self.server_address + "/send", data=payload)
        # TODO: handle server errors
        assert res.status_code == 200

    def recieve(self):
        raise NotImplementedError("TODO: write recieve")

    def decrypt(self, message, pad_index):
        # TODO: give ability of default index
        raise NotImplementedError("TODO: clients need to decrypt messages")

    def encrypt(self, encrypt, pad_index):
        raise NotImplementedError("TODO: clients need to encrypt messages")

    def connect(self):
        res = requests.get(self.server_address + "/check")
        # TODO: handle server errors
        assert res.status_code == 200

    def readFromDevice(self):
        raise NotImplementedError(
            "TODO: clients need to be able to read from their device")
            # TODO: http form maybe

    def get_user_id(self):
        print "TODO: clients need to be able to fetch user id from their device"
        return raw_input("enter a fake user id: ")

    def get_messages(self, start_ref):
        """Get all messages starting at start_ref."""
        payload = {
            "recipient_uid": self.user_id,
            "start_ref": start_ref,
            # maxcount optional
        }
        res = requests.get(self.server_address + "/getmessages", params=payload)
        # TODO: handle server errors
        assert res.status_code == 200
        return res.json()

    def run(self):
        cursor = 0
        while (True):
            target = input("Who is your target: ")
            message = input("What is your message: ")
            self.send(message, target)
            print "Message sent!"
            # GET messages
            response = self.getMessages(self.user_id, cursor)

if __name__ == "__main__":
    if (len(sys.argv) < 3):
        print "ERROR: correct usage is client.py [server_address] [device_address]"
        sys.exit(-1)
    server_address = sys.argv[1]
    device_address = sys.argv[2]
    client = OTC_Client(server_address, device_address)
    client.send("HELLO", "bob")
    print client.get_messages(0)
