class OTC_Client(object):
    def __init__(self):

        raise NotImplementedError("TODO: write a client")
    def send(self,message):
        payload = {'message':message}
        r = requets.post(self.server_address,data=payload)
        raise NotImplementedError("TODO: write send method")
    def recieve(self):
        raise NotImplementedError("TODO: write recieve")
    def decrypt(self,message, pad_index=current_index):
        raise NotImplementedError("TODO: clients need to decrypt messages")
    def encrypt(self,encrypt):
        raise NotImplementedError("TODO: clients need to encrypt messages")
    def connect(self,server_address):
        self.server_address = server_address
        raise NotImplementedError("TODO:clients need to be able to connect to server")
if __name__ == "__main__":
    client = OTC_Client()
