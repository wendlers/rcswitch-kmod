##
# Python daemon for rcswitch-kmod
#
# Copyright (c) 2014 Stefan Wendler
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

__author__ = 'Stefan Wendler'

import logging as log

APP = "swsrv"
VERSION = "0.0.1 alpha"

PID = '/var/run/swsrv.pid'

HTTP_HOST = '0.0.0.0'
HTTP_PORT = 8080
HTTP_DOC_ROOT = '/opt/swsrv/www'

LOG_LEVEL = log.DEBUG
LOG_FILE = None

SYS_KERNEL_RCSWITCH_COMMAND = '/sys/kernel/rcswitch/command'