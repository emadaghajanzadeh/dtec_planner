class States:

    def __init__(self, stateList) -> None:
        self.stateList = stateList
        self.initialStates = []
        self.finalStates = []
        for state in stateList:
            if state.isStartState:
                self.initialStates.append(state)
            if state.isFinalState:
                self.isFinalState.append(state)
    
    def getInitialStates(self):
        return self.initialStates

    def getFinalStates(self):
        return self.finalStates
    
    