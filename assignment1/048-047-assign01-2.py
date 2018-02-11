"""
usage: 048-047-assign01-2.py [-h] [-v] [-n NPROCESS] [-o ORDER]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose mode
  -n NPROCESS, --nprocess NPROCESS
                        Number of processes n where n>=2
"""
from multiprocessing import Process, Pipe, Array
import random
import time
import sys
import argparse

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

class Variable(object):
    """
    Class for maintaining copy of data
    """

    def __init__(self, var, marked=False):

        self.var = var
        self.marked = marked

class ProcessNode(Process):
    """
    Process Nodes
    """

    def __init__(self, lconn=None, rconn=None, shared_array=None, order='asc', data=None):
        """
        Initializes the process object with data and connections
        to left and right processes
        """

        Process.__init__(self)

        if not data:
            self.data = int(random.uniform(-100.0,500.0))
        else:
            self.data = data
        self.lconn = lconn
        self.rconn = rconn
        self.vid = -1

        self.vl = None
        self.vr = None
        self.order = order

        self.area = 0

        if shared_array:
            self.shared_array = shared_array

    def recieve(self, sender_node):
        """
        Recieve packet
        """

        if sender_node == "left":
            msg = self.lconn.recv()

            if msg.type == PACKET_TYPE["CMP_REQUEST"]:
                if msg.data.var > self.vl.var:
                    if msg.data.marked:
                        self.area = self.area - 1
                    if self.vl.marked:
                        self.area = self.area + 1
                    self.vl.var = msg.data.var
                    self.vl.marked = msg.data.marked

            else:
                if self.rconn != None:
                    self.vid = msg.data + 1
                    self.rconn.send(Packet(self.vid, "PR_CNT_MSG"))
                else:
                    self.vid = msg.data + 1
                    self.n_processes = self.vid
                    self.lconn.send(Packet(self.n_processes, "PR_CNT_MSG"))

        elif sender_node == "right":
            msg = self.rconn.recv()

            if msg.type == PACKET_TYPE["CMP_REQUEST"]:
                if self.vr.var > msg.data.var:
                    self.vr.var = msg.data.var
                    self.vr.marked = msg.data.marked
            else:
                self.n_processes = msg.data
                if self.lconn != None:
                    self.lconn.send(msg)

    def send(self, reciever_node):
        """
        Send packet
        """

        if reciever_node == "right":
            if self.rconn != None:
                self.rconn.send(Packet(self.vr, "CMP_REQUEST"))
        else:
            if self.lconn != None:
                self.lconn.send(Packet(self.vl, "CMP_REQUEST"))

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

    def swap_vlvr(self):
        if self.lconn == None or self.rconn == None:
            return
        else:
            temp_var = self.vl.var
            temp_marked = self.vl.marked
            self.vl.var = self.vr.var
            self.vl.marked = self.vr.marked
            self.vr.var = temp_var
            self.vr_marked = temp_marked

    def run(self):

        # Count number of processes and relative position of each process
        # in line network
        self.count_processes()

        # print("process id {}, process data {}".format(self.vid, self.data))

        # Update process state in shared array
        if hasattr(self, 'shared_array'):
            self.shared_array[0*self.n_processes*4 + 4*(self.vid-1) + 0] = self.data

        # Round-0
        if self.lconn == None:
            self.vl = Variable(self.data)
            self.vr = Variable(self.data, marked=True)
            self.area = self.area - 1
        elif self.rconn == None:
            self.vl = Variable(self.data, marked=True)
            self.vr = Variable(self.data)
        else:
            self.vl = Variable(self.data)
            self.vr = Variable(self.data)
        self.send("left")
        self.send("right")

        # Update process state in shared array
        if hasattr(self, 'shared_array'):
            self.shared_array[1*self.n_processes*4 + 4*(self.vid-1) + 0] = self.data
            self.shared_array[1*self.n_processes*4 + 4*(self.vid-1) + 1] = self.vl.var
            self.shared_array[1*self.n_processes*4 + 4*(self.vid-1) + 2] = self.vr.var
            self.shared_array[1*self.n_processes*4 + 4*(self.vid-1) + 3] = self.area

        # For Round > 1
        for i in range(1, self.n_processes):
            if self.lconn != None:
                self.recieve("left")
            if self.rconn != None:
                self.recieve("right")
            if self.vl.var > self.vr.var:
                self.swap_vlvr()
            if i < (self.n_processes-1) :
                self.send("left")
                self.send("right")
            else:
                if self.area == -1:
                    self.data = self.vr.var
                if (self.area == 0) or (self.area == 1):
                    self.data = self.vl.var

            # Update process state in shared array
            if hasattr(self, 'shared_array'):
                if i == (self.n_processes-1):
                    self.shared_array[(i+1)*self.n_processes*4 + 4*(self.vid-1) + 0] = self.data
                self.shared_array[(i+1)*self.n_processes*4 + 4*(self.vid-1) + 1] = self.vl.var
                self.shared_array[(i+1)*self.n_processes*4 + 4*(self.vid-1) + 2] = self.vr.var
                self.shared_array[(i+1)*self.n_processes*4 + 4*(self.vid-1) + 3] = self.area

        # print("Sorted process id {}, process data {}".format(self.vid, self.data))

