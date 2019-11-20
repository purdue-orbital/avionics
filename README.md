<span style="font-family:univers">

Flight Computer Repository
==========================

This is the GitHub repository for all software pertaining to Purdue Orbital's *Hapsis Project* flight computer. Programs are coded in Python for use on a Raspberry Pi Model 3 B+.


## Getting Started ##

### 1. Connecting to the Raspberry Pi ###

Currently, there are two flight computers -- both RPi Model 3 B+. Connection can either be local, or over `PAL3.0` using ethernet. 

//NOTE: Currently, WiFi is not configured for these Pis, so this method isn't functional.

To connect through SSH, PuTTY can be used (Windows) or the terminal (MacOS). Windows users can also use the command prompt. On the Pi, type `ifconfig | grep 'inet '`. The output should look something like:

`$ ifconfig | grep 'inet '`  

        inet 127.0.0.1  netmask 255.0.0.0
        inet 10.186.110.99  netmask 255.255.240.0  broadcast 10.186.111.255
        
The Pi's local IP address for `PAL3.0` is preceded by `inet`, and on the same line as `broadcast`. In this example, it is `10.186.110.99`.

Next, ask an avionics member to add your user to each computer. Choose a password and a short username (these will be your login credentials each time). Enter
`sudo adduser <username>`
Type your first and last name as prompted -- all other prompts can be skipped. Next, enter
`sudo usermod -aG sudo <username>`
After this, proceed to your OS for instructions on connecting.

* ### Windows Users ###
On Windows, there are two options for SSHing into the Pi: PuTTY or the command prompt. PuTTY is generally more compatible with remote shells, so it's the recommended connection method. After launching PuTTY, enter `<username>@<IP>` into the *Host Name* box and click *Open*.
You will be prompted to enter your password; once you do, you will be connected.

* ### MacOS Users ###
In the terminal, enter `ssh <username>@<IP>`. You will be prompted to enter your password; once you do, you will be connected.

### 2. Cloning the Repository and Staying Up-to-Date ###

Orbital uses Git for version control of software. This is achieved by using separate branches for different tasks. The _master_ branch contains the most recent functional version of the repository. Changes can't be made directly to this branch; to make changes, a new branch must be made and edited, followed by a *Pull Request*.

The first time you log in, enter
`git clone https://github.com/purdue-orbital/avionics.git`
This will clone the most recent version of the repository, creating a local version on your profile. Before you do any work, always type `git pull`. This will ensure your version of the _master_ branch is the most up-to-date. Next, type `git branch <name>`, where `<name>` is a descriptive identifier for the task you are working on. Finally, type `git checkout <name>`.

The working branch is now _<name>_ instead of _master_. Once changes are made, to add them to _master_ type `git commit --interactive`. Select only the files you want to change on master, then exit and enter a descriptive message into the `COMMITMSG` file that is opened.

Finally, enter `git push --set-upstream origin <name>` the first time you push to connect your local version to a remote branch (after this is set, you can use `git push`). Enter your Github credentials when prompted: your work should now be on Github!

Go to your branch on Github and click *Make a Pull Request* when you're ready to add your changes to the _master_ branch. Only do this when the new additions have been fully debugged and tested!

Once your task had been completed and committed to the _master_ branch, enter `git checkout master` on the Pi, followed by `git branch -D <name>` to remove the old branch. Lastly, type `git pull` to re-update your version of master and begin the process anew.

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



Balloon Flight Computer
=======================

Below you will find a simple explanation of this system and its subsequent processes.

### Components ###
   1. Raspberry Pi 3B+: Flight computer, running Raspbian Lite. Software programmed in Python
   2. MPU9250/MS5611: Combined accelerometer/gyroscope, along with a pressure sensor (respectively).
   3. NEO 7M GPS: GPS unit
   4. DS3231 RTC: Millisecond precision for time
   5. Radio: Data transfer to Ground Station via their API through USB Serial
   
## Interaction ##

`src/sensors.py` Collects sensor data and transfers to ground station via Radio and `src/control.py` via Python's multithreading capability

`src/control.py` Makes data-driven decisions for operation of launch platform and rocket

`src/balloon.py` Runs separate threads for `src/sensors.py` and `src/control.py`, as well as passes data between

</span>
