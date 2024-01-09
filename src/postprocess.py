import matplotlib.pyplot as plt
plt.ioff()


def findProvider(plan, precondIDList):
    '''This function recieves a list of pre-conditions and returns the time of the longest action among
    all actions that provide that pre-condition.'''
    max_length = 0
    for preconID in precondIDList:
        for action in reversed(plan):
            if action.finalState.id == preconID:
                length = action.startingPoint + action.processingTimeInWeeks
                max_length = max(max_length, length)
                continue
    return max_length

def findProviderV2(plan, precondList):
    '''This function recieves a list of pre-conditions and returns the time of the longest action among
    all actions that provide that pre-condition.'''
    optimal_start = 0
    for precon in precondList:
        state_object , deliveryTimeLatestInWeeks = precon['state_object'], precon['deliveryTimeLatestInWeeks']
        for action in reversed(plan):
            if action.finalState == state_object:
                length = action.startingPoint + action.processingTimeInWeeks
                length = length - deliveryTimeLatestInWeeks
                optimal_start = max(optimal_start, length)
                continue

    return optimal_start

# Plot functions
def timelines(y, xstart, xstop, color='b'):
    """Plot timelines at y from xstart to xstop with given color."""   
    plt.hlines(y, xstart, xstop, color, lw=4)
    plt.vlines(xstart, y+0.03, y-0.03, color, lw=2)
    plt.vlines(xstop, y+0.03, y-0.03, color, lw=2)

def ScheduleVisualization(plan):

    fig = plt.figure(figsize=(10,3))
    # Extract data from the plan
    y_values = list(range(len(plan)))
    x_start_values = [action.startingPoint for action in plan]
    x_stop_values = [action.endingPoint for action in plan]

    # Plot timelines
    for y, xstart, xstop in zip(y_values, x_start_values, x_stop_values):
        timelines(y, xstart, xstop)

    # Set labels and title
    plt.yticks(y_values, [str(action) for action in plan])
    plt.xlabel("Time (In Week)")
    plt.title("Timelines the Plan")
    plt.savefig(f"./outputs/schedule_outputs/plan{plan.planId}")
    
def SchedulePrinting(plan):
    print("Schedule Info:")
    for action in reversed(plan):
        print(f"{action}: [ {action.startingPoint}, {action.endingPoint} ]")
    print()

def postprocess(plans):
    for plan in plans:
        starting_points = {}
        for action in reversed(plan):
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
                length = findProviderV2(plan, action.preconditions)
                # This length variable shows when the action a is provided with the first pre-condition
                action.startingPoint = length
                action.endingPoint = action.startingPoint + action.processingTimeInWeeks
            else:
                length = findProvider(plan, action.minDeliveryTimeStateID)
                action.startingPoint = length - action.minDeliveryTime
                action.endingPoint = action.startingPoint + action.processingTimeInWeeks

        ScheduleVisualization(plan)
        SchedulePrinting(plan)
        


    return
