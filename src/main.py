import jsonOperations, stateListOperations, plannerOperations, schedulingOperations
# source /Users/emadaghajanzadeh/Documents/Work/Dtec/planner/planner_venv/bin/activate

if __name__ == '__main__':
   example_number = 10
   producerObjects, stateObjects, actionObjects, optCriteria = jsonOperations.jsonReader(f"./jsonFiles/pddlExchangeExample{example_number}.json")
   initialStates, finalStates = stateListOperations.get_Init_Final_States(stateObjects)
   # plannerOperations.forwardPlanning(initialStates, finalStates, actionObjects, "BFS")
   plans = plannerOperations.backwardPlanning(initialStates, finalStates, actionObjects, "BFS")
   sortedPlans = plannerOperations.sortPlans(plans, optCriteria)
   plannerOperations.printPlans(sortedPlans)
   # VisualizePlans(sortedPlans)
   
   for planObj in sortedPlans:
      planObj.schedule()
   prunedPlans = schedulingOperations.pruneScheduledPlans(sortedPlans)
   schedulingOperations.printSchedules(prunedPlans)
   schedulingOperations.visualizeSchedules(prunedPlans)
   outputFileName = f"./outputs/pddlExchangeExample{example_number}Solution.json"
   jsonOperations.writeToJson(prunedPlans, outputFileName, optCriteria)


   
