import copy
import matplotlib.pyplot as plt
import itertools
# Plot functions
def timelines(y, xstart, xstop, color='b'):
    """Plot timelines at y from xstart to xstop with given color."""   
    plt.hlines(y, xstart, xstop, color, lw=4)
    plt.vlines(xstart, y+0.03, y-0.03, color, lw=2)
    plt.vlines(xstop, y+0.03, y-0.03, color, lw=2)


class Plan():
    id_iter = itertools.count()

    def __init__(self, actionSequence) -> None:
        self.setActionSequence(actionSequence)
        self.planId = next(self.id_iter)
        
    def setActionSequence(self, actionSequence):
        self.actionSequence = copy.deepcopy(actionSequence[::-1])

    def getActionSequence(self):
        return self.actionSequence

    def getPlanId(self):
        return self.planId
    
    def computePlanValue(self, optimizationCriteria = "cost"):
        self.planValue = sum(action.getObjectives()[optimizationCriteria] for action in self.getActionSequence())
        return self.planValue
    
    def getPlanValue(self):
        return self.planValue
        
    def getPlanVisualization(self):
        plt.figure(figsize=(10,4))
        # Extract data from the plan
        y_values = list(range(len(self.getActionSequence())))
        time_step = 0
        for index,action in enumerate(self.getActionSequence()):
            starting_time = time_step
            ending_time = starting_time + action.processingTimeInWeeks
            timelines(index, starting_time, ending_time)
            time_step = ending_time
        # Set labels and title
        plt.yticks(y_values, [str(action) for action in self.getActionSequence()])
        plt.xlabel("Time (In Week)")
        plt.title(f"Timeline of Plan {self.getPlanId()}, Value: {self.getPlanValue()}")
        plt.savefig(f"./outputs/planner_outputs/plan{self.getPlanId()}")

    def findProvider(self, precondIDList):
        '''This function recieves a list of pre-conditions and returns the time of the longest action among
        all actions that provide that pre-condition.'''
        max_length = 0
        for preconID in precondIDList:
            for action in self.getActionSequence():
                if action.finalState.id == preconID:
                    length = action.startingPoint + action.processingTimeInWeeks
                    max_length = max(max_length, length)
                    continue
        return max_length
    
    def findProviderV2(self, precondList):
        '''This function recieves a list of pre-conditions and returns the time of the longest action among
        all actions that provide that pre-condition.'''
        optimal_start = 0
        for precon in precondList:
            state_object , deliveryTimeLatestInWeeks = precon['state_object'], precon['deliveryTimeLatestInWeeks']
            for action in self.getActionSequence():
                if action.finalState == state_object:
                    length = action.startingPoint + action.processingTimeInWeeks
                    length = length - deliveryTimeLatestInWeeks
                    optimal_start = max(optimal_start, length)
                    continue

        return optimal_start

    def getScheduleVisualization(self):
        fig = plt.figure(figsize=(10,4))
        # Extract data from the plan
        y_values = list(range(len(self.getActionSequence())))
        x_start_values = [action.startingPoint for action in self.getActionSequence()]
        x_stop_values = [action.endingPoint for action in self.getActionSequence()]

        # Plot timelines
        for y, xstart, xstop in zip(y_values, x_start_values, x_stop_values):
            timelines(y, xstart, xstop)

        # Set labels and title
        plt.yticks(y_values, [str(action) for action in self.getActionSequence()])
        plt.xlabel("Time (In Week)")
        plt.title(f"Timeline of Plan {self.getPlanId()}, Value: {self.getPlanValue()}")
        plt.savefig(f"./outputs/schedule_outputs/plan{self.planId}")

    def schedulePrinting(self):
        print("Schedule Info:")
        for action in self.getActionSequence():
            print(f"{action}: [ {action.startingPoint}, {action.endingPoint} ]")
        print()

    def schedule(self):
        starting_points = {}
        for action in self.getActionSequence():
            # print(action)
            # print(action.preconditions)
            # Check if all preconditions are initial states:
            if action.onlyInitialStates:
                action.startingPoint = 0
                action.endingPoint = action.processingTimeInWeeks
                continue
            # Reaching here means we are dealing with actions dependent on result of another action
            if action.minDeliveryTime == 0:
                # length = findProvider(plan, action.minDeliveryTimeStateID)
                length = self.findProviderV2(action.preconditions)
                # This length variable shows when the action a is provided with the first pre-condition
                action.startingPoint = length
                action.endingPoint = action.startingPoint + action.processingTimeInWeeks
            else:
                length = self.findProvider(action.minDeliveryTimeStateID)
                action.startingPoint = length - action.minDeliveryTime
                action.endingPoint = action.startingPoint + action.processingTimeInWeeks

        # self.getScheduleVisualization()
        # self.schedulePrinting()

    def getDictInfo(self):
        plan_dict = {}
        actions = []
        for action in self.getActionSequence():
            actions.append(action.getAllAttributes())
            plan_dict["plan_id"] = self.getPlanId()
            plan_dict["plan_value"] = self.getPlanValue()
            plan_dict["actions"] = actions
        return plan_dict


    def __eq__(self, secondPlan):
        if not isinstance(secondPlan, Plan):
            return False
        if len(self.getActionSequence()) != len(secondPlan.getActionSequence()):
            return False
        for action in self.getActionSequence():
            isequal = False
            for actionSecondPlan in secondPlan.getActionSequence():
                if action.isEqualSchedule(actionSecondPlan):
                    isequal = True
            if not isequal:
                return False
        return True

    def __str__(self):
        """When the plan is called directly to be printed, print(planObject)"""
        printingString = ""
        printingString += f"PlanID {self.getPlanId()}: \n"
        printingString += "Action Sequence: "
        for action in self.actionSequence[:-1]:
            printingString += (f"{action} => ")
        printingString += (f"{self.actionSequence[-1]} \n")
        printingString += f"Value: {self.getPlanValue()}"
        return printingString
    
    def __repr__(self):
        """When a list of plans are called to be printed, print(listOfPlans)"""
        printingString = ""
        for action in self.actionSequence[:-1]:
            printingString += str(action)
        printingString += str(self.actionSequence[-1])
        return printingString