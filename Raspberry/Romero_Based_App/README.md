# RaspberryPi3 application

This folder contains the source files of the RaspberryPi3 application.

## Build the application on the RPi3

First, copy the acm-rpi-app folder into the RaspberryPi.

CMake is used as build system to compile the application.
To build it, execute the following commands on the RaspberryPi:
```
cd acm-rpi-app
mkdir build && cd build
cmake ..
make
./acm-rpi-app
```

## Cross-compile the application from a Linux desktop

If you have the acm x86_64 SDK installed for example in /opt/acm/1.0/, you can cross-compile the application from a Linux OS with the following commands:
```
git clone http://github.com/juliencombattelli/ProjectRomero
cd ProjectRomero/RaspberryPi/acm-rpi-app
source /opt/acm/1.0/environment-setup-cortexa7hf-neon-vfpv4-poky-linux-gnueabi
mkdir build && cd build
cmake ..
make
```

Then, you can transfer the executable to the RaspberryPi.

## Cross-compile the application from a Windows desktop

ToDo
