#!/usr/bin/env python3

"""
@author: albrdev
@email: albrdev@gmail.com
@date: 2019-05-19
"""

import sys, socket, struct
from chirpsdk import CallbackSet

from modules.networking import PacketHeader
from modules.marvin42 import *

class ChirpCallbacks(CallbackSet):
    """
    Chirp callback class
    Contains methods called by ChirpConnect class when an event triggers
    These methods handles incomming/received chirp
    """
    def __init__(self, config):
        self.host = socket.getaddrinfo(config['remote']['bind_address'], int(config['remote']['bind_port']), socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.host = self.host[0][4]

        self.timeout = config.get('remote', 'timeout', fallback=None) # Set timeout(seconds) for socket.send()
        if self.timeout is not None:
            self.timeout = int(self.timeout)

    def on_receiving(self, channel):
        """
        Called when incoming Chirp audio is detected and receiving
        """
        print("Chirp: Incoming data [ch{ch}]...".format(ch=channel))

    def on_received(self, payload, channel):
        """
        Called when incoming Chirp audio has been completly received
        """
        if payload is not None: # Data may still be invalid
            self.process_data(bytes(payload));
        else:
            print("Chirp: Decoding failed")

    def process_data(self, data: bytes) -> bool:
        """
        Process a, to chirp, valid payload of data
        """
        print("Chirp: Data received: {d}".format(d=data))

        # Data may still not be a valid 'marvin42 packet'
        # Check if first byte is a valid 'CommandID'
        try:
            type = CommandID(data[0])
        except ValueError:
            print("Chirp: Invalid packet type: {t}".format(t=type), file=sys.stderr)
            return False

        data = data[1:] # Strip away first byte and forward to remote machine (Raspberry Pi)
        print("Chirp: Forwarding data: {d} ({t})".format(t=type, d=data))
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
        data = struct.pack(PacketMotorSpeed.FORMAT, data[0], data[1]) # Pack data to byte string, including byte order
        header = struct.pack(PacketHeader.FORMAT, int(CommandID.MOTORSPEED), PacketMotorSpeed.SIZE) # Pack header to byte string, including byte order
        self.forward_data(header, data)

    def forward_packet_motorstop(self):
        header = struct.pack(PacketHeader.FORMAT, int(CommandID.MOTORSTOP), 0) # Pack header to byte string, including byte order, since this particular command doesnt need any parameters, like speed, we only need to send one byte i.e. the command 'type'
        self.forward_data(header)

    def forward_packet_motorsettings(self, data):
        data = struct.pack(PacketMotorSettings.FORMAT, data[0]) # Pack data to byte string, including byte order
        header = struct.pack(PacketHeader.FORMAT, int(CommandID.MOTORSETTINGS), PacketMotorSettings.SIZE) # Pack header to byte string, including byte order
        self.forward_data(header, data)

    def forward_data(self, header: PacketHeader, data=None) -> bool:
        """
        Send header and data (if any) packet to a remote machine
        """
        s = socket.socket()
        s.settimeout(self.timeout) # Timeout for socket

        s.connect(self.host)
        s.sendall(header) # Send all data (wait for all data to be sent)
        if data is not None:
            s.sendall(data)

        # Wait for a response
        # Response packet should have 'type' of either PacketID.FALSE (0) or PacketID.TRUE (1) (Depending on how the remote machine handled the previous sent command). We currently only print that out for debug/log purposes
        try:
            response = s.recv(PacketHeader.SIZE)
        except socket.timeout:
            # Remote machine never got the packet (probably got cut off/crashed)
            print('Remote: Response timed out')
            s.close()
            return False
        else:
            response = PacketHeader._make(struct.unpack(PacketHeader.FORMAT, response))
            print("Remote: {d}".format(d=response))

            s.close()
            return True
        return True
