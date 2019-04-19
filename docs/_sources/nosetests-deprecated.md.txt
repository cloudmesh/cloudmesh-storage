
## Timed decorator

In some cases you may want to use a timed decorator that limits the time a test
is executed for. An example is given next:

```python
############################################
# nosetest -v --nocapture 
# nosetests tests/test_timed.py
# nosetests -v --nocapture tests/test_timed.py
############################################

class TestTimed:

    @timed(1.0)
    def test_10_sleep_which_fails():
        time.sleep(2.0)
```

## Test Setup

The setup in a class can be controlled by the following functions. We include in
the print statement when they are called:

```python
   def setup(self):
        print ("setup() is called before each test method")
 
    def teardown(self):
        print ("teardown() is called after each test method")
 
    @classmethod
    def setup_class(cls):
        print ("setup_class()is called before any methods in this class")
 
    @classmethod
    def teardown_class(cls):
        print ("teardown_class() is called after any methods in this class")
```

## Test Timer

The following extension adds timers to nosetests

* <https://github.com/mahmoudimus/nose-timer>

It is installed with 

```bash
$ pip install nose-timer
```

It is started with the flag `--with-timer`

Thus, 

```bash
$ nosetests -v --nocapture --with-timer tests/test_key.py
```

Will print the time for each test as shown in this partial output:

```
...
[success] 58.61% tests.test_key.TestName.test_02_git: 0.1957s
[success] 41.39% tests.test_key.TestName.test_01_key: 0.1382s
----------------------------------------------------------------------
Ran 2 tests in 0.334s
```

## Doctests in Cloudmesh

Out of principal we will not create an test running doctests.


## Sniffer (not tested)

often we make changes frequently and like to get an imediate feedback on the
changes made. For the automatic repeated execution on change we can use the tool
`sniffer`.

```bash
$ sniffer -x--with-spec -x--spec-color
```

This will execute the nosetests upon change. To specify a specific test you can
pass along the name of the python test.

To install it use

```bash
$ pip install sniffer
```

The manual page can be called with 

```bash
$ sniffer --help
```

## Profiling

Nosetest can be augmented with profiles that showcase some of the internal time
spend on different functions and methods. To do so install 

* <https://github.com/msherry/nose-cprof>

```bash
$ pip install nose-cprof
$ pip install cprofilev
$ pip install snakeviz
$ pip install profiling
```

Then call the nosetest with the additional option 

```bash
$ nosetests --with-cprofile
```

The output will be stored by default in `stats.dat`

To view it use cprofilev

```bash
$ cprofilev -f stats.dat
```

To view it with snakeviz use 

```bash
$ snakeviz -f stats.dat
```


To visualize the call graph we use pygraphviz. Unfortunatley it has an error and only produces png files.
Thus we use a modified version and instal it from source:

```bash
cd /tmp
$ git clone git@github.com:laszewsk/pycallgraph.git
$ cd pycallgraph
$ pip install .
```

Next we go to the cm directory and can creat a call graph from a python program
and open the output

```bash
$ pycallgraph graphviz -- tests/test_key.py 
$ open pycallgraph.pdf 
```

Another very usefule module is `profiling` which can be invoked with

```bash
$ profiling tests/test_key.py
```


To do live profiling you can use

```bash
$ profiling live-profile tests/test_key.py
```

