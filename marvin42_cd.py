#!/usr/bin/env python3

import sys, os, time, argparse, configparser, signal
from chirpsdk import ChirpConnect

from modules.pathtools import *
from modules.daemon import Daemon
from chirp_callbacks import ChirpCallbacks

class marvin42_cd(Daemon):
    __slots__ = ['is_init', 'chirp']

    def __init__(self):
        self.is_init = False
        super(marvin42_cd, self).__init__(main_config['daemon']['user'], main_config['daemon']['pid_file'], main_config['daemon']['log_default'], main_config['daemon']['log_error'])

    def cleanup(self):
        if self.is_init:
            self.chirp.stop()

        super(marvin42_cd, self).cleanup()

    def init(self):
        super(marvin42_cd, self).init()

        self.chirp = ChirpConnect(chirp_config['default']['app_key'], chirp_config['default']['app_secret'], chirp_config['default']['app_config'])
        adi = main_config.get('chirp', 'audiodevice_index', fallback=None)
        self.chirp.audio.input_device = int(adi) if adi != None else adi
        self.chirp.set_callbacks(ChirpCallbacks(main_config))
        self.chirp.start(send=False, receive=True)
        self.is_init = True

    def signal_handler(self, num, frame):
        {
            signal.SIGINT: lambda: sys.exit(0), 
            signal.SIGTERM: lambda: sys.exit(0),
            signal.SIGHUP: lambda: self.restart()
        }.get(num, lambda *args: None)()

    def restart(self):
        self.stop()
        time.sleep(5)
        self.start()

    def run(self):
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
