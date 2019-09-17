##E.Cloudmesh.Shell.1,2,3
# E.Cloudmesh.Shell.1 - Installed cmd5 and command cms.

from cloudmesh.common.Shell import Shell

# E.Cloudmesh.Shell.2 - New command with firstname as command name.
## cloudmesh-pratibha directory has been uploaded:
##https://github.com/cloudmesh-community/fa19-516-152/tree/master/cloudmesh-exercises/cloudmesh-pratibha

shell2_result = Shell.execute('cms', 'pratibha --text HelloWorld')
print(shell2_result)

# E.Cloudmesh.Shell.3 - New command with firstname as command name.
## cloudmesh-shell3 directory has been uploaded:
## https://github.com/cloudmesh-community/fa19-516-152/tree/master/cloudmesh-exercises/cloudmesh-shell3

shell3_result = Shell.execute('cms', 'shell3 --text abcd')
print(shell3_result)

shell3_result1 = Shell.execute('cms', 'shell3 --number 45')
print(shell3_result1)

shell3_result2 = Shell.execute('cms', 'shell3 list')
print(shell3_result2)
