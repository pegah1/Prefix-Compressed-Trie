import math
import string
from collections import OrderedDict
from operator import itemgetter

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
    
def main():
    trie = Trie()
    tmp = trie.read_file()
    for i in tmp:   trie.add(i[0],i[1])         #Routing Table Construction
    

main()

