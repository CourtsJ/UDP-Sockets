#UDP Receiver
import socket
import pickle
port_list = []
port_names = ["r_in","r_out"]
i = 0
while len(port_list) < 2:
    port_input = int(input("Enter Port Number for {}: ".format(port_names[i])))
    if ((port_input > 1024 and port_input < 64000) and (port_input not in port_list)):
        port_list.append(port_input)
        i += 1
    else:
        print("Must be unique and between 1024 and 64000")
port_list_channel = []
while len(port_list_channel) < 1:
    port_input = int(input("Enter cr_in Port Number: "))
    if ((port_input > 1024 and port_input < 64000) and (port_input not in port_list)):
        port_list_channel.append(port_input)
    else:
        print("Must be unique and between 1024 and 64000")

#Output File
file_output = input("Enter Output file name: ")

class Packet:
    def __init__(self, magicno, typePack, seqno, dataLen, data):
        self.magicno = magicno # Should usually be 0x497E
        self.typePack = typePack #Only 2 types data, acknowledge
        self.seqno = seqno #Should be 0 or 1
        self.dataLen = dataLen #This determines, how long data is
        self.data = data # length determined by dataLen
    
#Sockets
r_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
r_in.bind(('127.0.0.1', port_list[0]))
r_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
r_out.bind(('127.0.0.1', port_list[1]))
r_out.connect(('127.0.0.1', port_list_channel[0]))

#initialising
file = open(file_output, 'a')
expected = 0
processing = True
while (processing):
    incoming_packet = r_in.recv(1024)
    incoming = pickle.loads(incoming_packet)
    if (incoming.magicno != 0x497E) or (incoming.typePack != "dataPacket"):
        break
    else:
        if incoming.seqno != expected:
            packet = Packet(0x497E, "acknowledgementPacket", incoming.seqno, 0, None)
            packet = pickle.dumps(packet)
            r_out.send(packet)
        else:
            packet = Packet(0x497E, "acknowledgementPacket", incoming.seqno, 0, None)
            packet = pickle.dumps(packet)
            r_out.send(packet)
            expected = 1 - expected
            if (incoming.dataLen > 0):
                file.write(incoming.data)
            else:
                file.close()
                r_in.close()
                r_out.close()
                processing = False
    incoming = None
    incoming_packet = None