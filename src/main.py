import os
import jsonOperations, stateListOperations, plannerOperations, schedulingOperations
import argparse
# source /Users/emadaghajanzadeh/Documents/Work/Dtec/planner/planner_venv/bin/activate


parser = argparse.ArgumentParser()
# General parameters
parser.add_argument("--input", type=str, required=True,
                    help="Address of the input file. It should be in the json format and in the inputs folder.")
parser.add_argument("--algo", type=str, required=False, default="BFS",
                    help="The algorithm to be used for planning. For now, only BFS is supported.")
parser.add_argument("--print", action="store_true", default=False,
                     help="Print the plans or not. If yes, it will print the plans.")
parser.add_argument("--visualize", action="store_true", default=False,
                    help="Visualize the plans or not. If yes, it will visualize the plans.")
parser.add_argument("--output", type=str, required=True,
                     help="The address to which the output file should be written.")
parser.add_argument("--max-cost", type=int, required=False, default=-1,
                     help="The maximum cost for searching the plans.")





if __name__ == '__main__':
   args = parser.parse_args()
   # Process the arguments
   input_file = args.input
   algo = args.algo
   printFlag = args.print
   visualizeFlag = args.visualize
   output_file = args.output
   max_cost = args.max_cost
   

   
   input_file = "./inputs/" + input_file
   # Create corresponding folders for the output files
   output_folder = "./outputs/" + output_file
   if not os.path.exists(output_folder):
      os.makedirs(output_folder)
   output_file_json = output_folder + f"/{output_file}.json"
   if visualizeFlag:
      output_file_plans = output_folder + "/plans"
      os.makedirs(output_file_plans)
      output_file_schedules = output_folder + "/schedules"
      os.makedirs(output_file_schedules)
   

   # Extract information from the input file
   producerObjects, stateObjects, actionObjects, optCriteria = jsonOperations.jsonReader(input_file)
   initialStates, finalStates = stateListOperations.get_Init_Final_States(stateObjects)
   # Perform the planning
   plans = plannerOperations.backwardPlanning(initialStates, finalStates, actionObjects, algo, max_cost)
   # Sort the plans based on the optimization criteria
   sortedPlans = plannerOperations.sortPlans(plans, optCriteria)
   # Print the plans
   if printFlag:
      plannerOperations.printPlans(sortedPlans)
   # Visualize the plans
   if visualizeFlag:
      plannerOperations.visualizePlans(sortedPlans, output_file_plans)
   # Perform the scheduling   
   for planObj in sortedPlans:
      planObj.schedule()
   # Pruining the schedules
   prunedPlans = schedulingOperations.pruneScheduledPlans(sortedPlans)
   # Print the schedules
   if printFlag:
      schedulingOperations.printSchedules(prunedPlans)
   # Visualize the schedules
   if visualizeFlag:
      schedulingOperations.visualizeSchedules(prunedPlans, output_file_schedules)
   # Write the schedules to a file
   jsonOperations.writeToJson(prunedPlans, output_file_json, optCriteria)

   