def main(verbose=False, n_processes=None, given_array=None, order='asc'):
    """
    Simulation of the distributed sorting proposed by Sasaski.
    Each Process node has it's own resource. Each of the non-terminal
    node is connected to two adjacent processes with a synchronized duplex Pipe
    connection.
    """

    num_process = 0
    process_list = []

    if not given_array:

        num_process = int(random.uniform(2.0, 20.0))
        if n_processes:
            num_process = n_processes

        connection_list = [Pipe() for i in range(num_process-1)]

        shared_array = None
        if verbose:
            shared_array = Array('i', (num_process+1)*num_process*4)

        process_list = [ProcessNode(
            None,
            connection_list[0][0],
            shared_array=shared_array,
            order=order)]
        for i in range(num_process-2):
            p = ProcessNode(
                connection_list[i][1],
                connection_list[i+1][0],
                shared_array=shared_array,
                order=order)
            process_list.append(p)
        process_list.append(
            ProcessNode(
            connection_list[num_process-2][1],
            shared_array=shared_array,
            order=order))

    else:

        num_process = len(given_array)

        connection_list = [Pipe() for i in range(num_process-1)]

        shared_array = None
        if verbose:
            shared_array = Array('i', (num_process+1)*num_process)

        process_list = [ProcessNode(
            None,
            connection_list[0][0],
            shared_array=shared_array,
            data=given_array[0],
            order=order)]

        for i in range(num_process-2):
            p = ProcessNode(
                connection_list[i][1],
                connection_list[i+1][0],
                shared_array=shared_array,
                data=given_array[i],
                order=order)
            process_list.append(p)

        process_list.append(
            ProcessNode(
            connection_list[num_process-2][1],
            shared_array=shared_array,
            data=given_array[-1],
            order=order))

    # Start time
    start = time.clock()

    for p in process_list:
        p.start()

    for p in process_list:
        p.join()

    # Elapsed time
    time_elapsed = time.clock() - start

    if verbose:
        print("number of process {}".format(num_process))

        print_factor = 1
        if num_process <= 10 and num_process>=5:
            print_factor = 2
        else:
            print_factor = 5

        for i in range(0, num_process+1):
            if i==0:
                print("Initial : ", end=" ")
                for j in range(0, num_process):
                    print("P{}(D({}))".format(
                        j+1, shared_array[i*num_process*4+j*4+0]), end=" ")
                print("\n")

            elif (i==(num_process)) or (i%print_factor==0):

                print("Round {} : ".format(i-1))

                if i==num_process:
                    print("Data   :", end=" ")
                    for j in range(0, num_process):
                        print("P{}(D({})) ".format(
                            j+1,shared_array[i*num_process*4+j*4+0]), end=" ")
                        if j==(num_process-1):
                            print('')

                print("vl, vr  :", end=" ")
                for j in range(0, num_process):
                    print("P{}({}|{})".format(
                        j+1,
                        shared_array[i*num_process*4+j*4+1],
                        shared_array[i*num_process*4+j*4+2]), end=" ")
                    if j==(num_process-1):
                        print('')

                print("Area   :", end=" ")
                for j in range(0, num_process):
                    print("P{}(A({})) ".format(
                        j+1,shared_array[i*num_process*4+j*4+3]), end=" ")
                    if j==(num_process-1):
                        print('')
                print("\n")

    return time_elapsed

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Verbose mode", action="store_true")
    parser.add_argument("-n", "--nprocess", help="Number of processes n where n>=2", action="store", type=int)
    parser.add_argument("-o", "--order", help="0 for ascending order, 1 for descending order. Without any argument ascending order is used", action="store", type=int)
    args = parser.parse_args()

    order = 'asc'
    if args.order:
        if args.order == 1:
            order = 'dsc'

    if args.nprocess:
        if args.nprocess >= 2:
            main(verbose=args.verbose, n_processes = args.nprocess, order=order)
        else:
            print("Invalid n")
    else:
        main(verbose=args.verbose, order=order)
