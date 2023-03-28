import sys
import time

#shared buffer for all nodes to be able to access each other's dv info
#when nodes get an update to their dv, they will update the buffer and notify the other nodes to check if they need to update
#initialized to 16 (infinity) except the node's relation to itself, will be set to lower numbers when connections are set
sharedBuffer = [[0,16,16,16,16,16],
                [16,0,16,16,16,16],
                [16,16,0,16,16,16],
                [16,16,16,0,16,16],
                [16,16,16,16,0,16],
                [16,16,16,16,16,0]]

#define class node to keep track of node info, maximum 6
class node:
    #reinitialize num to node number
    num = -1
    dv = []
    #keep track of who to send dv to, maximum 4 neighbors
    neighbors = []
    #subset of neighbors, consists of neighbors who updated in the previous iteration
    updatedNeighbors = []
    #flag for if dv has been updated this iteration, may not need to be in class
    updated = True

    def __init__(self, num, dv):
        self.num = num
        self.dv = dv
        self.neighbors = []
        self.updatedNeighbors = []
        self.updated = True
        for i in range(len(dv)):
            if dv[i] != 16 and i != self.num:
                self.neighbors.append(i)
                #print('node',num,'assigned neighbor',i)

    #ran in step of computing new dvs
    def updateLinks(self):
        if len(self.updatedNeighbors) == 0:
            #no neighboring links need to be updated
            #updated should already be false when this is the case, this is mostly a safeguard
            self.updated = False
            #print('node',self.num,'was sent no dvs')
            return

        #applies b-f equation for each node
        #print('node',self.num)
        for i in range(len(self.dv)):
            links = [self.dv[i]]
            for n in self.updatedNeighbors:
                #dist from curnode to n + dist from n to current index of dv
                links.append(sharedBuffer[self.num][n] + sharedBuffer[n][i])
            #print(self.dv[i], links)
            if self.dv[i] != min(links):
                print('updated node',self.num,'cost to node',i,'from',self.dv[i],'to',min(links))
                self.dv[i] = min(links)
                self.updated = True

if __name__ == "__main__":
    #determine whether to allow user to iterate through each step of algorithm
    stopping = input('would you like to run the program without stopping? y or n: ') == 'n'
    startTime = time.time()
    #disgusting line to convert file into int list
    links = list(map(int, open(sys.argv[1]).read().replace('\n', ' ').split(' ')))

    #apply lines in links to sharedBuffer
    while len(links) > 0:
        n1 = links.pop(0) - 1
        n2 = links.pop(0) - 1
        c = links.pop(0)
        sharedBuffer[n1][n2] = c
        sharedBuffer[n2][n1] = c

    #initialize the maximum six nodes with their part of initial sharedBuffer
    nodes = [node(0, sharedBuffer[0]),
             node(1, sharedBuffer[1]),
             node(2, sharedBuffer[2]),
             node(3, sharedBuffer[3]),
             node(4, sharedBuffer[4]),
             node(5, sharedBuffer[5])]

    #keep track of iterations
    itNum = 0
    #flag to check for stable
    updated = True

    while True:
        #print current node status
        itNum += 1
        print('\niteration ', itNum)
        print('\n|node| c0 | c1 | c2 | c3 | c4 | c5 |')
        print('------------------------------------')
        for i in range(len(nodes)):
            print('| {}  | {:<2} | {:<2} | {:<2} | {:<2} | {:<2} | {:<2} |'.format(i,*sharedBuffer[i]))
        
        #allow user to update links in system if desired
        if stopping:
            updatedLinks = False
            while input('enter c to change a link, or press enter to proceed: ') == 'c':
                updatedLinks = True
                updated = True
                n1 = int(input('enter number of first node: '))
                n2 = int(input('enter number of second node: '))
                c = int(input('enter cost, 0-16: '))

                #since link is directly created between n1 and n2, they are now neighbors
                if n1 not in nodes[n2].neighbors:
                    nodes[n1].neighbors.append(n2)
                    nodes[n2].neighbors.append(n1)
                
                #if c is 16, a direct link would be severed if it existed
                if c == 16 and n1 in nodes[n2].neighbors:
                    nodes[n1].neighbors.remove(n2)
                    nodes[n2].neighbors.remove(n1)

                #only makes updates if value isn't the same already
                if nodes[n1].dv[n2] != c:
                    nodes[n1].dv[n2] = c
                    sharedBuffer[n1][n2] = c
                    nodes[n1].updated = True
                
                #vice versa for the connection in the opposite direction
                if nodes[n2].dv[n1] != c:
                    nodes[n2].dv[n1] = c
                    sharedBuffer[n1][n2] = c
                    nodes[n2].updated = True
                print('link updated')
            
            if updatedLinks:
                print('updated node info:')
                print('\n|node| c0 | c1 | c2 | c3 | c4 | c5 |')
                print('------------------------------------')
                for i in range(len(nodes)):
                    print('| {}  | {:<2} | {:<2} | {:<2} | {:<2} | {:<2} | {:<2} |'.format(i,*sharedBuffer[i]))

        #set flag to false since no updates observed yet
        updated = False
        
        #equivalent to step of each node receiving dvs from neighbors
        #any node whose neighbor updated last iteration will receive their dv
        #or technically will receive their index in the updatedNeighbors list
        print('\nstep 1')
        for n in nodes:
            if n.updated:
                #if at least one update, set updated flag to true
                updated = True
                #adds current node to all of its neighbors lists of updated dvs
                for nb in n.neighbors:
                    print('node',nb,'receives dv from node',n.num)
                    nodes[nb].updatedNeighbors.append(n.num)
                #set node's updated flag to false, since it hasn't updated this iteration
                n.updated = False
        if not updated:
            print('no dvs were received')

        #equivalent to step of computing new dvs
        print('\nstep 2')
        for n in nodes:
            if len(n.neighbors) != 0:
                n.updateLinks()
                continue

            #if we're here, n has no neighbors
            #this line checks if any other nodes have a connection to n
            if all((sharedBuffer[i][n.num] == 16 and nodes[i].dv[n.num] == 16) or i == n.num for i in range(len(sharedBuffer))):
                continue

            #now we can update the connections to n to sever them
            for i in range(len(sharedBuffer)):
                if i == n.num:
                    continue
                sharedBuffer[i][n.num] = 16
                nodes[i].dv[n.num] = 16
                n.dv[i] = 16
            print('updated values for severed connection to node',n.num)


        if all(n.updated == False for n in nodes):
            print('no new values were computed')
        
        #equivalent to step of sending new dvs by updating sharedBuffer with each node's dvs
        print('\nstep 3')
        for n in nodes:
            if nodes[n.num].updated:
                print('node',n.num,'sends out updated dv to neighbors')
                sharedBuffer[n.num] = n.dv
        if all(n.updated == False for n in nodes):
            print('no dvs were sent\nstable state reached after',itNum,'iterations')
            if stopping and input('enter c to continue, or press enter to close: ') == 'c':
                continue
            if not stopping:
                print('acheived in',round(time.time()-startTime, 5) * 1000,'milliseconds')
            break