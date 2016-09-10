#UDP Channel
import socket
import select
import random
import pickle

#Port input
port_list = []
port_names = ["cs_in","cs_out","cr_in","cr_out","s_in","r_in"]
i = 0
while len(port_list) < 6:
    port_input = int(input("Enter Port Number for {}: ".format(port_names[i])))
    if ((port_input > 1024 and port_input < 64000) and (port_input not in port_list)):
        port_list.append(port_input)
        i += 1
    else:
        print("Must be unique and between 1024 and 64000")
packet_loss = 1
while (packet_loss < 0) or (packet_loss >= 1):
    packet_loss = float(input("Enter Packet Loss Rate: "))
    
#Sockets
cs_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cs_in.bind(('127.0.0.1', port_list[0]))
cs_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cs_out.bind(('127.0.0.1', port_list[1]))
cs_out.connect(('127.0.0.1', port_list[4]))
cr_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cr_out.bind(('127.0.0.1', port_list[3]))
cr_out.connect(('127.0.0.1', port_list[5]))
cr_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cr_in.bind(('127.0.0.1', port_list[2]))

#Packet magicno function
def magicnoCompare(magicno):
    if magicno != 0x497E:
        return False
    else:
        return True
    
class Packet:
    
    def __init__(self, magicno, typePack, seqno, dataLen, data):
        self.magicno = magicno # Should usually be 0x497E
        self.typePack = typePack #Only 2 types data, acknowledge
        self.seqno = seqno #Should be 0 or 1
        self.dataLen = dataLen #This determines, how long data is
        self.data = data # length determined by dataLen
#Waiting for input
while(1):
    data_sockets = select.select([cr_in, cs_in], [], [])

    receiver_packet = False
    sender_packet = False
    for sock in data_sockets[0]:
        if sock == cs_in:
            incoming_sender = cs_in.recv(1024)
            incoming_sender = pickle.loads(incoming_sender)
            isAPacketReceiver = False
            isAPacketSender = False
            sender_packet = True
        elif sock == cr_in:
            incoming_receiver = cr_in.recv(1024)
            incoming_receiver = pickle.loads(incoming_receiver)
            isAPacketReceiver = False
            isAPacketSender = False
            receiver_packet = True
            
    if receiver_packet is True:
        isAPacketReceiver = True
        
    if sender_packet is True:
        isAPacketSender = True
        
    isAcceptedReceiver = False
    isAcceptedSender = False
    
    if receiver_packet is True:
        isThatMagicnoR = magicnoCompare(incoming_receiver.magicno)
        isAcceptedReceiver = True
        
    if sender_packet is True:
        isThatMagicnoS = magicnoCompare(incoming_sender.magicno)
        isAcceptedSender = True
            
    if (isAcceptedSender is True) and (isThatMagicnoS is True):
        if random.random() > packet_loss:
            cr_out.send(pickle.dumps(incoming_sender))
    if (isAcceptedReceiver is True) and (isThatMagicnoR is True):
        if random.random() > packet_loss:
            cs_out.send(pickle.dumps(incoming_receiver))
