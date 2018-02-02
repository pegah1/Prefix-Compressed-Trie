import math
import string
from collections import OrderedDict
from operator import itemgetter
bitmap1 = {"*":0, "0*":1, "1*":2, "00*":3, "01*":4, "10*":5, "11*":6, "000*":7, "001*":8, "010*":9, "011*":10, "100*":11,
         "101*":12, "110*":13, "111*":14}
bitmap2 = {"*":0, "0*":1, "1*":2, "00*":3, "01*":4, "10*":5, "11*":6}

class PCTrieNode:
    def __init__(self):
        self.node = []
        self.real = 0

class Node:
    def __init__(self):
        self.Prefix = ""
        self.Left = None
        self.Right = None
        self.NextHop = ""
        self.depth = 1
        self.real = 1           #if node has a prefix -> real is 1 ... else -> real is 0

class Trie:
    def __init__(self):
        self.Root = Node()
        self.depth = 1
        self.hash = {}          #collection of first of each subtrie
        self.stride = 4
        self.compSize = 2
        self.SubTrie = {}           #collection of constituents of each full binary subtrie
        self.PCTrie_BitMap = {}     #collection of constituents of each full PCTrie_subtrie

    #add the prefix to binary tree and divide the tree with the stride to some subtrie and save the root of each subtrie
    def add(self, route, nexthop):
        ro = self.Root
        self.hash[0] = [ro]
        for i in range(len(route)):
            if route[i] == "*":
                ro.Prefix = route
                ro.NextHop = nexthop
                ro.real = 1
                if self.depth < ro.depth: self.depth = ro.depth
            else:
                if route[i] == "1":
                    if ro.Right == None:
                        ro.Right = Node()
                        ro.Right.depth = ro.depth + 1
                        ro.Right.NextHop = ro.NextHop
                        ro.Right.Prefix = ro.Prefix[0:len(ro.Prefix)-1] + "1*"
                        ro.Right.real = 0
                        if (((ro.Right.depth - 1) % self.stride) == 0):     #insert node to hash dict
                            k = (ro.Right.depth - 1) / self.stride
                            if k in self.hash.keys():
                                self.hash[k].append(ro.Right)
                            else:
                                self.hash[k] = [ro.Right]
                    ro = ro.Right
                if route[i] == "0":
                    if ro.Left == None:
                        ro.Left = Node()
                        ro.Left.depth = ro.depth + 1
                        ro.Left.NextHop = ro.NextHop
                        ro.Left.Prefix = ro.Prefix[0:len(ro.Prefix)-1] + "0*"
                        ro.Left.real = 0
                        if (((ro.Left.depth - 1) % self.stride) == 0):  #insert node to hash dict
                            k = (ro.Left.depth - 1) / self.stride
                            if k in self.hash.keys():
                                self.hash[k].append(ro.Left)
                            else:
                                self.hash[k] = [ro.Left]
                    ro = ro.Left


    def LookUP(self,_string):
        print "ip address:", _string
        slash = _string.index("/")
        ip = _string[:slash]
        netmask = _string[slash + 1:]
        netmask = int(netmask) + 1
        netmask = netmask - 1

        net = ''.join([bin(int(x) + 256)[3:] for x in ip.split('.')])
        _string = net[:netmask]

        print "Binary network ip address:",_string,"\n"
        ro = self.Root
        nexhop = "-"
        if ro.Prefix != "": nexhop = ro.NextHop
        for i in range(len(_string)):
            if ro.Prefix != "":
                nexhop = ro.NextHop

            if _string[i] == "0":
                if ro.Left != None:
                    ro = ro.Left
                else: return ro
            if _string[i] == "1":
                if ro.Right != None:
                    ro = ro.Right
                else: return ro
        return ro

    def lookup_bitmap(self,_string):
        print "ip address:", _string
        slash = _string.index("/")
        ip = _string[:slash]
        netmask = _string[slash + 1:]
        netmask = int(netmask) + 1
        netmask = netmask - 1

        net = ''.join([bin(int(x) + 256)[3:] for x in ip.split('.')])
        _string = net[:netmask]

        print "Binary network ip address:",_string,"\n"

        flag = 0
        index = len(_string)/self.stride
        #find appropriate subtrie to search the next hop for ip add
        for i in range(0,index+1):
            if(i < len(self.hash)):
                for j in range(len(self.hash[i])):
                    if self.hash[i][j].Prefix == _string [0:(i*4)] + "*":
                        remain = _string[i*4:]      #divide IP add to stride size
                        if(len(remain) > 4): remain = remain[0:4]
                        if remain != "":
                            if len(remain) >= 4: remain = remain[0:3]
                            id = remain[len(remain)-1]    #this bit for determination the NH of prefix node
                            remain= remain[:len(remain)-1] + "*"
                            _index = bitmap2[remain]
                            nh = self.PCTrie_BitMap[i][j][_index].node[int(id)].NextHop #determination prefix node by bitmap
                            count_last = _index
                            while count_last > 0 and self.PCTrie_BitMap[i][j][count_last].real == 0:
                                if count_last % 2 == 0: count_last = count_last - 1
                                if (self.PCTrie_BitMap[i][j][count_last / 2].node[0].NextHop != nh and self.PCTrie_BitMap[i][j][count_last / 2].node[1].NextHop != nh):
                                    print "Removed Node in PC-Trie"
                                    break
                                count_last = count_last / 2   # determination prefix by parent of node
                            if (count_last == 0 and self.PCTrie_BitMap[i][j][count_last].real == 0):
                                print "Removed Node in PC-Trie"
                        else:
                            nh = self.hash[i][j].NextHop        #exception
                            if self.hash[i][j].Left.real == 1 and self.hash[i][j].Right.real==1: print "Removed Node in PC-Trie"
                            count_last =0
                        count_node = (j*7)+count_last+1
                        if(i>0):
                            for k in range(0,i):
                                count_node = count_node + len(self.PCTrie_BitMap[k])*7

                        print "Level of tree:", i
                        print "SubTrie: ST", j
                        print "Node",count_node
                        print "Next Hop:", nh
                        print "--------------------------------------------"

    def Create_PCTrie(self):
        for key, value in self.SubTrie.items():
            self.PCTrie_BitMap[key]=[]
            for r in value:
                pcNode = []   #collection of pcnode in each subtrie
                for i in range(self.compSize-1, pow(2,self.stride)-1, self.compSize):
                    tmp = PCTrieNode() #collection of node in pctrie node
                    # all sibling nodes must be filled if one of them contains NHI
                    for j in range(i,i+self.compSize):
                        if (r[j].real == 1):
                            for k in range(i, i+self.compSize):
                                r[k].real = 1
                                tmp.real = 1
                        tmp.node.append(r[j])
                    pcNode.append(tmp)
                self.PCTrie_BitMap[key].append(pcNode)
                #remove redundancy
                for i in range(0,len(pcNode)/2):
                    if(pcNode[(2*i)+1].real ==1 and pcNode[(2*i)+2].real ==1):
                        pcNode[i].real = 0

    def show(self):
        index = 1
        for key, value in self.PCTrie_BitMap.items():
            print "\nLevel", key, ":",
            for i in range(len(value)):
                print "\nSubTrie",i,":",
                for j in value[i]:
                    print index,",",j.node[0].NextHop,j.node[1].NextHop,j.real,"-",
                    index = index + 1

    def Create_tree_Bitmap(self):
        for key, value in self.hash.items():
            self.SubTrie[key] = []
            for i in range(len(value)):
                nodes = []
                stack = [value[i]]
                while(stack):
                    cur_node = stack[0]
                    stack = stack[1:]
                    nodes.append(cur_node)
                    if((cur_node.depth + 1) <= (1 + key) * self.stride):
                        if(cur_node.Left == None) : #convert SubTrie to full tree
                            cur_node.Left = Node()
                            cur_node.Left.depth = cur_node.depth + 1
                            cur_node.Left.Prefix = cur_node.Prefix[0:len(cur_node.Prefix)-1]+"0*"
                            cur_node.Left.NextHop = cur_node.NextHop
                            cur_node.Left.real = 0
                        stack.append(cur_node.Left)
                        if(cur_node.Right == None): #convert SubTrie to full tree
                            cur_node.Right = Node()
                            cur_node.Right.depth = cur_node.depth + 1
                            cur_node.Right.Prefix = cur_node.Prefix[0:len(cur_node.Prefix)-1]+"1*"
                            cur_node.Right.NextHop = cur_node.NextHop
                            cur_node.Right.real = 0
                        stack.append(cur_node.Right)

                self.SubTrie[key].append(nodes) #create BitMap

    def read_file_id(self,id):
        num = int(id[len(id)-1])+ int(id[len(id)-2])
        r = 1
        fr = open("input.txt", "rb")
        lr = open("Data.txt", "w")
        for line in fr:
            if ((r - num*10) >= 0 and (r - num*10) % num == 0 and 0 <= (r - num*10) / num <= 99):
                lr.write('%s' % line)
            if (r > 109*num): break
            r = r + 1
        fr.close()
        lr.close()
    def read_file(self):
        tmp = []
        tmp.append(("*", "144.228.241.81"))
        fr = open("Data.txt", "rb")
        for line in fr:
            c = line[:len(line)].split()
            slash = c[2].index("/")
            ip = c[2][:slash]
            nh = c[len(c) - 1]

            netmask = c[2][slash + 1:]
            netmask = int(netmask) + 1
            netmask = netmask - 1

            net = ''.join([bin(int(x) + 256)[3:] for x in ip.split('.')])
            ip = net[:netmask]
            tmp.append((ip + "*", nh))

        for i in range(len(tmp) - 1, -1, -1):     # sort ip add
            for j in range(1, i + 1):
                if len(tmp[j - 1][0]) > len(tmp[j][0] or (len(tmp[j - 1][0]) == len(tmp[j][0]) and tmp[j - 1][0] > tmp[j][0])):
                    tmp1 = tmp[j - 1]
                    tmp[j - 1] = tmp[j]
                    tmp[j] = tmp1
        return tmp
    
    def show_node(self,count):
        print "\nContents of node",count,":\n"
        index = 1
        for key, value in self.PCTrie_BitMap.items():
            for i in range(len(value)):
                child = 0
                for j in value[i]:
                    if index == count:
                        if j.real == 0: print "NextHop: None"
                        if j.real == 1: print "NextHop:",j.node[0].NextHop,",",j.node[1].NextHop
                        if ((2*child) + 1 >= len(value[i])):
                            print "Left Pointer:", child + count + 1, " , None"
                        if (2*child+1 < len(value[i]) and (value[i][(2*child)+1] == None or value[i][(2*child)+1].real == 0)):
                            print "Left Pointer:",child+count+1," , None"
                        if ((2*child) + 1 < len(value[i]) and value[i][(2*child)+1] != None and value[i][(2*child)+1].real == 1):
                            print "Left Pointer:",child+count+1," , ",value[i][(2*child)+1].node[0].NextHop,",",value[i][(2*child)+1].node[1].NextHop
                        if ((2 * child) + 2 >= len(value[i])):
                            print "Right Pointer:",child+count+2," , None"
                        if ((2*child) + 2 < len(value[i]) and (value[i][(2 * child) + 2] == None or value[i][(2 * child) + 2].real == 0)):
                            print "Right Pointer:", child + count + 2, " , None"
                        if ((2*child) + 2 < len(value[i]) and value[i][(2*child)+2] != None and value[i][(2 * child) + 2].real == 1):
                            print "Right Pointer:",child+count+2," , ",value[i][(2*child)+2].node[0].NextHop,",",value[i][(2*child)+2].node[1].NextHop
                    index = index + 1
                    child = child + 1

def main():
    trie = Trie()
    #trie.read_file_id("95131023")
    tmp = trie.read_file()
    for i in tmp:   trie.add(i[0],i[1])         #Routing Table Construction
    trie.Create_tree_Bitmap()                   #creat Tree Bitmap and independant subtries
    trie.Create_PCTrie()                        #Prefix-Compressed Trie Construction

    #Test COD:

    trie.lookup_bitmap("8.64.0.0/10")        #Lookup and Membership Queries
    #trie.show()                                #show BEF search of tree
    #trie.show_node(464)                         #shoe contents of node

main()

