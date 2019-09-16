# E.Cloudmesh.Common.3

# Demostrate use of Flatdict

from cloudmesh.common.FlatDict import FlatDict

flatDictData = {
    "name": "Pratibha", "topic": "Cloudmesh API",
    "assignment": {"assignmentNumber": "Common.3", "assignmentTopic": "FlatDict Demo"}
}

flatDictData = FlatDict(flatDictData, ".")

print(flatDictData)
