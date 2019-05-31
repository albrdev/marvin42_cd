#!/usr/bin/env python3

"""
@author: albrdev
@email: albrdev@gmail.com
@date: 2019-05-13
"""

import sys, os, time, argparse, configparser, signal
from chirpsdk import ChirpConnect

from modules.pathtools import *
from modules.daemon import Daemon
from chirp_callbacks import ChirpCallbacks

class marvin42_cd(Daemon):
    """
    marvin42 Chirp Daemon
    Receives Chirp audio and redirects its data to an external device
    """
    __slots__ = ['chirp']

    def __init__(self):
        self.chirp = None
        super(marvin42_cd, self).__init__(main_config['daemon']['user'], main_config['daemon']['pid_file'], main_config['daemon']['log_default'], main_config['daemon']['log_error'])

    def cleanup(self):
        """
        Stops Chirp SDK, if initialized
        """
        if self.chirp is not None:
            self.chirp.stop()

        super(marvin42_cd, self).cleanup()

    def init(self):
        """
        Setting up Chirp SDK
        """
        super(marvin42_cd, self).init()

        self.chirp = ChirpConnect(chirp_config['default']['app_key'], chirp_config['default']['app_secret'], chirp_config['default']['app_config']) # Using chirp config file (.chirprc)
        adi = main_config.get('chirp', 'audiodevice_index', fallback=None) # Get audio device index, if any, otherwise None (which will make Chirp choose one automatically)
        self.chirp.audio.input_device = int(adi) if adi != None else adi # Convert string to int
        self.chirp.set_callbacks(ChirpCallbacks(main_config)) # Chirp needs an entire class with specifically named callback methods i.e. (see class 'ChirpCallbacks')
        self.chirp.start(send=False, receive=True) # Start listening for Chirps. We don't need to send anything

    def signal_handler(self, num, frame):
        """
        Signal handler
        """
        {
            signal.SIGINT: lambda: sys.exit(0), 
            signal.SIGTERM: lambda: sys.exit(0),
            signal.SIGHUP: lambda: self.restart()
        }.get(num, lambda *args: None)()

    def restart(self):
        """
        Overridden restart method from base class.
        This was just to test if Chirp could be able to listen for Chirps again after a specific time (Chirp daemon fails to (re)initialize Chirp SDK when calling this method. The acctual problem is probably due to the old Python process is still running while the new one starts (Use 'systemd' instead?))
        It did'nt work. So I left this here for a heads-up
        """
        self.stop()
        time.sleep(5)
        self.start()

    def run(self):
        """
        Overriden daemon main loop
        Nothing to be handled here right now
        """
        time.sleep(0.1)

if __name__ == '__main__':
    global main_config
    global chirp_config

    if len(sys.argv) < 2:
        print ("Usage: {app} start|stop|restart".format(app=sys.argv[0]))
        sys.exit(1)

    args = argparse.ArgumentParser(
        description="marvin42 chirp daemon",
        epilog="marvin42, 2019"
    )

    args.add_argument('operation', type=str, help="Operation to perform", metavar='operation')
    args.add_argument('-c', '--config', dest='config', action=FullPath, type=str, default=pathtools.fullpath('/etc/marvin42_cdrc'), help="Custom config file (optional)", metavar='filepath')
    args = args.parse_args()

    main_config = configparser.ConfigParser()
    main_config.read(args.config)

    chirp_config = configparser.ConfigParser()
    chirp_config.read(pathtools.fullpath(main_config['chirp']['config_path']))

    daemon = marvin42_cd()
    if args.operation == 'start':
        daemon.start()
    elif args.operation == 'stop':
        daemon.stop()
    elif args.operation == 'restart':
        daemon.restart()
    else:
        print ("Unknown operation \'{op}\'".format(op=sys.argv[1]))
        sys.exit(1)
