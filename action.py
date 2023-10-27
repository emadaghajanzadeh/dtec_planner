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


    def __repr__(self):
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

        # Filter out attributes with None values
        filtered_attributes = [attr for attr in attributes if attr.split("=")[1] is not None]

        return f"Action({', '.join(filtered_attributes)})"
    

    def getObjectives(self):
        '''
        Get all objectives on which the optimization should be performed
        ! Ask how to sum deliveryTimeLatestInWeeks with the other two variables
        '''
        objectives = {}
        objectives["cost"] = self.costs
        objectives["workingTimeInHours"] = self.workingTimeInHours
        maxDeliveryTime = 0
        for precondition in self.preconditions:
            maxDeliveryTime = max(maxDeliveryTime, precondition["deliveryTimeLatestInWeeks"])
        objectives["TotalTimeInWeeks"] = self.processingTimeInWeeks + maxDeliveryTime

        return objectives






