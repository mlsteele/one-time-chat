import requests
import sys
class OTC_Client(object):
    def __init__(self,server_address,pad):
        self.encrypt_index = 0 
        self.pad = pad
        self.decrypt_index = len(pad)
        self.connect(server_address)
        raise NotImplementedError("TODO: write a client")
    def send(self,message,target):
        payload = {'message':message,'target':target}
        r = requets.post(self.server_address,data=payload)
        raise NotImplementedError("TODO: write send method")
    def recieve(self):
        raise NotImplementedError("TODO: write recieve")
    def decrypt(self,message, pad_index):
        ## TODO: give ability of default index
        raise NotImplementedError("TODO: clients need to decrypt messages")
    def encrypt(self,encrypt, pad_index):
        raise NotImplementedError("TODO: clients need to encrypt messages")
    def connect(self,server_address):
        self.server_address = server_address
        raise NotImplementedError("TODO:clients need to be able to connect to server")
if __name__ == "__main__":
    
    if (len(sys.argv)<3):
        print "ERROR: correct usage is client.py [server_address] [pad_file]"
    server_address = sys.argv[1]
    pad_file = sys.argv[2]
    client = OTC_Client(server_address,pad_file)
