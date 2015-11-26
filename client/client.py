import requests
import sys


class OTC_Client(object):
    # A client is initialized with the address of the server it intends to
    # connect to.

    def __init__(self, server_address, user_id, device_address=0):
        if not server_address.startswith("http://"):
            server_address = "http://" + server_address
        self.server_address = server_address
        # TODO: remove for testing self.user_id = self.get_user_id()
        self.user_id = user_id
        self.connect()
        self.friends = {}

    #TODO: mapping of username to uid
    def send(self, target, message):
        payload = {
            "recipient_uid": target,
            "sender_uid": self.user_id,
            "contents": message,
        }
        res = requests.post(self.server_address + "/send", data=payload)
        # TODO: handle server errors
        assert res.status_code == 200
        return res.json()

    def receive(self):
        raise NotImplementedError("TODO: write receive")

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

    def getCurrentCursor(self):
        raise NotImplemetnedError("TODO: cursor must be read from device")
    def get_user_id(self):
        print "TODO: clients need to be able to fetch user id from their device"
        return raw_input("enter a fake user id: ")
    def get_username_id(self,username):
        return self.friends[username]
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
        print "Welcome to One Time Chat. Type 'help' for help"
        while (True):
            print cursor
            user_input = raw_input().split()
            if len(user_input) == 0:
                response = self.get_messages(cursor)
                messages = response[u'messages']
                for message in messages:
                    print message[u'sender_uid'] + ":" + message[u'contents']
                    cursor += 1
                continue
            command = user_input[0]
            if ( command == "help"):
                print "to send type send [message] [target]"
            elif (command  == "send"):
                sent_response = self.send(user_input[1]," ".join(user_input[2:]))
                if sent_response[u'received']==True:
                    print "Message sent!"
            elif command == "id":
                print self.user_id
            elif command == "lookup":
                raise NotImplementedError("need to implement username to uid lookup")
            # GET messages
            response = self.get_messages(cursor)
            messages = response[u'messages']
            for message in messages:
                print message[u'sender_uid'] + ":" + message[u'contents']
                cursor+= 1

if __name__ == "__main__":
    if (len(sys.argv) < 3):
        print "ERROR: correct usage is client.py [server_address] [user_name]"
        sys.exit(-1)
    server_address = sys.argv[1]
    user_name = sys.argv[2]
    client = OTC_Client(server_address, user_name)
    client.run()
