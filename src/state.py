class State:
    def __init__(self, id, name, isStartState=False, isFinalState=False) -> None:
        self.id = id
        self.name = name
        self.isStartState = isStartState
        self.isFinalState = isFinalState

    def __repr__(self) -> str:
        # return f"State(id={self.id}, name='{self.name}, isStartState='{self.isStartState}', isFinalState='{self.isFinalState}' )"
        return f"State(id={self.id})"
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return isinstance(other, State) and self.id == other.id
    
    def getAllAttributes(self):
        return {
            "id": self.id,
            "name": self.name,
            "isStartState": self.isStartState,
            "isFinalState": self.isFinalState
        }