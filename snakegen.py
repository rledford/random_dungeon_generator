'''
Created on Oct 14, 2014

@author: Ryan Ledford
'''
import random

import pygame


class Node(object):
    def __init__(self, ID, position):
        self.ID = ID
        self.position = position
        self.width = 1
        self.height = 1
    def __str__(self):
        return "ID:%d\nXY:%d,%d\nWH:%d,%d"%(self.ID,self.position.x,self.position.y,self.width,self.height)
    @property
    def rect(self):
        return pygame.Rect(self.left,self.top,self.width,self.height)
    @property
    def top(self):
        return int(self.position.y - self.height/2)
    @property
    def bottom(self):
        return int(self.position.y + self.height/2)
    @property
    def left(self):
        return int(self.position.x - self.width/2)
    @property
    def right(self):
        return int(self.position.x + self.width/2)
    
class Portal(object):
    def __init__(self, position):
        self.position = position
        
    @property
    def intPos(self):
        return (int(self.position.x),int(self.position.y))
    
    def Draw(self, surface):
        pygame.draw.circle(surface, (128,255,128), self.intPos, 3, 0)
    
class MapGenerator(object):
    def __init__(self):
        """
        With this generator, it would be better to start a playable character in
        a node that is around the middle of the number of nodes in the map.
        Objectives, quests, and items could be placed in nodes outside of the nodes
        in the players starting range. When a node is chosen as the players starting
        location, no enemies will be spawned there. The adjacent rooms could have
        weaker enemies to ease the player into the new level (or not).
        Example: There are 50 nodes on the map. The player starts between node
        20 and node 30. This gives at least 2 paths for the player to choose to take.
        Now you decide to place quest givers and items in nodes in a different range.
        We can use nodes 10 to 19 and also 31 to 35 for quest givers and items.
        With the remaining nodes, you could designate that the range 36 to 45 and
        0 through 9 have treasures and maybe some harder enemies, then 46 through
        49 could contain a boss, or mini-boss and the exit to the next level.
        This would eliminate the fact that there could only be one way to navigate
        through the map like if the player started at nodeID 0 (zero), then they would
        just have to move from room to room until the reach the end (boring).
        """
        self.nextID = 0         #will match a nodes index in the nodes[] collection
        self.nodes = []         #collection of nodes
        self.links = []         #collection of node relationships
        self.portals = []       #collection of portals
        self.nodeMap = []       #order of placement and relationships [parent,child,dirX,dirY]
        self.numNodes = 50      #maximum number of nodes to generate
        self.overlapThreshold = 0#reject 'this' percent of overlapping nodes
        self.minInflation = 16  #minimum number of units a node must be inflated to
        self.maxInflation = 48  #maximum number of units a node can be inflated to
        self.maxMapWidth = 600  #limit how width of map
        self.maxMapHeight = 300 #limit how height of map
        self.width = 1          #will update when __Shift is called
        self.height = 1         #will update when __Shift is called
        
        #font for debugging only
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 20, False, False)
        self.startNodeRangeLow = 0.45#percentage of len(nodes) to use
        self.startNodeRangeHigh = 0.55#percentage of len(nodes) to use
        self.startNode = 0
        
    def __NextID(self):
        ID = self.nextID
        self.nextID += 1
        return ID
        
    def __PlaceNodesRandom(self):
        for i in xrange(self.numNodes):
            placing = True
            tryCount = 5
            while(placing):
                pos = pygame.math.Vector2(random.randint(0, self.desiredSize),random.randint(0, self.desiredSize))
                if not self.__IsValidPosition(pos):
                    tryCount -= 1
                    if tryCount <= 0:
                        placing = False
                else:
                    placing = False
                    self.nodes.append(Node(self.__NextID(), pos))
        self.__InflateNodes()
        self.__HandleOverlap()
    
    def __PlaceNodesBlindMan(self):
        #SNAKE / BLIND MAN
        maxX = (self.maxMapWidth-self.maxInflation)/2
        maxY = (self.maxMapHeight-self.maxInflation)/2
        self.nodes.append(Node(self.__NextID(), pygame.math.Vector2(0,0)))
        self.nodes[0].width = random.randint(self.minInflation, self.maxInflation)
        self.nodes[0].height = random.randint(self.minInflation, self.maxInflation)
        directions = [pygame.math.Vector2(0,1),pygame.math.Vector2(0,-1),pygame.math.Vector2(-1,0),pygame.math.Vector2(1,0)]
        self.centroid = pygame.math.Vector2(0,0)
        nWidth = 0
        nHeight = 0
        refNode = 0
        n = 1
        while n < self.numNodes:
            if refNode < -1:
                print "unable to place all nodes due to size constraints"
                break
            newDirection = directions.pop(random.randint(0,len(directions)-1))
            x = 0#newDirection.x
            y = 0#newDirection.y
            if newDirection.x != 0:
                x = self.nodes[refNode].position.x + ((self.nodes[refNode].width/2 + self.maxInflation/2)*newDirection.x)#NEVER CHANGE
                y = self.nodes[refNode].position.y# + nHeight/4*random.randint(-1,1)
                nWidth = self.maxInflation
                nHeight = random.randint(self.minInflation, self.maxInflation)
            if newDirection.y != 0:
                x = self.nodes[refNode].position.x# + nWidth/4*random.randint(-1,1)
                y = self.nodes[refNode].position.y + ((self.nodes[refNode].height/2 + self.maxInflation/2)*newDirection.y)#NEVER CHANGE
                nWidth = random.randint(self.minInflation, self.maxInflation)
                nHeight = self.maxInflation
            if nWidth%2 != 0:
                nWidth+=1
            if nHeight%2 != 0:
                nHeight+=1
            position = pygame.math.Vector2(x,y)
            newNode = Node(self.__NextID(), position)
            newNode.width = nWidth
            newNode.height = nHeight
            distX = abs(self.nodes[0].position.x - x)
            distY = abs(self.nodes[0].position.y - y)
            if self.__IsValidArea(newNode.rect) and distX < maxX and distY < maxY:
                self.nodes.append(newNode)
                self.links.append([refNode,n,newDirection.x,newDirection.y])
                n += 1
                refNode = n-1
                directions = [pygame.math.Vector2(0,1),pygame.math.Vector2(0,-1),pygame.math.Vector2(-1,0),pygame.math.Vector2(1,0)]
            if len(directions) == 0:
                directions = [pygame.math.Vector2(0,1),pygame.math.Vector2(0,-1),pygame.math.Vector2(-1,0),pygame.math.Vector2(1,0)]
                refNode-=1
    
    def __InflateNodes(self):
        for i in xrange(len(self.nodes)):
            #make sure w and h area even numbers so division is symmetric
            w = random.randint(self.minInflation,self.maxInflation)
            if w%2 != 0:
                w+=1
            h = random.randint(self.minInflation,self.maxInflation)
            if h%2 != 0:
                h+=1
            self.nodes[i].width = w
            self.nodes[i].height = h
            
    def __DisplaceSurroundingNodes(self, ignoredNodeIndex):
        pos = self.nodes[ignoredNodeIndex].position
        xDisplacement = self.nodes[ignoredNodeIndex].width/2
        yDisplacement = self.nodes[ignoredNodeIndex].height/2
        for i in xrange(len(self.nodes)):
            if i == ignoredNodeIndex:
                continue
            xDisplacementDirection = self.__GetUnitDisplacementDirection(-(pos.x-self.nodes[i].position.x))
            yDisplacementDirection = self.__GetUnitDisplacementDirection(-(pos.y-self.nodes[i].position.y))
            self.nodes[i].position.x += xDisplacementDirection*xDisplacement
            self.nodes[i].position.y += yDisplacementDirection*yDisplacement
            
    def __JoinNodes(self):#should be called last
        for i in xrange(len(self.links)):
            sourceNode,destinationNode,dirX,dirY = self.links[i]
            n = self.nodes[sourceNode]
            x = n.position.x + (n.width/2*dirX)
            y = n.position.y + (n.height/2*dirY)
            self.portals.append(Portal(pygame.math.Vector2(x,y)))
            
    def __GetUnitDisplacementDirection(self, value):
        if value < 0:
            return -1
        if value > 0:
            return 1
        return 0
                    
    def __Shift(self):
        """
        Find the minimum x and y values and shift
        all nodes by that amount to move them all
        into the positive sides of the origin (0,0)
        """
        minX = 0
        minY = 0
        maxX = 0
        maxY = 0
        for i in xrange(len(self.nodes)):
            if self.nodes[i].left < minX:
                minX = self.nodes[i].left
            if self.nodes[i].top < minY:
                minY = self.nodes[i].top
        """
                            NOTE
        Subtracting an extra 1 from the minX minY values and
        adding an extra 1 to the maxX maxY values ensures that
        there will be one unit between the top, bottom,
        left and right edges of the map and the closest node.
        """
        for i in xrange(len(self.nodes)):
            """
                        OBSERVATION
            If minX < 0 all negative x's would need to be
            shifted by the opposite amount to move in the correct direction
            hence the -= used to change position
            """
            self.nodes[i].position.x -= minX-1#subtract an extra 1
            self.nodes[i].position.y -= minY-1#subtract an extra 1
            #find maxX and maxY
            if self.nodes[i].right > maxX:
                maxX = self.nodes[i].right
            if self.nodes[i].bottom > maxY:
                maxY = self.nodes[i].bottom
        self.width = maxX+1#add an extra 1
        self.height = maxY+1#add an extra 1
        print "max nodes:",self.numNodes
        print "actual nodes:",len(self.nodes)
        print "maximum size:",self.maxMapWidth,":",self.maxMapHeight
        print "actual size: ",self.width,":",self.height
    
    def Generate(self):
        self.nextID = 0
        self.nodes = []#clear the current node container
        self.portals = []
        self.links = []
        self.__PlaceNodesBlindMan()
        self.__Shift()
        self.__JoinNodes()
        #get start node
        self.startNode = random.randint(int(len(self.nodes)*self.startNodeRangeLow),int(len(self.nodes)*self.startNodeRangeHigh))
        print "start node:",self.startNode
        print "************************************"
                
    def __IsValidArea(self, rect):
        for n in self.nodes:
            if n.rect.colliderect(rect):
                return False
        return True
            
    def __IsValidPosition(self, pos):
        for i in xrange(len(self.nodes)):
            if self.nodes[i].position.x == pos.x and self.nodes[i].position.y == pos.y:
                return False
        return True
    
    def __CheckInflation(self,ignoredNodeIndex):
        n = self.nodes[ignoredNodeIndex]#for convenience and clarity
        for i in xrange(len(self.nodes)):
            if i == ignoredNodeIndex:
                continue
            if n.rect.colliderect(self.nodes[i].rect):
                return False
        return True
    
    def __HandleOverlap(self):
        for i in xrange(len(self.nodes)-1,-1,-1):
            #check if overlap should be considered for  fixing
            if random.random() > self.overlapThreshold:
                continue
            for n in xrange(len(self.nodes)):
                if n == i:
                    continue
                if (self.nodes[i].rect.colliderect(self.nodes[n].rect)):
                    self.nodes.pop(i)
                    break
    
    def Draw(self, surface):
        pygame.draw.rect(surface, (128,128,128), pygame.Rect(0,0,self.width, self.height), 0)
        for i in xrange(len(self.nodes)):
            n = self.nodes[i]
            r = n.rect#pygame.Rect(n.position.x-n.width/2,n.position.y-n.height/2,n.width, n.height)
            if i != self.startNode:
                pygame.draw.rect(surface, (128,255,128), r, 0)
            else:
                pygame.draw.rect(surface, (128,128,255), r, 0)
            w,h = self.font.size(str(i))
            surface.blit(self.font.render(str(i),True, (0,0,0)),(int(n.position.x-w/2),int(n.position.y-h/2)))
            pygame.draw.rect(surface, (255,64,64), r, 1)
        for portal in self.portals:
            portal.Draw(screen)
            
            
pygame.init()

width = 600
height = 600

screen = pygame.display.set_mode((width,height))
clock = pygame.time.Clock()

FPS = 60.0
REFRESH = pygame.USEREVENT

pygame.time.set_timer(REFRESH, int(1000.0/FPS))

running = True

test = MapGenerator()
test.Generate()

while running:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            test.Generate()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r:
                pass
        if event.type == pygame.QUIT:
            running = False
        if event.type == REFRESH:
            screen.fill((0,0,0))
            test.Draw(screen)

    pygame.display.flip()
    
pygame.quit()
