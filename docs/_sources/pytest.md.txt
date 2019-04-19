# Pytest

Pytest is a utility to unit test python code. 

We use nosetests and not `__main__` to test all functionality so they can me
automatically run and reports can be generated. A project that does not have a
sufficient number of tests to make sure the module works can not be accepted.

## Installation

The nose module can be installed with the help of pip utility

```python
$ pip install pytest
```

This will install the pytest module in the current Python distribution, which
means the test can be run using this utility as well as using `–m` switch. All
tests are included in the folder `tests`.

For example for the cloudmesh-cloud module they are in 

* <https://github.com/cloudmesh/cloudmesh-cloud/tree/master/tests>

Best is to add a numbe rto identify in which order they are run

```
+cm
  + cloudmesh
  + tests
    - test_01_topic1.py
    - test_02_topic2.py
    - test_03_topic2.py
```


## Test Specification and Execution

A simple example for a test is 

* <https://github.com/cloudmesh/cloudmesh-cloud/blob/master/tests/test_key.py>

Note that all test python programs have specific function names 
of the form

`def test_number_topic (self)`

The number is defined to order them and is typically something like `001`, note
the leading spaces. The topic is a descriptive term on what we test.

Each test starts with a setup function `def setup(self)` we declare a setup that
is run prior to each test being executed. Other functions will use the setup
prior to execution.

A function includes one or multiple asserts that check if a particular test
succeeds and reports this to nose to expose the information if a tess succeds or
fails, when running it

Note that all nosetest functions start with a `HEADING()` in the body which conveniently
prints a banner with the function name and thus helps in debugging in case of
errors.


Invocation is simply done with the comment lines you see on top that you will include.

in our case the test is called test_key.py so we include on the top

```
###############################################################
# pytest -v --capture=no tests/test_key.py
# pytest -v  tests/test_key.py
# pytest -v --capture=no -v --nocapture tests/test_key.py:Test_key.<METHIDNAME>
###############################################################
```

You can than execute the test with either command. More information is printed
with the command

Make sure that you place this comment in your tests.

The following is our simple nosetests for key. THe file is stored at 
`tests/test_key.py`

First, we import the needed classes and methods we like to test. 
We define a class, and than we define the methods. such as the setup and the actual tests.

your run it with 

```bash
$ pytest -v --capture=no tests/test_key.py
```

```python
###############################################################
# pytest -v --capture=no tests/test_key.py
# pytest -v  tests/test_key.py
# pytest -v --capture=no -v --nocapture tests/test_key.py:Test_key.<METHIDNAME>
###############################################################
from pprint import pprint
from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import HEADING
from cloudmesh.management.configuration.SSHkey import SSHkey
from cloudmesh.management.configuration.config import Config

@pytest.mark.incremental
class TestKey:

    def setup(self):
        self.sshkey = SSHkey()


    def test_01_key(self):
        HEADING()
        pprint(self.sshkey)
        print(self.sshkey)
        print(type(self.sshkey))
        pprint(self.sshkey.__dict__)

        assert self.sshkey.__dict__  is not None


    def test_02_git(self):
        HEADING()
        config = Config()
        username = config["cloudmesh.profile.github"]
        print ("Username:", username)
        keys = self.sshkey.get_from_git(username)
        pprint (keys)
        print(Printer.flatwrite(keys,
                            sort_keys=("name"),
                            order=["name", "fingerprint"],
                            header=["Name", "Fingerprint"])
              )

        assert len(keys) > 0

```

The output with `pytest tests/test_key.py` does not provide any detail,
but just reports if tests fail or succeed.

```
----------------------------------------------------------------------
Ran 2 tests in 0.457s

OK
```

The output with  `nosetests -v tests/test_key.py`

results in 

```
tests.test_key.TestName.test_01_key ... ok
tests.test_key.TestName.test_02_git ... ok

----------------------------------------------------------------------
Ran 2 tests in 1.072s

OK
```

During development phase you want to use `nosetests -v --nocapture tests/test_key.py`

WHich prints all print statements also
