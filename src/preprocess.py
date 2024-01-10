import json
import producer, state, action, plan
import fringe
import time
import postprocess
import matplotlib.pyplot as plt
# source /Users/emadaghajanzadeh/Documents/Work/Dtec/planner/planner_venv/bin/activate      

def jsonReader(jsonFilename):
   """
   This function gets the address of the Json file, extracts its content, and instantiates objects corresponding to data types.
   Input: Adress of the Jsonfile
   Output: 
         producer_objects: list of producer objects
         state_objects: list of state objects
         action_objects: list of action objects
         opt_criteria: a string shows the optimization goal (Can be changed to a list consists of multiple optimization criteria)
   """
   # Read the json file
   with open(jsonFilename) as f:
      data = json.load(f)
   # decode the json file
   for key,value_list in data.items():
      if key == "producer":
         producer_objects = []
         for value in value_list:
            producer_object = producer.Producer(id=value["id"], name=value["name"], trade = value["trade"],
                                                valueChainParameters = value.get("valueChainParameters", None))
            producer_objects.append(producer_object)
      if key == "states":
         state_objects = []
         for value in value_list:
            state_object = state.State(id=value["id"], name=value["name"], isStartState = value.get("isStartState", False), isFinalState = value.get("isFinalState", False))
            state_objects.append(state_object)
      if key == "processSteps":
         action_objects = []
         for value in value_list:
            # Finding State Objects
            initialStateId=value["initialStateId"]
            finalStateId=value["finalStateId"]
            preconditions_IDlist=value.get("preconditions", [])           
            preconditions_objects = []
            for state_object in state_objects:
               if state_object.id == initialStateId:
                  initialStateObject = state_object
               if state_object.id == finalStateId:
                  finalStateObject = state_object
               for precondition_dict in preconditions_IDlist:
                  if state_object.id == precondition_dict["id"]:
                     preconditions_objects.append({"state_object": state_object, "deliveryTimeLatestInWeeks":precondition_dict["deliveryTimeLatestInWeeks"]})
                     break
            
            # Finding Proucer Objects
            producerId=value.get("producerId", None)
            for producer_object in producer_objects:
               if producer_object.id == producerId:
                  producerObject = producer_object
                  break

            action_object = action.Action(id = value["id"],
                                          initialState = initialStateObject,
                                          finalState = finalStateObject,
                                          preconditions = preconditions_objects,
                                          costs=value.get("costs", None),
                                          producer = producerObject,
                                          processingTimeInWeeks=value.get("processingTimeInWeeks", None),
                                          workingTimeInHours=value.get("workingTimeInHours", None)
                                       )
            action_objects.append(action_object)
      if key == "optimizeFor":
         opt_criteria =  value_list
   return producer_objects, state_objects, action_objects, opt_criteria

def writeToJson(sortedPlans, outputFileName):
   """Writing the output into the Json file."""
   if len(sortedPlans) == 0:
      data = {"optimizeFor": optCriteria, "Minimum Plan": "-", "Maximum Plan":"-",
              "Number of Plans":0}
   else:
      data = {"optimizeFor": optCriteria, "Minimum Plan":sortedPlans[0].getPlanValue(), "Maximum Plan":sortedPlans[-1].getPlanValue()}
      data["Number of Plans"] = len(sortedPlans)
      plans_list = [] # list of dictionaries (plans)
      for plan in sortedPlans:
         plans_list.append(plan.getDictInfo())
      data["plans"] = plans_list
   json_object = json.dumps(data, indent=4)
   with open(outputFileName, "w") as outfile:
      outfile.write(json_object)


#--------------State-related functions---------------------------
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

#-----------------------------------------------------------------


#--------------Action-related functions---------------------------
def applicable(stateSet, actionPrecon):
   '''
   This function is used in a progression planner where we want to see if a 
   specific action can be applied based on the current set of states. For this,
   All pre-conditions of an action should be present among current states.
   '''
   precons = set([x["state_object"] for x in actionPrecon])
   if precons.issubset(stateSet):
      return True
   return False

def apply(actionPrecon, actionEffect, currentStateSet):
   '''
   This function will be called whenever a specific action is applicable.
   Firstly, the preconditions of that action are removed (assumption of consuming pre-conditions),
   and all effects of that action are also added.
   Input arguments:
      actionPrecon: set of objects of an action's preconditions
      actionEffect: set of objects of an action's effects
      currentStateSet: set contains all current states
   '''
   precons = set([x["state_object"] for x in actionPrecon])
   newStateSet = currentStateSet.difference(precons)
   newStateSet.add(actionEffect)
   return newStateSet

def applicableBackward(stateSet, actionEffect):
   '''
   This function checks if all effects of an action are present in the current states.
   If so, it means we can backtrack from this action.
   '''
   actioEffectSet = set()
   actioEffectSet.add(actionEffect)
   if actioEffectSet.issubset(stateSet):
      return True
   return False

def applyBackward(actionPrecon, actionEffect, currentStateSet):
   '''
   This function applies an action in the backward fashion. So, firstly, all
   effects of the action are removed and then all of its preconditions are added.
   '''
   actionEffectSet = set()
   actionEffectSet.add(actionEffect)
   newStateSet = currentStateSet.difference(actionEffectSet)
   for precon in actionPrecon:
      newStateSet.add(precon["state_object"])
   return newStateSet
