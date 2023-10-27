#--------------Fringe-related functions---------------------------
traversalMethod = ""
fringe = None

def setTraversalMethod(method):
   global traversalMethod
   traversalMethod = method

def printFringe():
   print(fringe)
   pass

def initFringe():
    '''Since the initialization can vary depending on the traversal method'''
    global fringe
    fringe = []


def insert(stateSet):
   if traversalMethod == "BFS":
    fringe.append(stateSet)
   

def pop():
   global fringe
   return fringe.pop(0)

def isEmpty():
   if len(fringe)==0:
      return True
   return False