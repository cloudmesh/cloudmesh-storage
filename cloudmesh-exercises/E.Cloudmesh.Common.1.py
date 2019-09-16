# E.Cloudmesh.Common.1

## Develop a program that demonstartes the use of banner, HEADING, and VERBOSE.

from cloudmesh.common.util import banner
from cloudmesh.common.util import HEADING
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.variables import Variables

## Defining variables

headingText = "Pratibha - E.Cloudmesh.Common.1 HEADING"
bannerText = "Pratibha - E.Cloudmesh.Common.1 banner"
verboseData = {"Name": "Pratibha", "Assigment": "Cloudmesh.Common.1"}
verboseData1 = {"headingText": headingText, "bannerText": bannerText}

variables = Variables()
variables['debug'] = True
variables['verbose'] = 10


class cloudmeshCommon1():

    def demo1(self, text1, text2):
        ##Demostrate use of banner
        banner(text1, "*", color="BLUE")

        ##Demostrate use of HEADING
        HEADING(text2, "+")

        ##Demostrate use of VERBOSE
        VERBOSE(verboseData1, "Verbose Debug Data", "GREEN")


cloudmeshCommon1.demo1(object, headingText, bannerText)
