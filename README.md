# One Time Chat
One time pad based communication.
6.858 Final Project by Jake Barnwell, Andres Perez, Miles Steele

# Security Warning

This is a class project including homebaked crypto.
We are not expert cryptographers.
This project should NOT be treated as secure or vetted.
It may well have bugs or design flaws.

## Device
A user has a device which stores their one time pad and allows
clients to encrypt and decrypt without giving them the whole pad.

## Client
User uses a client running on a computer to communicate with other users.
python client.py 'server address' 'user name'
for example
python client.py localhost:9050 andres

once the client is running you can send message as follows:
send 'recipient' 'message'

recieve messages by entering a newline

## Server
Runs on a server and relays messages between clients.

## Running
To run 2 clients on a single computer run the following commands.

```
    # Create a pad for use between Alice and Bob (see later for
    #  more details on pad generation)
    python device/generate.py "alice" "bob" -m 1
    # Start the message relay server.
    python server/server.py 9050
    # Start Alice's device.
    python device/main.py 9051 --no-display
    # Start Bob's device.
    python device/main.py 9052 --no-display
    # Start Alice's client.
    python client/client.py localhost:9050 localhost:9051 alice
    # Start Bob's client.
    python client/client.py localhost:9050 localhost:9052 bob
```

## Setting up the HRNG (RNG Hardware Device) to seed os /dev/random
(Adapted from http://ubld.it/products/support/truerng-install-guide)
```
# First download the rules and unzip them:
wget http://ubld.it/wp-content/uploads/2014/02/TrueRNG-Linux-udev-rules.zip
unzip TrueRNG-Linux-udev-rules.zip -d /etc/udev/rules.d/
# Then plug in the HRNG and check that it's detected:
ls -l /dev/TrueRNG
# Install rng-tools if you don't already have it:
sudo apt-get install rng-tools
# Edit the config file to make sure that rng-tools correctly references
#  the HRNG device. Open up /etc/default/rng-tools with an editor and
#  add the following line to the file:
HRNGDEVICE=/dev/TrueRNG
# or wherever the TrueRNG (HRNG device) is detected.
# Enable the auto-start of rng-tools:
sudo update-rc.d rng-tools enable
# Start the rng-tools daemon:
sudo /etc/init.d/rng-tools start
# At this point, when the HRNG is plugged in, it feeds entropy to 
#  /dev/random and so /dev/random blocks for a lot less time and
#  can generate random bits more quickly.
# If the HRNG is not working for some reason, try unplugging and
#  plugging it back in and then re-starting rng-tools
# N.B. To view how many bits of entropy are available, use:
/proc/sys/kernel/random/entropy_avail

## Generating the two pads
Pad generation is assumed to be done on a trusted computing device,
e.g. a trusted computer or raspberry pi.

To call the script you can either go to device/ and call
```
python generate.py ...
```
or
```
./generate.py ...
```
The first two arguments are the two users that the pad will
allow to communicate with each other. Generation is symmetric
so order doesn't matter. You must also supply a size for the
generated pad file. To do so, use the `-b`, `-k`, or `-m`
flags and supply the requested size in bytes, kilobytes, or
megabytes, respectively. For example,
```
./generate.py alice bob -b 1000
```
generates two pads to be used by Alice and Bob to communicate
with each other. The pads each have 1000 bytes of random
data.

For more details and options, do
```
./generate.py -h
```

When pads for alice and bob are generated, the following four
files are created:
```
alice.bob.random.store
alice.bob.random.metadata
bob.alice.random.store
bob.alice.random.metadata
```
The alice.bob* files are to be stored on alice's device, and
the bob.alice* files are to be stored on bob's device. The
*.store files store the random data, and the *.metadata files
store metadata about the store files. These metadata files
should not be modified. The system uses advanced techniques
to detect modification of the metadata files.

The respective files must be transferred to the appropriate
devices, e.g. the alice.bob* files should be transferred to
alice's device and stored in alice's device/ directory. It
is assumed that there is a secure way to transport the
files from the trusted generation system to the appropriate
users' devices.
