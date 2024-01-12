
def get_Init_Final_States(stateList):
   """This function checks the list of states and returns initial and final states."""
   initialStates = set()
   finalStates = set()
   for state in stateList:
      if state.isStartState:
            initialStates.add(state)
      if state.isFinalState:
            finalStates.add(state)
   return initialStates, finalStates

def isGoalAchieved(StateList, finalStates):
   """ 
   This function checks if all final states are present in the current states. 
   Since we do not have any negative state, we just need to calculate
   the subset condition.
   """
   if finalStates.issubset(StateList): return True
   return False

def isGoalAchievedBackward(StateList, initialStates):
   """
   This function checks if all current states are initial states. 
   The principal is a little different from the forwaerd version,
   where all final states should be met.
   """
   if StateList.issubset(initialStates): return True
   return False
