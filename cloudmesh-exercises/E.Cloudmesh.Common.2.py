#E.Cloudmesh.Common.2
#Demostrate usage of dotdict
from cloudmesh.common.dotdict import dotdict

dictValues = {"name": "Pratibha", "topic": "Cloudmesh API", "assignment": "E.Cloudmesh.Common.2"}

dictValues = dotdict(dictValues)

print(dictValues.name + "\n" + dictValues.topic + "\n" + dictValues.assignment)
