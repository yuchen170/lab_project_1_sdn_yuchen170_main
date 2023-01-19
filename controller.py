
"""This is the Controller Starter Code for ECE50863 Lab Project 1
Author: Xin Du
Email: du201@purdue.edu
Last Modified Date: December 9th, 2021
"""

import sys
import socket
from datetime import date, datetime
from queue import PriorityQueue
import threading

# Please do not modify the name of the log file, otherwise you will lose points because the grader won't be able to find your log file
LOG_FILE = "Controller.log"

# Those are logging functions to help you follow the correct logging standard

# "Register Request" Format is below:
#
# Timestamp
# Register Request <Switch-ID>

def register_request_received(switch_id):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Register Request {switch_id}\n")
    write_to_log(log)

# "Register Responses" Format is below (for every switch):
#
# Timestamp
# Register Response <Switch-ID>

def register_response_sent(switch_id):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Register Response {switch_id}\n")
    write_to_log(log) 

# For the parameter "routing_table", it should be a list of lists in the form of [[...], [...], ...]. 
# Within each list in the outermost list, the first element is <Switch ID>. The second is <Dest ID>, and the third is <Next Hop>, and the fourth is <Shortest distance>
# "Routing Update" Format is below:
#
# Timestamp
# Routing Update 
# <Switch ID>,<Dest ID>:<Next Hop>,<Shortest distance>
# ...
# ...
# Routing Complete
#
# You should also include all of the Self routes in your routing_table argument -- e.g.,  Switch (ID = 4) should include the following entry: 		
# 4,4:4,0
# 0 indicates ‘zero‘ distance
#
# For switches that can’t be reached, the next hop and bandwidth should be ‘-1’ and ‘9999’ respectively. (9999 means infinite distance so that that switch can’t be reached)
#  E.g, If switch=4 cannot reach switch=5, the following should be printed
#  4,5:-1,9999
#
# For any switch that has been killed, do not include the routes that are going out from that switch. 
# One example can be found in the sample log in starter code. 
# After switch 1 is killed, the routing update from the controller does not have routes from switch 1 to other switches.

def routing_table_update(routing_table):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append("Routing Update\n")
    for row in routing_table:
        log.append(f"{row[0]},{row[1]}:{row[2]},{row[3]}\n")
    log.append("Routing Complete\n")
    write_to_log(log)

# "Topology Update: Link Dead" Format is below: (Note: We do not require you to print out Link Alive log in this project)
#
#  Timestamp
#  Link Dead <Switch ID 1>,<Switch ID 2>

def topology_update_link_dead(switch_id_1, switch_id_2):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Link Dead {switch_id_1},{switch_id_2}\n")
    write_to_log(log) 

# "Topology Update: Switch Dead" Format is below:
#
#  Timestamp
#  Switch Dead <Switch ID>

def topology_update_switch_dead(switch_id):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Switch Dead {switch_id}\n")
    write_to_log(log) 

# "Topology Update: Switch Alive" Format is below:
#
#  Timestamp
#  Switch Alive <Switch ID>

def topology_update_switch_alive(switch_id):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Switch Alive {switch_id}\n")
    write_to_log(log) 

def write_to_log(log):
    with open(LOG_FILE, 'a+') as log_file:
        log_file.write("\n\n")
        # Write to log
        log_file.writelines(log)

def main():
    #Check for number of arguments and exit if host/port not provided
    num_args = len(sys.argv)
    if num_args < 3:
        print ("Usage: python controller.py <port> <config file>\n")
        sys.exit(1)
    
    # Write your code below or elsewhere in this file
    controller = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    controller.bind(('127.0.0.1',9999))
    
    #read config file
    file = str(sys.argv[2])
    
    config_array = []

    with open(file) as f:
        config_array = f.readlines()
    num_switch = int(config_array[0])
    #print(num_switch)
    Matrix = [[-2 for x in range(3)] for y in range(len(config_array)-1)]

    for n in range(len(config_array)-1):
        Matrix[n] = config_array[n+1].split( )
        for m in range(3):
            Matrix[n][m] = int(Matrix[n][m])
    print(Matrix)
    
