Flight Computer Repository
==========================

This is the GitHub repository for all scripts pertaining to Purdue Orbital's *Hapsis Project* balloon flight computer. Software is coded in Python for use on a Raspberry Pi Model 3 B+.


## Getting Started ##

### 1. Connecting to the Raspberry Pi ###

Currently, our only flight computer is the RPi Model 3 B+, with the name `AvionicsPi`. It can be connected to through either SSH (Secure Shell) or X11 forwarding (Remote Desktop Protocol).

To connect through SSH, PuTTY can be used (Windows) or the terminal (MacOS). Windows users can also use the command prompt.

**Windows Users:** Open the PuTTY client. In the prompt beneath **Host Name (or IP address)** type the following: 

*If located in ARMS* `pi@10.186.12.50`

Here `pi` denotes the user on the machine, and `10.186.12.50` is the public IP address. You can save this device using the **Save** and **Load** functions. Afterwards, press **Open**. You will be redirected to a terminal, and prompted:

`pi@10.XXX.XXX.XXX's password: `

Enter the following password exactly as displayed:
                        
`PurdueOrbital`

You are now connected to the Pi via SSH. If connection fails, the IP may have changed. Since each building around Purdue technically has a different router controlling it, the Pi will have a different IP based on location. Static IP has yet to be established.

**MacOS Users:** <Not yet determined>