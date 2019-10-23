<span style="font-family:univers">

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

`src/data_aggr.py` Collects sensor data and transfers to ground station via Radio and `src/comm_parse.py` via Python's multithreading capability

`src/comm_parse.py` Makes data-driven decisions for operation of launch platform and rocket

`src/origin.py` Runs separate threads for `src/data_aggr.py` and `src/comm_parse.py`, as well as passes data between

</span>
