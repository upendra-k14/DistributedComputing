from multiprocessing import Process, Pipe
import random

"""
Three message types are defined:

1. CMP_REQUEST >> Swap request from P_(i) to P_(i+1)

2. RESPONSE >> Response message containing minimum of data at P_(i) and P_(i+1)
               for corresponding swap request

3. PR_CNT_MSG >> Flag for marking the message for purpose of finding number of
               processes in line network
"""

PACKET_TYPE = {
    "CMP_REQUEST" : 0,
    "RESPONSE" : 1,
    "PR_CNT_MSG" : 2
}

class Packet(object):
    """
    Class for encapsulating the message and it's properties
    """

    def __init__(self, data, ptype):

        self.data = data
        self.type = PACKET_TYPE[ptype]

class ProcessNode(Process):
    """
    Process Nodes
    """

    def __init__(self, lconn=None, rconn=None):
        """
        Initializes the process object with data and connections
        to left and right processes
        """

        Process.__init__(self)
        self.data = int(random.uniform(-100.0,500.0))
        self.lconn = lconn
        self.rconn = rconn
        self.vid = -1

    def recieve(self, sender_node):
        """
        Recieve packet
        """

        if sender_node == "left":
            msg = self.lconn.recv()

            if msg.type == PACKET_TYPE["CMP_REQUEST"]:
                self.lconn.send(Packet(min(self.data, msg.data), "RESPONSE"))
                if msg.data > self.data:
                    self.data = msg.data

            elif msg.type == PACKET_TYPE["PR_CNT_MSG"]:
                if self.rconn != None:
                    self.vid = msg.data + 1
                    self.rconn.send(Packet(self.vid, "PR_CNT_MSG"))
                else:
                    self.vid = msg.data + 1
                    self.n_processes = self.vid
                    self.lconn.send(Packet(self.n_processes, "PR_CNT_MSG"))

            elif msg.type == PACKET_TYPE["RESPONSE"]:
                self.data = msg.data

        elif sender_node == "right":
            msg = self.rconn.recv()

            if msg.type == PACKET_TYPE["RESPONSE"]:
                self.data = msg.data

            elif msg.type == PACKET_TYPE["PR_CNT_MSG"]:
                self.n_processes = msg.data
                if self.lconn != None:
                    self.lconn.send(msg)

            elif msg.type == PACKET_TYPE["CMP_REQUEST"]:
                self.rconn.send(Packet(max(self.data, msg.data), "RESPONSE"))
                if msg.data < self.data:
                    self.data = msg.data

    def send(self, reciever_node):
        """
        Send packet
        """

        if reciever_node == "right":
            if self.rconn != None:
                self.rconn.send(Packet(self.data, "CMP_REQUEST"))
                self.recieve("right")

        else:
            if self.lconn != None:
                self.lconn.send(Packet(self.data, "CMP_REQUEST"))
                self.recieve("left")

    def count_processes(self):
        """
        Initiate count processes subroutine
        If process id and number of processes are not determined yet,
        then subroutine will be called.
        """

        if self.lconn == None:
            self.vid = 1
            self.rconn.send(Packet(self.vid, "PR_CNT_MSG"))
            self.recieve("right")

        else:
            self.recieve("left")
            if self.rconn != None:
                self.recieve("right")

    def run(self):

        # Count number of processes and relative position of each process
        # in line network
        self.count_processes()

        print("process id {}, process data {}".format(self.vid, self.data))

        for i in range(1, self.n_processes-1):
            # Check if process should generate compare request message
            # in i_th round
            if ((self.vid - i)%2) == 0:
                    self.send("left")
                    self.send("right")
            else:
                if self.lconn != None:
                    self.recieve("left")
                if self.rconn != None:
                    self.recieve("right")

        print("Sorted process id {}, process data {}".format(self.vid, self.data))

def main():
    """
    Create environment for simulating the distributed n-2 rounds alternative OET
    sorting. Each Process node has it's own resource. Each of the non-terminal
    node is connected to two adjacent processes with a synchronized duplex Pipe
    connection.
    """

    num_process = int(random.uniform(2.0, 20.0))
    connection_list = [Pipe() for i in range(num_process-1)]

    process_list = [ProcessNode(None, connection_list[0][0])]
    for i in range(num_process-2):
        p = ProcessNode(connection_list[i][1], connection_list[i+1][0])
        process_list.append(p)
    process_list.append(ProcessNode(connection_list[num_process-2][1]))

    for p in process_list:
        p.start()

    for p in process_list:
        p.join()

if __name__ == "__main__":
    main()
