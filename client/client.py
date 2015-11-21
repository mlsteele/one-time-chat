import requests
import sys
class OTC_Client(object):
    ## A client is initialized with the address of the server it intends to connect to
    
    ## TODO: fix the initialization with pad. Client shouldn't get access to pad
    def __init__(self,server_address,device_id):
        self.encrypt_index = 0 
        self.device_id = device_id
        self.decrypt_index = None # TODO: what is a good value for the decrypt index?
        self.connect(server_address)
        raise NotImplementedError("TODO: write a client")
    def send(self,message,target):
        payload = {'message':message,'target':target}
        r = request.post(self.server_address,data=payload)
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
        payload = {'message':"connect"}
        r = request.post(self.server,data=payload)
        #TODO: handle response from server
    def readFromDevice():
        raise NotImplementedError("TODO: clients need to be able to read from their device")
    #TODO: http form maybe
    def getMessages(self,name,cursor):
        raise NotImplementedError("TODO: clients need to be able to poll messages")
if __name__ == "__main__":
    
    if (len(sys.argv)<3):
        print "ERROR: correct usage is client.py [server_address] [pad_file]"
    server_address = sys.argv[1]
    pad_file = sys.argv[2]
    client = OTC_Client(server_address,device_id)
    client.send("HELLO","alice")
