class Action:

    def __init__(self, id, initialState, finalState, preconditions, costs, producer, processingTimeInWeeks, workingTimeInHours) -> None:
        self.id = id
        self.initialState = initialState
        self.finalState = finalState
        if preconditions == None:
            self.preconditions = []
        else:
            self.preconditions = preconditions
        self.preconditions.append({"state_object": initialState, "deliveryTimeLatestInWeeks": 0})
        self.costs = costs
        self.producer = producer
        self.processingTimeInWeeks = processingTimeInWeeks
        self.workingTimeInHours = workingTimeInHours
        self.objectives = {}

        # These attributes are helpful for the post-processing (schduling after planning)
        self.onlyInitialStates = True
        for precon in self.preconditions:
            if not precon['state_object'].isStartState:
                self.onlyInitialStates = False
                break
        
        self.maxDeliveryTime = 0
        self.maxDeliveryTimeStateID = []
        self.minDeliveryTime = 1000000 # A large number
        self.minDeliveryTimeStateID = []
        for precon in self.preconditions:
            if precon['deliveryTimeLatestInWeeks'] >= self.maxDeliveryTime:
                self.maxDeliveryTime = precon['deliveryTimeLatestInWeeks']
                self.maxDeliveryTimeStateID.append(precon['state_object'].id)
            if precon['deliveryTimeLatestInWeeks'] <= self.minDeliveryTime:
                self.minDeliveryTime = precon['deliveryTimeLatestInWeeks']
                self.minDeliveryTimeStateID.append(precon['state_object'].id)

        self.startingPoint = -1
        self.endingPoint = -1

    def __repr__(self) -> str:
        attributes = [
            f"id={self.id}",
            # f"initialStateId={self.initialState}",
            # f"finalStateId={self.finalState}",
            # f"preconditions={self.preconditions}",
            # f"costs={self.costs}",
            # f"producerId={self.producer}",
            # f"processingTimeInWeeks={self.processingTimeInWeeks}",
            # f"workingTimeInHours={self.workingTimeInHours}",
        ]

        filtered_attributes = [attr for attr in attributes if attr.split("=")[1] is not None]
        return f"Action({', '.join(filtered_attributes)})"
    
    def __str__(self) -> str:
        return f"Action(id={self.id})"
    
    def getAllAttributes(self) -> dict:
        """This function returns all attributes of this class as a dictionary."""
        pre_conditions_serializable = [elm["state_object"].getAllAttributes() for elm in self.preconditions]
        return {
            "id": self.id,
            # Since initial state is included in the pre-conditions
            # "initialStateId": self.initialState.getAllAttributes(),
            "preconditions": pre_conditions_serializable,
            "finalStateId": self.finalState.getAllAttributes(),
            "startingPoint": self.startingPoint,
            "endingPoint": self.endingPoint,
            "costs": self.costs,
            "producerId": self.producer.getAllAttributes(),
            "processingTimeInWeeks": self.processingTimeInWeeks,
            "workingTimeInHours": self.workingTimeInHours
        }

    def getObjectives(self) -> dict:
        """This function gets all objectives on which the optimization should be performed and returns them as a dictionary."""
        self.objectives["cost"] = self.costs
        self.objectives["workingTimeInHours"] = self.workingTimeInHours
        maxDeliveryTime = 0
        for precondition in self.preconditions:
            maxDeliveryTime = max(maxDeliveryTime, precondition["deliveryTimeLatestInWeeks"])
        self.objectives["totalTimeInWeeks"] = self.processingTimeInWeeks + maxDeliveryTime

        for parameter, value in self.producer.valueChainParameters.items():
            self.objectives[parameter] = value

        return self.objectives

    def __eq__(self, otherAction: object) -> bool:
        if isinstance(otherAction, Action):
            return self.id == otherAction.id
        return False
    
    def isEqualSchedule(self, otherAction: object) -> bool:
        """This function will be called to check if two actions which are the same are also scheduled the same way in two differen plans"""
        if self == otherAction:
            if (self.startingPoint == otherAction.startingPoint) and (self.endingPoint == otherAction.endingPoint):
                return True
        return False




