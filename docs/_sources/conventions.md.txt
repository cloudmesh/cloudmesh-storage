# Code Conventions


* Python lint: All code must be formatted with the pyCHarm inspect method which
  will suggest a reformat with pyCharm and allows good error and python issue
  detection. Please fix as many as you can.

* Printing errors: 

  In case you need to print errors please do not use print, but use

  ```python
  from cloudmesh.common.console import Console

  Console.error("this is an example")
  ```

* Printing debug messages in verbose mode 

  In case yo ulike to do debug messages use

  ````python
  from cloudmesh.DEBUG import VERBOSE

  VERBOSE("this is an example")  
  ```

* Managing debug and verbose mode
 
  Verbosity and debugging can be controlled with 
  
  ```python
  cms set verbose=10
  cms set debug=True
  cms set trace=True
  ```

  anything that is smaller than 10will be printed.
