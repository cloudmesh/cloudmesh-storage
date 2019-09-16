##E.Cloudmesh.Common.5

from cloudmesh.common.StopWatch import StopWatch
import time

StopWatch.start("demoStopWatch")
print("StopWatch Started..")

for i in range(1, 10):
   i+=1
   time.sleep(1)

StopWatch.stop("demoStopWatch")
print("StopWatch Stopped..")
print ("Time taken: " + str(StopWatch.get("demoStopWatch")) +" seconds")