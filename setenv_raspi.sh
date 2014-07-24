#!/bin/sh

##
# Set cross-compile environment for building the srf05mod and srf05web packages for MIPS
# using the OpenWrt toolchain (build OpenWrt first).
##

# Linux source code location 
# 
# NOTE: you could conde the latest RasPi Kernle from git: 
# git clone https://github.com/raspberrypi/linux.git linux-raspberrypi
#
export LINUX_DIR=$PWD/../linux-raspberrypi

# Add arm-gcc to PATH
#
# NOTE: on Ubuntu, no need for this. Yust do a
# sudo apt-get install gcc-arm-linux-gnueabi make ncurses-dev
#
#export TOOLCHAIN_DIR=/opt/rpi/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian
#export PATH=$TOOLCHAIN_DIR/bin:$PATH

# Set arch to ARM 
export ARCH=arm 

# Set corss-compile prefix to arm-gcc
export CROSS_COMPILE=arm-linux-gnueabi-
