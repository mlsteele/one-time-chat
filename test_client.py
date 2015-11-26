if __name__ == "__main__":
    
    server_address = "localhost:9050"
    alice = OTC_Client(server_address, "alice")
    bob = OTC_Client(server_address, "bob")
    print "Sending 'HELLO' to alice"
    alice.send("HELLO", "bob")
    alice.send("how are you?", "bob")
    messages = bob.get_messages(0)[u'messages']
    for message in messages:
        print message[u'sender_uid'] + ":" + message[u'contents']
    assert bob.get_messages(0) == "HELLO"
