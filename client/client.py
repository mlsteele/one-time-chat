import requests
import sys


class OTC_Client(object):
    # A client is initialized with the address of the server it intends to
    # connect to

    # TODO: fix the initialization with pad. Client shouldn't get access to pad
    def __init__(self, server_address, device_id, username=None,):
        self.encrypt_index = 0
        self.device_id = device_id
        # TODO: what is a good value for the decrypt index?
        self.decrypt_index = None
        if username is None:
            self.username = self.getUserId()
        else:
            self.username = username
        self.server_address = server_address
        self.connect()

    def send(self, message, target):
        payload = {'message': message, 'target': target}
        r = requests.post(self.server_address, data=payload)

    def recieve(self):
        raise NotImplementedError("TODO: write recieve")

    def decrypt(self, message, pad_index):
        # TODO: give ability of default index
        raise NotImplementedError("TODO: clients need to decrypt messages")

    def encrypt(self, encrypt, pad_index):
        raise NotImplementedError("TODO: clients need to encrypt messages")

    def connect(self):
        payload = {'message': "connect"}
        r = requests.post(self.server_address, data=payload)
        # TODO: handle response from server

    def readFromDevice(self):
        raise NotImplementedError(
            "TODO: clients need to be able to read from their device")
    # TODO: http form maybe

    def getUserId(self):
        raise NotImplementedError(
            "TODO: clients need to be able to fetch user id from their device")

    def getMessages(self, name, cursor):
        payload = {'uid': name, 'last_seen': cursor}
        r = requests.post(self.server_address + "/getmessages", params=payload)
        return r
        raise NotImplementedError(
            "TODO: clients need to be able to poll messages")

    def run(self):
        cursor = 0
        while (True):
            target = input("Who is your target: ")
            message = input("What is your message: ")
            self.send(message, target)
            print "Message sent!"
            # GET messages
            response = self.getMessages(self.username, cursor)

if __name__ == "__main__":
    if (len(sys.argv) < 3):
        print "ERROR: correct usage is client.py [server_address] [pad_file]"
    server_address = sys.argv[1]
    pad_file = sys.argv[2]
    client = OTC_Client(server_address, device_id)
    client.send("HELLO", "alice")
