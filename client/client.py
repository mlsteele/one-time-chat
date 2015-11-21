class OTC_Client(object):
    def __init__(self):
        raise NotImplementedError("TODO: write a client")
    def send(message):
        raise NotImplementedError("TODO: write send method")
    def recieve():
        raise NotImplementedError("TODO: write recieve")
    def decrypt(message, pad_index=current_index):
        raise NotImplementedError("TODO: clients need to decrypt messages")
    def encrypt(encrypt):
        raise NotImplementedError("TODO: clients need to encrypt messages")
    def connect():
        raise NotImplementedError("TODO:clients need to be able to connect to server")
if __name__ == "__main__":
    client = OTC_Client()
