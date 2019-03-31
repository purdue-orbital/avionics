<span style="font-family:univers">

Flight Computer Repository
==========================

This is the GitHub repository for all scripts pertaining to Purdue Orbital's *Hapsis Project* balloon flight computer. Software is coded in Python for use on a Raspberry Pi Model 3 B+.


## Getting Started ##

### 1. Connecting to the Raspberry Pi ###

Currently, there are four flight computers -- all RPi Model 3 B+, with the name `AvionicsPiX`, where `X` is the system number documented on the Pi packaging. It can be connected to through SSH (Secure Shell) ~~or X11 forwarding (Remote Desktop Protocol)~~. The Pi broadcasts its own network, called `AvionicsPiAPX`, and is used as an access point to SSH into. Users must first power on the Pi (it may take up to a minute to fully boot up). Once the Pi is booted, users should notice a new network available to connect to with the name `AvionicsPiAPX`. Connect to it using the password `PurdueOrbital`. You will now be on a local network containing the Pi and your computer. Internet is available by connecting an ethernet cable to the Pi's port -- this makes it act as an access point to `PAL3.0`.

To connect through SSH, PuTTY can be used (Windows) or the terminal (MacOS). Windows users can also use the command prompt.

*  **Windows Users:** Open the PuTTY client. In the prompt beneath **Host Name (or IP address)** type the following: 

   `pi@192.168.#.1` - # is indicated on the Pi packaging

   Here `pi` denotes the user on the machine, and `192.168.#.1` is the static IP address. You can save this device using the **Save** and **Load** functions. Afterwards, press **Open**. You will be redirected to a terminal, and 
   prompted:

   `pi@192.168.#.1's password: `

   Enter the following password exactly as displayed:
                        
   `PurdueOrbital`
   
   Upon first login, you will be asked something along these lines:
   
   `Authenticity of the host ... cannot be established. Do you ...?`

   Enter `yes`.

   You are now connected to the Pi via SSH. You may also be able to type `ssh pi@192.168.#.1` into the command prompt and proceed as follows, but I'm not 100% on that. If connection fails, see **Troubleshooting**.

*  **MacOS Users:** {Not yet determined}


## Troubleshooting ##

*  ### Unable to connect to the Pi (can't reach server) ###

   Check that your computer has properly established connection to the network. On Windows, open the command prompt. Enter `ipconfig`, and under the section labelled `Wireless LAN adapter Wi-Fi` verify that `IPv4 Address` is of the 
   form `192.168.#.XXX`, where `XXX` is any number from 2 to 20. If it isn't, your computer hasn't properly acquired a new local IP. In this case, either reboot your machine or type the following commands:

   `ipconfig /release`

   `ipconfig /flushdns`

   `ipconfig /renew`

   This will refresh your connection settings without requiring a system reboot. Renewing may take a minute or two, so don't be alarmed if it appears to be stall on `Windows IP Configuration`. Afterwards, verify that your IP is now 
   correctly configured by repeating the steps above.

### Please report any further problems to appropriate person(s). ###


## Setting Up a New Pi ##
   ### Resources ###
   [How to set up Pi access to PAL3.0 (or other relevant commercial Wifi)](https://imgur.com/euypelW)
   
   [How to set up Pi as an access point with an Ethernet bridge](https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md)
   *  [How to correct hostapd.service masked error](https://github.com/raspberrypi/documentation/issues/1018#issuecomment-471335938)
</span>
