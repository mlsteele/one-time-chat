# One Time Chat
One time pad based communication.
6.858 Final Project by Jake Barnwell, Andres Perez, Miles Steele

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

# Setting up the HRNG (RNG Hardware Device)
(Adapted from http://ubld.it/products/support/truerng-install-guide)
First download the rules and unzip them:

wget http://ubld.it/wp-content/uploads/2014/02/TrueRNG-Linux-udev-rules.zip

unzip TrueRNG-Linux-udev-rules.zip -d /etc/udev/rules.d/
Then plug in the HRNG and check that it's detected:
ls -l /dev/TrueRNG
Install rng-tools if you don't already have it:
sudo apt-get install rng-tools
Edit the config file to make sure that rng-tools correctly references
the HRNG device. Open up /etc/default/rng-tools with an editor and
add the following line to the file:
HRNGDEVICE=/dev/TrueRNG
or wherever the TrueRNG (HRNG device) is detected
Enable the auto-start of rng-tools:
sudo update-rc.d rng-tools enable
Start the rng-tools daemon:
sudo /etc/init.d/rng-tools start
At this point, when the HRNG is plugged in, it feeds entropy to 
/dev/random and so /dev/random blocks for a lot less time and
can generate random bits more quickly.
If the HRNG is not working for some reason, try unplugging and
plugging it back in and then re-starting rng-tools
N.B. To view how many bits of entropy are available, use:
/proc/sys/kernel/random/entropy_avail
