##
# Python client for rcswitch-kmod
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

__author__ = 'Stefan Wendler, sw@kaltpost.de'

import optparse as par


SYS_KERNEL_RCSWITCH_COMMAND = '/sys/kernel/rcswitch/command'
SYS_KERNEL_RCSWITCH_POWER = '/sys/kernel/rcswitch/power'


class RCTransmitter(object):

    """
    Class to change the power state of the RF transmitter.
    """

    @property
    def state(self):

        """
        Get the current power state of the RF transmitter.

        :return: 'ON' or 'OFF' or 'UNKNOWN'
        """

        ret = 'UNKNOWN'

        pwr = open(SYS_KERNEL_RCSWITCH_POWER, 'r')

        with pwr:
            value = pwr.readline()

            if value == '1':
                ret = 'ON'
            elif value == '0':
                ret = 'OFF'

            pwr.close()

        return ret

    @state.setter
    def state(self, value):

        """
        Set the power state of the RF transmitter.

        :param value: 'ON', 'on', 'OFF' or 'off'
        """

        pwr = open(SYS_KERNEL_RCSWITCH_POWER, 'w')

        with pwr:
            if value == 'ON' or value == 'on':
                pwr.write('1\n')
            elif value == 'OFF' or value == 'off':
                pwr.write('0\n')
            else:
                pwr.close()
                raise Exception("Unknown transmitter state (only ON/on or OFF/off allowed but got: %s" % value)

            pwr.close()


class RCSwitch(object):

    """
    Class to change the state of a RCSwitch with given address and channel.
    """

    def __init__(self, address, channel):

        self.address = address
        self.channel = channel
        self.last_state = 'UNKNOWN'

    @property
    def state(self):

        """
        Get the current state of the RCSwitch.

        Note: this will most likely always return 'UNKNWON'

        :return: 'ON' or 'OFF' or 'UNKNOWN'
        """

        return self.last_state

    @state.setter
    def state(self, value):

        """
        Set the state of the RCSwitch

        :param value: 'ON', 'on', 'OFF' or 'off'
        """

        cmd = open(SYS_KERNEL_RCSWITCH_COMMAND, 'w')

        with cmd:
            if value == 'ON' or value == 'on':
                cmd.write('%s%s1\n' % (self.address, self.channel))
                self.last_state = 'ON'
            elif value == 'OFF' or value == 'off':
                cmd.write('%s%s0\n' % (self.address, self.channel))
                self.last_state = 'OFF'
            else:
                cmd.close()
                raise Exception("Unknown switch state (only ON/on or OFF/off allowed but got: %s" % value)

            cmd.close()

if __name__ == "__main__":

    """
    Sample usage of the classe RCTransmitter and RCSwitch.
    """

    usage = "%prog [options]"

    parser = par.OptionParser(usage)

    parser.add_option("-t", "--transmitter", action="store_true", help="Transmitter state: ON or OFF")

    parser.add_option("-a", "--address", help="Address of plug")
    parser.add_option("-c", "--channel", help="Channel of plug")

    parser.add_option("-g", "--get",  action="store_true", help="Get state of plug")
    parser.add_option("-s", "--set",  help="Set state of plug: ON or OFF")

    (options, args) = parser.parse_args()

    try:

        if options.transmitter and (options.address or options.channel):

            raise Exception("Either user -t to set/get transmitter state or -a + -c to set/get switch state.")

        elif options.transmitter and (options.get or options.set):

            t = RCTransmitter()

            if options.get:
                print(t.state)
            elif options.set:
                t.state = options.set

        elif options.address and options.channel and (options.get or options.set):

            s = RCSwitch(options.address, options.channel)

            if options.get:
                print(s.state)
            elif options.set:
                s.state = options.set

        else:

            raise Exception("Invalid options given. Use -h for help.")

    except Exception as e:
        print(e.__str__())