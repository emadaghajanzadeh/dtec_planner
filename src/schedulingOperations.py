
def visualizeSchedules(plans):
   for plan in plans:
      plan.getScheduleVisualization()

def printSchedules(plans):
   print(f"Total number of scheduled plans: {len(plans)}")
   for plan in plans:
      plan.schedulePrinting()
      print("-"*20)

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
      

   