from random import random
from functools import reduce

INTERNATIONAL = ["Pontheugh", "Alderdyfi", "Stathmore"]

class Flight:
    """
    params:
    - wait: current waiting time of plane
    - passngrs: number of passengers on plane
    - remain: remaining time before plane must departure (for roundtrips)
    - intrntl: if flight is international
    - dep: location of departure
    - arr: location of arrival
    """
    def __init__(self, flightNum, dep, arr, depTime, arrTime, passngrs):
        self.flightNum = flightNum
        self.passngrs = passngrs
        self.intrntl = dep != arr and dep in INTERNATIONAL and arr in INTERNATIONAL
        self.depTime = depTime
        self.arrTime = arrTime
        self.dep = dep
        self.arr = arr
        self.wait = 0 # in hours
        self.route = 0
        self.remain = 6 # default, unused value
        self.params = [random() for i in range(5)]

    def __iter__(self):
        return iter([self.wait, self.passngrs, self.remain, int(self.intrntl), self.route])

    # compute weighted sum of the properties to get priority, where the weights are from self.params
    def priority(self):
        return reduce(lambda x, y: x + y[0]*y[1], zip(self.__iter__(), self.params), 0)

    def __str__(self):
        return self.flightNum

    def __lt__(self, other):
        return self.priority() < other.priority()

    def __gt__(self, other):
        return self.priority() > other.priority()

    def __eq__(self, other):
        return self.flightNum == other.flightNum