#-----------------------------------------------------------------


#--------------Plan-related functions---------------------------
def forwardPlanning(initialStates, finalStates, actionObjects, traversalMethod):
   '''
   This function performs the forward planning, by considering a fringe where its element is a list
   with two elements [stateset,actionsequence], where stateset shows current states and actionsequence
   shows which actions have been taken that we reached this set of states. Then iteratively, all actions
   are tested to see if we can go backward or not.
   Input arguments:
         initialStates: set contains initial states
         finalsStates: set contains final states
         actionObjects: list of all objetcs of actions
         traversalMethod: how we traverse the planning graph, for now only BFS is supported
   '''
   # Setting Fringe Parameters
   fringe.setTraversalMethod(traversalMethod)
   fringe.initFringe()
   # Fringe initialization
   fringe.insert([initialStates, []])
   visited = set([tuple(initialStates)])
   plans = []
   while(not fringe.isEmpty()):
      # Each fringe element has this shape [stateSet, actionSequence]
      pathInfo = fringe.pop()
      stateSet = pathInfo[0]
      actionSequence = pathInfo[1]
      for act in actionObjects:
         # if action is applicable
         if applicable(stateSet, act.preconditions):
               # Apply the function
               newStateSet = apply(act.preconditions, act.finalState, stateSet)
               newActionSequence = actionSequence.copy()

               if isGoalAchieved(newStateSet, finalStates):
                  newActionSequence.append(act)
                  plans.append(newActionSequence)
               else:
                  newActionSequence.append(act)
                  fringe.insert([newStateSet,newActionSequence ])
                  visited.add(tuple(newStateSet))
   return plans

def backwardPlanning(initialStates, finalStates, actionObjects, traversalMethod):
   '''
   This function, similar to the forward version, provides the algorithm to backtrack
   all the way to the initial state.
   '''
   # Setting Fringe Parameters
   fringe.setTraversalMethod(traversalMethod)
   fringe.initFringe()
   # Planning Part:
   fringe.insert([finalStates, []])
   visited = set([tuple(finalStates)])
   plans = []
   while(not fringe.isEmpty()):
      pathInfo = fringe.pop()
      stateSet = pathInfo[0]
      actionSequence = pathInfo[1]
      for act in actionObjects:
         if applicableBackward(stateSet, act.finalState):
               newStateSet = applyBackward(act.preconditions, act.finalState, stateSet)
               newActionSequence = actionSequence.copy()
               if isGoalAchievedBackward(newStateSet, initialStates):
                  newActionSequence.append(act)
                  # plans.append(newActionSequence)
                  plans.append(plan.Plan(actionSequence=newActionSequence))
               else:
                  newActionSequence.append(act)
                  fringe.insert([newStateSet,newActionSequence ])
                  visited.add(tuple(newStateSet))
   return plans

def visualizePlans(plans):
   for plan in plans:
      plan.getPlanVisualization()

def printPlans(sortedPlans):
   print(f"Total number of plans: {len(sortedPlans)}")
   for plan in sortedPlans:
      print(plan)
      print("-"*20)


def visualizeSchedules(plans):
   for plan in plans:
      plan.getScheduleVisualization()


def printSchedules(plans):
   print(f"Total number of scheduled plans: {len(plans)}")
   for plan in plans:
      plan.schedulePrinting()
      print("-"*20)

def sortPlans(plans, optCriteria):
   # sortedPlans = sorted(plans, key=lambda plan: sum(action.getObjectives()[optCriteria] for action in plan))
   sortedPlans = sorted(plans, key=lambda plan: plan.computePlanValue(optCriteria))   
   # criteria_values = [plan.getPlanValue(optCriteria) for plan in sortedPlans]
   return sortedPlans

def pruneScheduledPlans(plans):
   repeatedPlans = set()
   for i in range(len(plans)):
      for j in range(i+1, len(plans)):
         if plans[i] == plans[j]:
               repeatedPlans.add(plans[j].planId)
   prunedPlans = []
   for plan in plans:
      if plan.planId not in repeatedPlans:
         prunedPlans.append(plan)
   return prunedPlans
      

   


#-----------------------------------------------------------------


if __name__ == '__main__':
   example_number = 10
   producerObjects, stateObjects, actionObjects, optCriteria = jsonReader(f"./jsonFiles/pddlExchangeExample{example_number}.json")
   initialStates, finalStates = get_Init_Final_States(stateObjects)
   # forwardPlanning(initialStates, finalStates, actionObjects, "BFS")
   plans = backwardPlanning(initialStates, finalStates, actionObjects, "BFS")
   sortedPlans = sortPlans(plans, optCriteria)
   printPlans(sortedPlans)
   # VisualizePlans(sortedPlans)
   
   for planObj in sortedPlans:
      planObj.schedule()

   prunedPlans = pruneScheduledPlans(sortedPlans)
   printSchedules(prunedPlans)
   visualizeSchedules(prunedPlans)
   outputFileName = f"./outputs/pddlExchangeExample{example_number}Solution.json"
   writeToJson(prunedPlans, outputFileName)
   # postprocess.postprocess(sortedPlans)


   
