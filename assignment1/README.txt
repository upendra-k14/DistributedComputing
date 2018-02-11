Assignment 1 : Distributed Computing

Files included :

1. 048-047-assign01-1.py : OddEven Sort
2. 048-047-assign01-2.py : Sasaski Algorithm
3. 048-047-assign01-3.py : Alternative Sorting Algorithm
4. chart.png
5. experiment : Contains sample arrays in pickle format

Requirements
------------

- python>=3.4

How to run ?
------------

1. 048-047-assign01-1.py : OddEven Sort
---------------------------------------

usage: python3 048-047-assign01-1.py [-h] [-v] [-n NPROCESS] [-o ORDER]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose mode
  -n NPROCESS, --nprocess NPROCESS
                        Number of processes n where n>=2
  -o ORDER, --order ORDER
                        0 for ascending order, 1 for descending order. Without
                        any argument ascending order is used


2. 048-047-assign01-2.py : Sasaski Algorithm
--------------------------------------------

usage: python3 048-047-assign01-2.py [-h] [-v] [-n NPROCESS] [-o ORDER]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose mode
  -n NPROCESS, --nprocess NPROCESS
                        Number of processes n where n>=2


3. 048-047-assign01-3.py : Alternative Sorting Algorithm
--------------------------------------------------------

usage: python3 048-047-assign01-3.py [-h] [-v] [-n NPROCESS] [-o ORDER]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose mode
  -n NPROCESS, --nprocess NPROCESS
                        Number of processes n where n>=2
  -o ORDER, --order ORDER
                        0 for ascending order, 1 for descending order. Without
                        any argument ascending order is used



Contribution :
--------------

Upendra Kumar - 201401048
-------------------------

1. Deciding the protocol for transfer of messages between processes with required flags
2. Implemented 048-047-assign01-1.py and 048-047-assign01-3.py

Tushar Maheshwari - 201401048
-------------------------

1. Implemented 048-047-assign01-2.py (Sasaski Algorithm)
2. Created experimental dataset : ./experiment/Sample and chart.png to measure time elpased for different algorithms.