###Dijkstra
    class Graph:
        def __init__(self, num_of_vertices):
            self.v = num_of_vertices
            self.edges = [[-1 for i in range(num_of_vertices)] for j in range(num_of_vertices)]
            self.visited = []
        def add_edge(self, u, v, weight):
            self.edges[u][v] = weight
            self.edges[v][u] = weight
    
    
    def dijkstra(graph, start_vertex):
        D = {v:int('9999') for v in range(graph.v)}###
        D[start_vertex] = 0
        #P = {node: -1 for node in range(graph.v)}
        P = {start_vertex: None}
        #last_point = start_vertex
        #print(graph.v)
        #V = [0]*graph.v###
        #print(V)

        pq = PriorityQueue()
        pq.put((0, start_vertex))

        while not pq.empty():
            (dist, current_vertex) = pq.get()
            graph.visited.append(current_vertex)
            #print(graph.visited)

            for neighbor in range(graph.v):
                if graph.edges[current_vertex][neighbor] != -1:
                    distance = graph.edges[current_vertex][neighbor]
                    if neighbor not in graph.visited:
                        old_cost = D[neighbor]
                        new_cost = D[current_vertex] + distance
                        if new_cost < old_cost:
                            pq.put((new_cost, neighbor))
                            D[neighbor] = new_cost
                            P[neighbor] = current_vertex
                            
                
            #print(pq.queue)    
        return P,D
   
    def make_path(parent, goal):
        if goal not in parent:
            return None
        v = goal
        path = []
        while v is not None: # root has null parent
            path.append(v)
            v = parent[v]
        #print(path)
        return path[::-1]

### 
    num_request=0
    neighbor = [[-1 for x in range(num_switch-1)] for y in range(num_switch)]
    switch_host=[0]*num_switch
    #print(switch_host)
    switch_port=[0]*num_switch
    while(1):
        msg, addr = controller.recvfrom(1024)
        #print(addr)
        #print(addr[0])
        #print(addr[1])
        
        #print(msg.decode('utf8'))
        parse = msg.split( )
        switch_id = int(parse[0])
        switch_host[switch_id] = addr[0]
        switch_port[switch_id] = addr[1]
        print(switch_host)
        print(switch_port)
        
        if 'Register_Request' in str(parse[1]):
            #print('receive request')
            num_request=num_request+1
            register_request_received(switch_id)
            if num_request==num_switch: #send register response
                print(Matrix)
                
                for n in range(num_switch):
                    count_nieghbor = []
                    for m in range(len(config_array)-1):
                        print(n,m)
                        if Matrix[m][0]==n:
                            count_nieghbor.append(Matrix[m][1])
                        if Matrix[m][1]==n:
                            count_nieghbor.append(Matrix[m][0])
                    neighbor[n]=count_nieghbor
                    controller.sendto((str(len(neighbor[n]))+' '+'Register_Response').encode('utf-8'),(switch_host[n],switch_port[n]))
                    register_response_sent(n)
                    for i in range(len(neighbor[n])):
                        #print(str(count_nieghbor[i]))
                        #print(str(switch_host[int(count_nieghbor[i])]))
                        controller.sendto((str(count_nieghbor[i])+' '+str(switch_host[int(count_nieghbor[i])])+' '+str(switch_port[int(count_nieghbor[i])])).encode('utf-8'),(switch_host[n],switch_port[n]))
                
                print(neighbor)
                num_switch_dead = 0
                dead_switch = []
                num_switch_alive = num_switch-num_switch_dead
                #route table
                route_table = []
                for n in range(num_switch):
                    g = Graph(num_switch)
                    for m in range(len(config_array)-1):
                        #print(m,'num of add')
                        #print(Matrix[n])
                        g.add_edge(Matrix[m][0], Matrix[m][1], Matrix[m][2])
                    #D = dijkstra(g, n)
                    parent, Distance = dijkstra(g, n)
                    arr = [[-1 for x in range(num_switch)] for y in range(num_switch)]
                    for i in range(num_switch):
                        arr[i] = make_path(parent, i)
                        if len(arr[i])<2:
                            arr[i].append(i)
                    print(arr)
                    print(Distance)
                    controller.sendto((str(n)+' '+'Route_Table'+' '+str(num_switch)).encode('utf-8'),(switch_host[n],switch_port[n]))
                    for j in range(num_switch):
                        controller.sendto((str(j)+' '+str(arr[j][1])).encode('utf-8'),(switch_host[n],switch_port[n]))
                        route_table.append([n,j,arr[j][1],Distance[j]])
                        #route_table[n][0] = n
                        #route_table[n][1] = j
                        #route_table[n][2] = arr[j][1]
                        #route_table[n][3] = Distance[j]
                print(route_table)
                routing_table_update(route_table)
                        
                    
    

if __name__ == "__main__":
    main()
    
