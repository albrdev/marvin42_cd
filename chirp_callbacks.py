#!/usr/bin/env python3

import sys, socket, struct
from chirpsdk import CallbackSet

from modules.networking import PacketHeader
from modules.marvin42 import *

class ChirpCallbacks(CallbackSet):
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
            self.process_data(bytes(payload));
        else:
            print("Chirp: Decoding failed")

    def process_data(self, data: bytes) -> bool:
        print("Chirp: Data received: {d}".format(d=data))

        try:
            type = CommandID(data[0])
        except ValueError:
            print("Chirp: Invalid packet type: {t}".format(t=type), file=sys.stderr)
            return False

        data = data[1:]
        print("Chirp: Forwarding: {d} ({t})".format(t=type, d=data))
        if type == CommandID.MOTORSETTINGS:
            data = struct.unpack(PacketMotorSettings.FORMAT, data)
            self.forward_packet_motorsettings(data)
        elif type == CommandID.MOTORSPEED:
            data = struct.unpack(PacketMotorSpeed.FORMAT, data)
            self.forward_packet_motorspeed(data)
        elif type == CommandID.MOTORSTOP:
            self.forward_packet_motorstop()
        else:
            print("Chirp: Command ID not implemented: {t}".format(t=type), file=sys.stderr)

        return True

    def forward_packet_motorspeed(self, data):
        data = struct.pack(PacketMotorSpeed.FORMAT, data[0], data[1])
        header = struct.pack(PacketHeader.FORMAT, int(CommandID.MOTORSPEED), PacketMotorSpeed.SIZE)
        self.forward_data(header, data)

    def forward_packet_motorstop(self):
        header = struct.pack(PacketHeader.FORMAT, int(CommandID.MOTORSTOP), 0)
        self.forward_data(header)

    def forward_packet_motorsettings(self, data):
        data = struct.pack(PacketMotorSettings.FORMAT, data[0])
        header = struct.pack(PacketHeader.FORMAT, int(CommandID.MOTORSETTINGS), PacketMotorSettings.SIZE)
        self.forward_data(header, data)

    def forward_data(self, header: PacketHeader, data=None) -> bool:
        s = socket.socket()
        s.settimeout(self.timeout)

        s.connect(self.host)
        s.send(header)
        if data is not None:
            s.send(data)

        #try:
        #    response = s.recv(PacketHeader.SIZE)
        #except socket.timeout:
        #    print('Remote: Response timed out')
        #    s.close()
        #    return False
        #else:
        #    response = PacketHeader._make(struct.unpack(PacketHeader.FORMAT, response))
        #    print("Remote: {d}".format(d=response))

        #    s.close()
        #    return True
        return True
