import plan, fringe
import stateListOperations

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

def isMaximumCostExceeded(actionSeq, newAction, max_cost):
   '''
   This function checks if the cost of a plan is exceeded the maximum cost.
   '''
   current_cost = sum(action.getObjectives()["cost"] for action in actionSeq)
   current_cost += newAction.getObjectives()["cost"]
   if max_cost != -1 and current_cost > max_cost:
      return True
   return False

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

               if stateListOperations.isGoalAchieved(newStateSet, finalStates):
                  newActionSequence.append(act)
                  plans.append(newActionSequence)
               else:
                  newActionSequence.append(act)
                  fringe.insert([newStateSet,newActionSequence ])
                  visited.add(tuple(newStateSet))
   return plans

def backwardPlanning(initialStates, finalStates, actionObjects, traversalMethod, max_cost=-1):
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
         if applicableBackward(stateSet, act.finalState) and (not isMaximumCostExceeded(actionSequence, act, max_cost)):
               newStateSet = applyBackward(act.preconditions, act.finalState, stateSet)
               newActionSequence = actionSequence.copy()
               if stateListOperations.isGoalAchievedBackward(newStateSet, initialStates):
                  newActionSequence.append(act)
                  # plans.append(newActionSequence)
                  plans.append(plan.Plan(actionSequence=newActionSequence))
                  print(plans[-1])
               else:
                  newActionSequence.append(act)
                  fringe.insert([newStateSet,newActionSequence ])
                  visited.add(tuple(newStateSet))
   return plans

def visualizePlans(plans, output_file_plans):
   for plan in plans:
      plan.getPlanVisualization(output_file_plans)

def printPlans(sortedPlans):
   print(f"Total number of plans: {len(sortedPlans)}")
   for plan in sortedPlans:
      print(plan)
      print("-"*20)

def sortPlans(plans, optCriteria):
   # sortedPlans = sorted(plans, key=lambda plan: sum(action.getObjectives()[optCriteria] for action in plan))
   sortedPlans = sorted(plans, key=lambda plan: plan.computePlanValue(optCriteria))   
   # criteria_values = [plan.getPlanValue(optCriteria) for plan in sortedPlans]
   return sortedPlans