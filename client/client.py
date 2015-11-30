"""
OTC Chat Client.

Usage:
  client.py <server_address> <device_address> <user_name>

Options:
  server_address    Address of the message relay server.
  device_address    Address of the pad device rpc server.
  user_name         Your username.
"""
from docopt import docopt
import requests
from requests.exceptions import RequestException
import os
import sys
import rpcclient

MAX_INDEX_LENGTH = 32 # TODO: agree on a valid number
TAG_LENGTH=64

class ClientException(Exception):
    pass

class OTC_Client(object):
    # A client is initialized with the address of the server it intends to
    # connect to.

    def __init__(self, server_address, device_address, user_id):
        self.server_address = normalize_address(server_address)
        self.device_address = normalize_address(device_address)
        # TODO: remove for testing self.user_id = self.get_user_id()
        self.user_id = user_id

        print "Relay server address:", self.server_address
        print "Pad   device address:", self.device_address
        print "User ID:", self.user_id

        self.connect()
        self.nextref = self.get_next_ref()  # first unread ref
        self.friends = {}
        self.rpc_client = rpcclient.RpcClient(self.device_address)

    #TODO: mapping of username to uid
    def send_plaintext(self, target, message):
        payload = {
            "recipient_uid": target,
            "sender_uid": self.user_id,
            "contents": message,
        }
        try:
            res = requests.post(self.server_address + "/send", data=payload)
            res.raise_for_status()
        except RequestException as ex:
            raise ClientException("Could not connect to server.", ex)

    def package(self, target, message):
        res = self.rpc_client.package(self.user_id, target, message)
        if not res["success"]:
            raise ClientException("Message packaging failed on device.")
        return res["package"]

    def send_secure(self, target, message_plaintext):
        package = self.package(target, message_plaintext)
        self.send_plaintext(target, package)

    # TODO  FIX -- put all of this on device, cal it packet/package or something
    #  because it just makes more sense to do this all on device instead of
    #  sending shit back and forth 38 times. Also asking the person multiple
    #  times for confirmation is annoying
    def secure_send_old(self,target,message):
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
        try:
            res = requests.get(self.server_address + "/check")
            res.raise_for_status()
        except RequestException as ex:
            raise ClientException("Could not connect to server.", ex)

    def readFromDevice(self):
        raise NotImplementedError(
            "TODO: clients need to be able to read from their device")
            # TODO: http form maybe

    def get_user_id(self):
        print "TODO: clients need to be able to fetch user id from their device"
        return raw_input("enter a fake user id: ")

    def get_username_id(self,username):
        return self.friends[username]

    def get_next_ref(self):
        """Get the next ref for a recipient.
        This is the smallest ref number which has not yet been seen by the server.
        """
        # TODO it might better if this came from the device instead.
        payload = {
            "recipient_uid": self.user_id,
        }
        try:
            res = requests.get(self.server_address + "/getnextref", params=payload)
            res.raise_for_status()
        except RequestException as ex:
            raise ClientException("Could not get next ref from server.", ex)
        return res.json()["nextref"]

    def get_messages(self, start_ref):
        """Get all messages starting at start_ref."""
        payload = {
            "recipient_uid": self.user_id,
            "start_ref": start_ref,
            # maxcount optional
        }
        try:
            res = requests.get(self.server_address + "/getmessages", params=payload)
            res.raise_for_status()
        except RequestException as ex:
            raise ClientException("Could not get messages from server.", ex)
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
        print "Welcome to One Time Chat. Type 'help' for help."

        while (True):
            print ""
            print "Cursor:", self.nextref
            user_input = raw_input().split()
            if len(user_input) == 0:
                response = self.get_messages(self.nextref)
                messages = response[u'messages']
                for message in messages:
                    print message[u'sender_uid'] + ": " + message[u'contents']
                    self.nextref = message['ref'] + 1
                continue
            command = user_input[0]
            if ( command == "help"):
                print "=== help ==="
                print "to send type send [target] [message]"
                print "to recieve messages press enter."
                print "to see your user id type id."
                print "to clear the screen type clear."
                print "to quit type quit or q or exit."
                print "============"
            elif (command  == "send"):
                recipient = user_input[1]
                message = " ".join(user_input[2:])
                self.send_secure(recipient, message)
                print "Message sent!"
            elif command == "id":
                print "User ID:", self.user_id
            elif command == "lookup":
                raise NotImplementedError("need to implement username to uid lookup")
            elif command == "clear":
                os.system("clear")
            elif command in ["quit", "q", "exit"]:
                print "Bye."
                sys.exit(0)
            else:
                print "Unrecognized command '{}'. Type 'help' for help.".format(command)


def normalize_address(address):
    # Assume that a number is a port on localhost.
    try:
        int(address)
        return "http://localhost:{}".format(address)
    except ValueError:
        pass
    # Add http protocol.
    if not address.startswith("http://"):
        return "http://{}".format(address)


if __name__ == "__main__":
    arguments = docopt(__doc__)

    server_address = arguments["<server_address>"]
    device_address = arguments["<device_address>"]
    user_name = arguments["<user_name>"]
    client = OTC_Client(server_address, device_address, user_name)

    try:
        client.run()
    except (KeyboardInterrupt, EOFError):
        print "\nBye."
        sys.exit(0)
