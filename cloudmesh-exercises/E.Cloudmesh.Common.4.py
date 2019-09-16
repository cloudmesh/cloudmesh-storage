#E.Cloudmesh.Common.4

#Demostrate Shell - Used Win10 commands.

from cloudmesh.common.Shell import Shell

result = Shell.execute('echo',"Testing Shell")
print(result)

result = Shell.execute('dir')
print(result)

result = Shell.execute('ping',"github.com")
print(result)