import requests, sys



data = {'domain': open("pddlDomainExample1.pddl", 'r').read(),
        'problem': open("pddlProblemExample1.pddl", 'r').read()}


resp = requests.post('http://solver.planning.domains/solve',
                     verify=False, json=data).json()

print(resp)
# with open(sys.argv[3], 'w') as f:
    # f.write('\n'.join([act['name'] for act in resp['result']['plan']]))