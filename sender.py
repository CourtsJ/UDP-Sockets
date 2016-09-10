#UDP Sender
import socket
import select
import pickle
import os.path

port_list = []
port_names = ["s_out","s_in"]
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
    port_input = int(input("Enter cs_in Port Number: "))
    if ((port_input > 1024 and port_input < 64000) and (port_input not in port_list)):
        port_list_channel.append(port_input)
    else:
        print("Must be unique and between 1024 and 64000")
        
#Sockets
s_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_out.bind(('127.0.0.1', port_list[0]))
s_out.connect(('127.0.0.1', port_list_channel[0]))
s_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_in.bind(('127.0.0.1', port_list[1]))

class Packet:
    def __init__(self, magicno, typePack, seqno, dataLen, data):
        self.magicno = magicno # Should usually be 0x497E
        self.typePack = typePack #Only 2 types data, acknowledge
        self.seqno = seqno #Should be 0 or 1
        self.dataLen = dataLen #This determines, how long data is
        self.data = data # length determined by dataLen
        
#Initialsing 
successful = False
while (successful == False):
    try:
        file_input = input("Enter Input file name: ")
        if (os.path.isfile(file_input)):
            successful = True
        else:
            successful = False
    except:
        successful = False
        continue
next_packet = 0
exitFlag = False
buffer = 512
packetBuffer = []
i = 0
counter = 0
continue_loop = False

#Sending Packets
if successful:
    f = open(file_input)
    while (exitFlag is False):
        data_local = f.read(buffer)
        if len(data_local) == 0:
            packet = Packet(0x497E, "dataPacket", next_packet, 0, None)
            exitFlag = True
        else:
            packet = Packet(0x497E, "dataPacket", next_packet, len(data_local),data_local)
        encoded_packet= pickle.dumps(packet)
        packetBuffer.append(encoded_packet)
        received_good = False
        while (received_good is False):
            s_out.send(packetBuffer[i])
            print(packetBuffer[i])
            if (exitFlag == False):
                counter += 1
            s_in.settimeout(1.0)
            try:
                incoming = s_in.recv(1024)
                continue_loop = True
            except socket.timeout:
                continue_loop = False
                continue
            if (continue_loop is True):
                incoming = pickle.loads(incoming)
                if incoming == None:
                    break
                else:
                    if (incoming.magicno != 0x497E) or (incoming.typePack !="acknowledgementPacket") or (incoming.dataLen != 0):
                        break
                    elif incoming.seqno != next_packet:
                        break
                    else:
                        next_packet = 1 - next_packet
                        received_good = True
                        i += 1
                    if exitFlag is True:
                        f.close()
#Closing 
s_in.close()
s_out.close()
print("Number of packets send: ", counter)