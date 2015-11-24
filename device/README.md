# Device Software

Software to run on the pad device.
The pad device is a separate device (raspberry pi) from the one running the client software.
The device software can also be run on the same system as the client for convenience.

# Network Setup
In order to set up the network between the device and client follow these steps.

## Setup link
Connect an ethernet cable between the device rpi and client laptop.
It need not be a crossover on modern hardware. It worked for me with a normal cable on a rpi B and a 2014 laptop.

## On the device
Set up a static IP of 10.0.0.2 with no gateway.

/etc/network/intefaces should look something like this.
The important bit is the static eth0 in the middle.
```
auto lo

iface lo inet lopback

iface eth0 inet static
address 10.0.0.2
netmask 255.255.255.0

allow-hotplug wlan0
iface wlan0 inet manual
wpa-roam /etc/wpa_supplicant/wpa_supplicatn.conf
iface default inet dhcp
```

## On the client
Set up a fixed IP over ethernet of 10.0.0.1 with no gateway.
This can be done in the Ubuntu network manager.
Check the box that says something like "Only use this connection for stuff in its subnet."

## Testing the setup
Pings should work now.
```
ping 10.0.0.2 # from the laptop
ping 10.0.0.1 # from the rpi
```

# Useful Resources
[https://askubuntu.com/questions/22835/how-to-network-two-ubuntu-computers-using-ethernet-without-a-router](AskUbuntu: How to network two ubuntu computers using ethernet without a router)
