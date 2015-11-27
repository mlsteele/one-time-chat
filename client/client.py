import requests
import sys
import rpcclient

MAX_INDEX_LENGTH = 32
TAG_LENGTH=64
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
        self.rpc_client = rpcclient.RpcClient("http://localhost:9051")

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
    
    def secure_send(self,target,message):
        """ Wrapper around send that encrypts the message before sending 
         mesage that needs to be sent is along the form :
            ciphertext = encrypt(message, pad)
            index_used || encrypt ( ciphertext || MAC (index_used || ciphertext) )
             """
        response = self.rpc_client.encrypt(target,message)
        cipher_text = response["cipher_text"]
        index_used = response["index_used"]
        
        tag = self.rpc_client.sign(index_used+ciphertext)
        
        integrity = self.rpc_client.encrypt(target, ciphertext+tag)

        message_body = integrity["cipher_text"]
        
        return self.send(target,index_used+message_body)
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
    def secure_get_messages(self,start_ref):
        """Get all the ciphertext and return a list of messages.
        packets recieved are in the format 
        index || encrypt ( ciphertext || SHA ( i || ciphertext ) )

        """
        payload = {
                "recipient_uid": self.user_id,
                "start_ref": start_ref,
        }
        res = requests.get(self.server_address + "/getmessages",params=payload)
        assert res.status_code ==200
        response_data = res.json()
        recieved_packets = response_data[u'messages']
        ### PLEASE REVIEW I PROBABLY !@#$ED UP- anpere ###
        for packet in recieved_packets:
            packet_sender = packet[u'sender_uid']
            packet_message = packet[u'contents']
            index = packet_message[:MAX_INDEX_LENGTH]
            packet_body = packet_message[MAX_INDEX_LENGTH:]
            
            plain_body = self.rpc_client.decrypt(packet_sender,
                    packet_body,
                    int(index)+len(packet_body)-TAG_LENGTH)
            ## the starting index of the body pad: index + length of cipher text
            ## length of cipher text = length of body - length of tag
            tag = plain_body[-64:]
            ciphertext = plain_body[:-64]
            isSafe = self.rpc_client.verfy(packet_sender,index+ciphertext,tag)
            if isSafe:
               message = self.rpc_client.encrypt(packet_sender,ciphertext,index)


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
