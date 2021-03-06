#!/usr/bin/env python
"""
OTC Chat Client.

Usage:
  client.py <server_address> <device_address> <user_name>

Options:
  server_address    Address of the message relay server.
  device_address    Address of the pad device rpc server.
  user_id           Your username.
"""
from docopt import docopt
import requests
from requests.exceptions import RequestException
import os
import sys
import rpcclient

class ClientException(Exception):
    pass

class OTC_Client(object):
    # A client is initialized with the address of the server it intends to
    # connect to.

    def __init__(self, server_address, device_address, user_id):
        self.server_address = normalize_address(server_address)
        self.device_address = normalize_address(device_address)
        self.user_id = user_id

        print "Relay server address:", self.server_address
        print "Pad   device address:", self.device_address
        print "User ID:", self.user_id

        self.connect()
        # a map from groups to users in that group
        self.groups = {}
        self.rpc_client = rpcclient.RpcClient(self.device_address)
        self.nextref = self.get_next_ref()  # first unread ref

    def send_plaintext(self, target, message):
        payload = {
            "recipient_uid": target,
            "sender_uid": self.user_id,
            "contents": message,
        }
        try:
            res = requests.post(self.server_address + "/send", data=payload, timeout=1)
            res.raise_for_status()
        except RequestException as ex:
            raise ClientException("Could not connect to server.", ex)

    def package(self, target, message):
        """Package a message on the device."""
        res = self.rpc_client.package(self.user_id, target, message)
        if not res["success"]:
            raise ClientException("Message packaging failed on device.")
        return res["package"]

    def send_secure(self, target, message_plaintext):
        try:
            res = self.rpc_client.package(self.user_id, target, message_plaintext)
            if not res.get("success"):
                error = res.get("error")
                print "Failed to create message for '{}' ({})".format(target, error)
                return False
            self.send_plaintext(target, res["package"])
            return True
        except rpcclient.RpcException as ex:
            print ex
            return False

    def connect(self):
        """Check that the message relay server is alive."""
        try:
            res = requests.get(self.server_address + "/check", timeout=1)
            res.raise_for_status()
        except RequestException as ex:
            raise ClientException("Could not connect to server.", ex)

    def get_next_ref(self):
        """
        Get the next ref for a recipient from the device.
        This is the smallest ref number which has not yet been seen by the server.
        """
        payload = {
            "recipient_uid": self.user_id,
        }
        try:
            res = requests.get(self.server_address + "/getnextref", params=payload)
            res.raise_for_status()
            server_nextref = res.json()["nextref"]
        except RequestException as ex:
            print "Could not get next ref from server.", ex
            server_nextref = None

        device_nextref = self.rpc_client.get_next_ref(self.user_id, self.server_address)

        if server_nextref == None and device_nextref == None:
            return 0
        if server_nextref == None:
            return device_nextref
        if device_nextref == None:
            return server_nextref
        return min(server_nextref, device_nextref)

    def save_next_ref(self):
        """Save the next ref setting to the device."""
        self.rpc_client.save_next_ref(self.user_id, self.server_address, self.nextref)

    def get_messages(self, start_ref):
        """Get all messages starting at start_ref."""
        payload = {
            "recipient_uid": self.user_id,
            "start_ref": start_ref,
        }
        try:
            res = requests.get(self.server_address + "/getmessages", params=payload)
            res.raise_for_status()
        except RequestException as ex:
            raise ClientException("Could not get messages from server.", ex)
        return res.json()

    def show_package(self, from_uid, package):
        try:
            res = self.rpc_client.unpackage(from_uid, self.user_id, package)
        except:
            res = {
                "success": False,
                "error": "unknown rpc error",
            }

        if res.get("skip_detected"):
            print "WARNING: Possible skip detected. Server may be maliciously dropping packets."
        if res.get("reuse_detected"):
            print "WARNING: Possible reuse detected. An attacker may be injecting packets."

        if res["success"]:
            print from_uid + ": " + res["message"]
        else:
            error = res.get("error")
            print "Failed to decode message from '{}' ({})".format(from_uid, error)

    def run(self):
        print "Welcome to One Time Chat. Type 'help' for help."

        while (True):
            print ""
            print "Cursor:", self.nextref
            user_input = raw_input().split()
            if len(user_input) == 0:
                # Default to receive messages.
                response = self.get_messages(self.nextref)
                messages = response[u'messages']
                for message in messages:
                    self.nextref = message['ref'] + 1
                    self.save_next_ref()
                    self.show_package(message['sender_uid'], message['contents'])
                continue
            command = user_input[0]
            if ( command == "help"):
                print "=== help ==="
                print "to send type send [target] [message]"
                print "to send to many users type ms [user1],[user2],...,[userN] [message]"
                print "to send to a group type gs groupname message"
                print "to create a group type group groupname [user1] [user2] ... [userN]"
                print "to recieve messages press enter."
                print "to see your user id type id."
                print "to clear the screen type clear."
                print "to quit type quit or q or exit."
                print "============"
            elif (command  == "send"):
                if len(user_input) < 2:
                    print "Invalid command. See help for usage."
                    continue
                recipient = user_input[1]
                message = " ".join(user_input[2:])
                success = self.send_secure(recipient, message)
                if success:
                    print "Message sent."
                else:
                    print "Error: Failed to send message."
            elif command == "ms":
                if len(user_input) < 2:
                    print "Invalid command. See help for usage."
                    continue
                recipients = user_input[1].split(",")
                message = " ".join(user_input[2:])
                for recipient in recipients:
                    if recipient == self.user_id:
                        continue
                    success = self.send_secure(recipient, message)
                    if success:
                        print "Message sent."
                    else:
                        print "Error: Failed to send message."
            elif command == "gs":
                if len(user_input) < 2:
                    print "Invalid command. See help for usage."
                    continue
                message = " ".join(user_input[2:])
                for recipient in self.groups[user_input[1]]:
                    if recipient == self.user_id:
                        continue
                    success = self.send_secure(recipient, message)
                    if success:
                        print "Message sent."
                    else:
                        print "Error: Failed to send message."
            elif command == "group":
                if len(user_input) < 2:
                    print "Invalid command. See help for usage."
                    continue
                self.groups[user_input[1]] = user_input[2:]
            elif command == "id":
                print "User ID:", self.user_id
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
    if address.startswith("http://"):
        return address
    else:
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
