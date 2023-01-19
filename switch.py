
"""This is the Switch Starter Code for ECE50863 Lab Project 1
Author: Xin Du
Email: du201@purdue.edu
Last Modified Date: December 9th, 2021
"""

import sys
import socket
from datetime import date, datetime
import threading

# Please do not modify the name of the log file, otherwise you will lose points because the grader won't be able to find your log file
LOG_FILE = "switch#.log" # The log file for switches are switch#.log, where # is the id of that switch (i.e. switch0.log, switch1.log). The code for replacing # with a real number has been given to you in the main function.

# Those are logging functions to help you follow the correct logging standard

# "Register Request" Format is below:
#
# Timestamp
# Register Request Sent

def register_request_sent():
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Register Request Sent\n")
    write_to_log(log)

# "Register Response" Format is below:
#
# Timestamp
# Register Response Received

def register_response_received():
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Register Response received\n")
    write_to_log(log) 

# For the parameter "routing_table", it should be a list of lists in the form of [[...], [...], ...]. 
# Within each list in the outermost list, the first element is <Switch ID>. The second is <Dest ID>, and the third is <Next Hop>.
# "Routing Update" Format is below:
#
# Timestamp
# Routing Update 
# <Switch ID>,<Dest ID>:<Next Hop>
# ...
# ...
# Routing Complete
# 
# You should also include all of the Self routes in your routing_table argument -- e.g.,  Switch (ID = 4) should include the following entry: 		
# 4,4:4

def routing_table_update(routing_table):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append("Routing Update\n")
    for row in routing_table:
        log.append(f"{row[0]},{row[1]}:{row[2]}\n")
    log.append("Routing Complete\n")
    write_to_log(log)

# "Unresponsive/Dead Neighbor Detected" Format is below:
#
# Timestamp
# Neighbor Dead <Neighbor ID>

def neighbor_dead(switch_id):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Neighbor Dead {switch_id}\n")
    write_to_log(log) 

# "Unresponsive/Dead Neighbor comes back online" Format is below:
#
# Timestamp
# Neighbor Alive <Neighbor ID>

def neighbor_alive(switch_id):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Neighbor Alive {switch_id}\n")
    write_to_log(log) 

def write_to_log(log):
    with open(LOG_FILE, 'a+') as log_file:
        log_file.write("\n\n")
        # Write to log
        log_file.writelines(log)

def main():

    global LOG_FILE

    #Check for number of arguments and exit if host/port not provided
    num_args = len(sys.argv)
    if num_args < 4:
        print ("switch.py <Id_self> <Controller hostname> <Controller Port>\n")
        sys.exit(1)

    my_id = int(sys.argv[1])
    LOG_FILE = 'switch' + str(my_id) + ".log" 
    # Write your code below or elsewhere in this file
    my_hostname = str(sys.argv[2])
    my_port = int(sys.argv[3])
    # register request
    register_request_sent()
    switch = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #print(socket)
    switch.bind((my_hostname,my_port))
    #msg = str()
    switch.sendto((str(my_id)+' Register_Request ').encode('utf-8'),('127.0.0.1',9999))
    #print(switch.recvfrom.decoede('utf-8'))
    '''
    def Timer():
        threading.Timer(5.0, Timer).start()
        for n in num_switch:
            switch.sendto(('Keep_Alive').encode('utf-8'),(switch_host[n],switch_port[n]))
        Timer()
    '''
    route_received=[]
    RT_switchID = []
    RT_DestID = []
    RT_NextHop=[]

    while(1):
        msg, addr = switch.recvfrom(1024)
        print(msg.decode('utf8'))
        
        parse = msg.split( )
        #print(parse[1])
        type=str(parse[1])
        if 'Register_Response' in type:
            register_response_received()
        if 'Route_Table' in type:
            num_rule = int(parse[2])
            for n in range(num_rule):
                msg, addr = switch.recvfrom(1024)
                route_received.append(msg)
            print(route_received)
            print('received')
            route_table = [[-1 for x in range(3)] for y in range(num_rule)]
            for n in range(num_rule):
                x = route_received[n].split( )
                dest = int(x[0])
                next = int(x[1])
                route_table[n][0] = my_id
                route_table[n][1] = dest
                route_table[n][2] = next
            print(route_table)
            routing_table_update(route_table)
            
                
                
                
            
            
            

if __name__ == "__main__":
    main()
    