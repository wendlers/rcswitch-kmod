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

import bottle as bot
import logging as log
import optparse as par
import config as cfg

from daemonize import Daemonize


def switch_send_command(command):

    """
    """

    cmd = open(cfg.SYS_KERNEL_RCSWITCH_COMMAND, 'w')

    with cmd:
        cmd.write('%s\n' % command)
        cmd.close()


class Server:

    def __init__(self):
        """


        :type self: object
        """

        try:

            log.basicConfig(level=cfg.LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s',
                            filename=cfg.LOG_FILE)
            log.info("%s: %s", cfg.APP, cfg.VERSION)

            log.debug("Setting up routing")
            self.setup_routing()

            log.debug("Starting HTTP server")
            log.info("HTTP Server: %s:%s (%s)" % (cfg.HTTP_HOST, cfg.HTTP_PORT, cfg.HTTP_DOC_ROOT))
            bot.run(host=cfg.HTTP_HOST, port=cfg.HTTP_PORT, quiet=False)

        except Exception as e:
            log.error("ABORTING - %s" % e.__str__())
            exit(1)

    def setup_routing(self):
        """


        :type self: object
        :rtype : object
        """

        bot.route('/switch/<address>/<channel>', 'POST', self.handle_switch_command)

        bot.route('/<subdir>/<filename:path>', 'GET', self.handle_static)
        bot.route('/', 'GET', self.handle_index)

    def handle_switch_command(self, address, channel):
        """

        :type name: object
        """

        state = bot.request.forms.get('state')

        if not state or len(state) == 0:
            log.error("Missing parameter: state")
            return bot.abort(code=400, text="Missing parameter: state")

        try:
            command = "%s%s%s" % (address, channel, state)
            log.info("sending command: %s" % command)
            switch_send_command(command)
        except Exception as e:
            log.error("SYSFS - %s" % e.__str__())
            return bot.abort(code=400, text=e.__str__())

        return bot.abort(code=200, text="State set to: %s" % state)

    def handle_index(self):
        """

        :param filename:
        :return:
        """

        return bot.static_file("index.html", root=cfg.HTTP_DOC_ROOT)

    def handle_static(self, subdir, filename):
        """

        :param filename:
        :return:
        """

        path = subdir + "/" + filename

        return bot.static_file(path, root=cfg.HTTP_DOC_ROOT)


if __name__ == "__main__":

    usage = "usage: %prog [options]"

    parser = par.OptionParser(usage)
    parser.add_option("-d", "--daemonize", action="store_true",
                      help="run as daemon")
    parser.add_option("-p", "--pid", dest="pid", default=cfg.PID,
                      help="pid file when run as daemon")
    parser.add_option("-l", "--logfile", dest="logfile", default=cfg.LOG_FILE,
                      help="log file")
    parser.add_option("-L", "--loglevel", dest="loglevel", default="debug",
                      help="log level (debug|info|warning|error)")
    parser.add_option("-H", "--host", dest="host", default=cfg.HTTP_HOST,
                      help="host name/ip to bind server to")
    parser.add_option("-P", "--port", dest="port", default=cfg.HTTP_PORT,
                      help="port to bind server to")
    parser.add_option("-D", "--docroot", dest="docroot", default=cfg.HTTP_DOC_ROOT,
                      help="document root of server")

    (options, args) = parser.parse_args()

    if options.loglevel == "debug":
        cfg.LOG_LEVEL = log.DEBUG
    elif options.loglevel == "info":
        cfg.LOG_LEVEL = log.INFO
    elif options.loglevel == "warning":
        cfg.LOG_LEVEL = log.WARNING
    elif options.loglevel == "error":
        cfg.LOG_LEVEL = log.ERROR
    else:
        print("Unkown log level: %s" % options.loglevel)
        exit(1)

    # overwrite defaults ...
    cfg.LOG_FILE = options.logfile
    cfg.HTTP_HOST = options.host
    cfg.HTTP_PORT = int(options.port)
    cfg.HTTP_DOC_ROOT = options.docroot

    if options.daemonize:
        daemon = Daemonize(app=cfg.APP, pid=options.pid, action=Server)
        daemon.start()
    else:
        Server()

