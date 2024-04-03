import json
import producer, state, action

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

def writeToJson(sortedPlans, outputFileName, optCriteria):
   """Writing the output into the Json file."""
   if len(sortedPlans) == 0:
      data = {"optimizeFor": optCriteria, "minimumPlan": "-", "maximumPlan":"-",
              "Number of Plans":0}
   else:
      data = {"optimizeFor": optCriteria, "minimumPlan":sortedPlans[0].getPlanValue(), "minimumPlan":sortedPlans[-1].getPlanValue()}
      data["numberOfPlans"] = len(sortedPlans)
      plans_list = [] # list of dictionaries (plans)
      for plan in sortedPlans:
         plans_list.append(plan.getDictInfo())
      data["plans"] = plans_list
   json_object = json.dumps(data, indent=4)
   with open(outputFileName, "w") as outfile:
      outfile.write(json_object)

