import json
import producer, state, action
import fringe
# source /Users/emadaghajanzadeh/Documents/Work/Dtec/planner/planner_venv/bin/activate      
# Notes
# 1- Are there nagative pre-conditions in the project?
# 2- Do we consume pre-conditions after the action is done?
# 3- What is the difference between initial and precondition states?
# 4- how deliveryTimeLatestInWeeks is related to processingTimeInWeeks and workingTimeInHours? I think both of the later variables are somehow dependent to the former one?
# 5- Should we also consider special scenarios wherein initial and final states are not determined, or it is ensured we are given them correctly.
# Please refer to the knowledge base for further questions.
# 6- In Backward planning, removing precondition after oing an action is not considered but I think that is not problematic asince we only deal with trees.

def jsonReader(jsonFilename):
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


#--------------State-related functions---------------------------
def get_Init_Final_States(stateList):
   initialStates = set()
   finalStates = set()
   for state in stateList:
      if state.isStartState:
            initialStates.add(state)
      if state.isFinalState:
            finalStates.add(state)
   return initialStates, finalStates

def isStatePresent(stateList, stateID):
   '''
   Checks if a specific state is already present in a given state list.
   '''
   for state in stateList:
      if state.id == stateID:
         return True
   return   False

def isGoalAchieved(StateList, finalStates):
   if finalStates.issubset(StateList):
      return True
   return False

def isGoalAchievedBackward(StateList, initialStates):
   if StateList.issubset(initialStates): return True
   return False

#-----------------------------------------------------------------



#--------------Action-related functions---------------------------
def applicable(stateSet, actionPrecon):
   precons = set([x["state_object"] for x in actionPrecon])
   if precons.issubset(stateSet):
      return True
   return False

def apply(actionPrecon, actionEffect, currentStateSet):
   # Currently, actions have only the id of the state, so we need all state to find the intended one, but with linkning state objects it will more performant.
   # tasks: 
      # add new final state - remove used preconditinos - search over stateObjects to find state objects
   precons = set([x["state_object"] for x in actionPrecon])
   newStateSet = currentStateSet.difference(precons)
   newStateSet.add(actionEffect)
   return newStateSet

def applicableBackward(stateSet, actionEffect):
   actioEffectSet = set()
   actioEffectSet.add(actionEffect)
   if actioEffectSet.issubset(stateSet):
      return True
   return False

def applyBackward(actionPrecon, actionEffect, currentStateSet):
   actioEffectSet = set()
   actioEffectSet.add(actionEffect)
   
   newStateSet = currentStateSet.difference(actioEffectSet)

   for precon in actionPrecon:
      newStateSet.add(precon["state_object"])
   return newStateSet
#-----------------------------------------------------------------

def forwardPlanning(initialStates, finalStates, actionObjects, traversalMethod):

   # Setting Fringe Parameters
   fringe.setTraversalMethod(traversalMethod)
   fringe.initFringe()
   # Planning Part:
   fringe.insert([initialStates, []])
   visited = set([tuple(initialStates)])
   plans = []
   while(not fringe.isEmpty()):
      pathInfo = fringe.pop()
      stateSet = pathInfo[0]
      actionSequence = pathInfo[1]
      print(f"Poped: {stateSet} - {actionSequence}")
      for act in actionObjects:
         if applicable(stateSet, act.preconditions):
               newStateSet = apply(act.preconditions, act.finalState, stateSet)
               newActionSequence = actionSequence.copy()
               # if tuple(newStateSet) not in visited:
               if isGoalAchieved(newStateSet, finalStates):
                  newActionSequence.append(act)
                  plans.append(newActionSequence)
                  print(f"One plan Found! {newActionSequence}")
               else:
                  newActionSequence.append(act)
                  fringe.insert([newStateSet,newActionSequence ])
                  print(newStateSet)
                  visited.add(tuple(newStateSet))
      print("---")
   print(f"{len(plans)} Plans Found!")
   for plan in plans:
      for act in plan:
         print(f"Action ID: {act.id}")
      print("################")

def backwardPlanning(initialStates, finalStates, actionObjects, traversalMethod):
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
      # print(f"Poped: {stateSet} - {actionSequence}")
      for act in actionObjects:
         if applicableBackward(stateSet, act.finalState):
               newStateSet = applyBackward(act.preconditions, act.finalState, stateSet)
               newActionSequence = actionSequence.copy()
               # if tuple(newStateSet) not in visited:
               if isGoalAchievedBackward(newStateSet, initialStates):
                  newActionSequence.append(act)
                  plans.append(newActionSequence)
                  # print(f"One plan Found! {newActionSequence}")
               else:
                  newActionSequence.append(act)
                  fringe.insert([newStateSet,newActionSequence ])
                  # print(newStateSet)
                  visited.add(tuple(newStateSet))
      # print("---")
   return plans

def printPlan(plan):
   print("Sequence of actions: ")
   for action in plan[:-1]:
      print(f"{action}", end=" => ")
   print(plan[-1])


def sortPlans(plans, actionObjects, optCriteria):
   sortedPlans = sorted(plans, key=lambda plan: sum(action.getObjectives()[optCriteria] for action in plan))
   criteria_values = [sum(action.getObjectives()[optCriteria] for action in plan) for plan in sortedPlans]
   print(criteria_values)
   for plan,criteria_value in zip(plans,criteria_values) :
      printPlan(plan)
      print(criteria_value)
   return sortedPlans

      


if __name__ == '__main__':
   # load the JSON file
   producerObjects, stateObjects, actionObjects, optCriteria = jsonReader("./JsonFiles/pddlExchangeExample7.json")
   initialStates, finalStates = get_Init_Final_States(stateObjects)
   # forwardPlanning(initialStates, finalStates, actionObjects, "BFS")
   plans = backwardPlanning(initialStates, finalStates, actionObjects, "BFS")
   sortedPlans = sortPlans(plans, actionObjects, optCriteria)


   
