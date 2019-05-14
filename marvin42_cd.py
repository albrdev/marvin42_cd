#!/usr/bin/python3

import sys, time, argparse, configparser, signal, socket, struct
from chirpsdk import ChirpConnect, CallbackSet

from modules.pathtools import *
from modules.networking import PacketHeader
from modules.daemon import Daemon
import marvin42_types
from marvin42_types import *

class Callbacks(CallbackSet):
    def __init__(self, config):
        self.host = socket.getaddrinfo(config['remote']['bind_address'], int(config['remote']['bind_port']), socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.host = self.host[0][4]

        self.timeout = config.get('remote', 'timeout', fallback=None)
        if self.timeout is not None:
            self.timeout = int(self.timeout)

    def on_receiving(self, channel):
        print("Chirp: Incoming data [ch{ch}]...".format(ch=channel))

    def on_received(self, payload, channel):
        if payload is not None:
            self.process_data(payload);
        else:
            print("Chirp: Decoding failed")

    def process_data(self, data) -> bool:
        print("Chirp: Data received: {d}".format(d=data))

        try:
            type = CommandID(data[0])
        except ValueError:
            print("Chirp: Invalid packet type: {t}".format(t=type), file=sys.stderr)
            return False

        data = data[1:]
        if type == CommandID.MOTORSPEED:
            data = struct.unpack('!ii', data)
            self.forward_packet_motorspeed(data)
        elif type == CommandID.MOTORSETTINGS:
            data = struct.unpack('!i', data)
            self.forward_packet_motorsettings(data)
        else:
            print("Chirp: Command ID not implemented: {t}".format(t=type), file=sys.stderr)

        return True

    def forward_packet_motorspeed(self, data):
        data = struct.pack(PacketMotorSpeed.FORMAT, data[0], data[1])
        header = struct.pack(PacketHeader.FORMAT, int(CommandID.MOTORSPEED), PacketMotorSpeed.SIZE)
        self.forward_data(header, data)

    def forward_packet_motorsettings(self, data):
        data = struct.pack(PacketMotorSettings.FORMAT, data[0])
        header = struct.pack(PacketHeader.FORMAT, int(CommandID.MOTORSETTINGS), PacketMotorSettings.SIZE)
        self.forward_data(header, data)

    def forward_data(self, header: PacketHeader, data) -> bool:
        s = socket.socket()
        s.settimeout(self.timeout)

        s.connect(host)
        s.send(header)
        s.send(data)

        try:
            response = s.recv(PacketHeader.SIZE)
        except socket.timeout:
            print('Remote: Response timed out')
            s.close()
            return False
        else:
            response = PacketHeader._make(struct.unpack(PacketHeader.FORMAT, response))
            print("Remote: {d}".format(d=response))

            s.close()
            return True

class marvin42_cd(Daemon):
    def __init__(self, args, main_config, chirp_config):
        self.is_init = False
        print('init1:', self.is_init, file=sys.stderr)
        super(marvin42_cd, self).__init__(main_config['daemon']['user'], main_config['daemon']['pid_file'], main_config['daemon']['log_default'], main_config['daemon']['log_error'])

        print('init2:', self.is_init, file=sys.stderr)
        self.chirp = ChirpConnect(chirp_config['default']['app_key'], chirp_config['default']['app_secret'], chirp_config['default']['app_config'])
        adi = main_config.get('chirp', 'audiodevice_index', fallback=None)
        self.chirp.audio.input_device = int(adi) if adi != None else adi
        self.chirp.set_callbacks(Callbacks(main_config))
        self.chirp.start(send=False, receive=True)
        self.is_init = True

    def __del__(self):
        super(marvin42_cd, self).__del__()
        print('init3:', self.is_init, file=sys.stderr)
        if self.is_init:
            self.chirp.stop()

    def handle_signals(self, num, frame):
        {
            signal.SIGINT: lambda: sys.exit(0), 
            signal.SIGTERM: lambda: sys.exit(0)
        }.get(num, lambda *args: None)()

    def run(self):
        time.sleep(0.1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print ("Usage: {app} start|stop|restart".format(app=sys.argv[0]))
        sys.exit(1)

    args = argparse.ArgumentParser(
        description="marvin42 chirp daemon",
        epilog="marvin42, 2019"
    )

    args.add_argument('operation', type=str, help="Operation to perform", metavar='operation')
    args.add_argument('-c', '--config', dest='config', action=FullPath, type=str, default=pathtools.fullpath('~/.marvin42rc'), help="Custom config file (optional)", metavar='filepath')
    args = args.parse_args()

    main_config = configparser.ConfigParser()
    main_config.read(args.config)

    chirp_config = configparser.ConfigParser()
    chirp_config.read(pathtools.fullpath(main_config['chirp']['config_path']))

    daemon = marvin42_cd(args, main_config, chirp_config)
    if args.operation == 'start':
        daemon.start()
    elif args.operation == 'stop':
        daemon.stop()
    elif args.operation == 'restart':
        daemon.restart()
    else:
        print ("Unknown operation \'{op}\'".format(op=sys.argv[1]))
        sys.exit(1)
