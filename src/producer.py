class Producer():

    def __init__(self, id, name, trade, valueChainParameters=None) -> None:
        self.id = id    #int
        self.name = name    #string
        self.trade = trade  #string
        self.valueChainParameters = valueChainParameters    #dict

    def __repr__(self) -> str:
        return f"Producer(id={self.id}, name='{self.name}', trade='{self.trade}', valueChainParameters={self.valueChainParameters})"
    
    def getValueChainParameters(self):
        return self.valueChainParameters
    def getAllAttributes(self):
        return {
            "id": self.id,
            "name": self.name,
            "trade": self.trade,
            "valueChainParameters": self.valueChainParameters
        }
