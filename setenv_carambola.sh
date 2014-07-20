#!/bin/sh

##
# Set cross-compile environment for building the srf05mod and srf05web packages for MIPS
# using the OpenWrt toolchain (build OpenWrt first).
##

# Base directory of OpenWrt
export OPENWRT_DIR=$PWD/../brick-o-lage/carambola/

# Linux source code location 
export LINUX_DIR=$OPENWRT_DIR/build_dir/linux-ramips_rt305x/linux-3.3.8

# Staging dir from OpenWrt build
export STAGING_DIR=$OPENWRT_DIR/staging_dir

# Add mips-gcc to PATH
export PATH=$STAGING_DIR/toolchain-mipsel_r2_gcc-4.7-linaro_uClibc-0.9.33.2/bin:$PATH

# Set arch to MIPS
export ARCH=mips

# Set corss-compile prefix to mips-gcc
export CROSS_COMPILE=mipsel-openwrt-linux-
