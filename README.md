RCSwitch kenrnel module - operates 433MHz RCSwitches
=====================================================
18.07.2014 Stefan Wendler
sw@kaltpost.de

Credits: 

Most of the parts for sending command to the RCSwitches over RF are
taken from xkonis [raspbarry-remote] (https://github.com/xkonni/raspberry-remote)
 
Project Directory Layout
------------------------

The top-level directory structure of the project looks something like this:

* `Makefile` 		toplevel Make file
* `Makefile.kmod`	include for building kernel modules
* `README.md`		this README
* `setenv_*.sh`		source to set cross-compile environment
* `module`		the kernel module


Prerequisites
-------------

To compile this project the following is needed: 

* OpenWrt checked out and compiled for your target (see [this instructions] (http://wiki.openwrt.org/doc/howto/buildroot.exigence) )


Compilation
------------

**Note:** you need perform a complete OpenWrt build first to succeed with the following steps!

**Check `setenv_*.sh`**

Edit `setenv_*.sh`, make sure `OPENWRT_DIR` points to the location of your OpenWrt base directory.

**Set Cross-Compile Environment**

To set the cross-compile environment use the following:

	source setenv_*.sh

**Compile**

To compile the kernel module:

	make


Installing on the Target
------------------------

Copy the `rcswitch.ko` found in `module/src` to your target (e.g. to `/opt/rcswitch/module/`.

To start the kernel module at bootup, add the following to 
`/etc/rc.local` (before the `exit 0` statement):

	insmod /opt/rcswitch/module/rcswitch.ko

The module knows the following parameters:


	tx_gpio		- Number of GPIO to which TX of 433Mhz sender is connected (default 9/CTS). (int)
	en_gpio		- Number of GPIO to which 3v3 of 433Mhz sender is connected (default 7/RTS). (int)
	pulse_duration	- Duration of a single pulse in usec. (default 350) (int)
	
E.g. if connected to CTS/RTS on the Carambola: 

	insmod /opt/rcswitch/module/rcswitch.ko tx_gpio=9 en_gpio=7
 

Usage
-----

The command format is defined as follows: 

A command string has teh format: AAAAACS

 Where: 

	AAAAA 	- address bits - e.g. '11111'
	C	- channel A, B, C or D - e.g. 'A'
	S	- state 1 (on) or 0 (off) - e.g. '1'
 
Complete command string examples: 
  
 	'11111A0'	- Switch channel A off for address '11111' 
 	'11111B1' 	- Switch channel B on  for address '11111' 

Commands are send to through the kernel modules sysfs entry at: /sys/kernel/rcswitch/command

Examples: 

	echo "11111A0" > /sys/kernel/rcswitch/command
	echo "11111A1" > /sys/kernel/rcswitch/command
 
