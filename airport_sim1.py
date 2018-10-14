import numpy as np
import pandas as pd
from queue import PriorityQueue
from flight import Flight
from airport import Airport
from random import random
import datetime as dt
import math

GRAPH = True
compList = []
# global data structures
flightsInAir = PriorityQueue()
delayedQueue = PriorityQueue() # highest to lowest priority
airportList = {}
availableSlots = {}
delayedList = []
canceledList = []
# parameters
TEMP = 1000
TEMP_DECAY = 0.98
LEARN_RATE = 0.01
LEARN_DECAY = 0.98
MAX_ROUNDS = 100
K = 1

def setup():
    global airportList
    airportList["Llyne"] = Airport("Llyne", 2)
    airportList["Tenby"] = Airport("Tenby", 2)
    airportList["Hythe"] = Airport("Hythe", 2)
    airportList["Pontheugh"] = Airport("Pontheugh", 6)
    airportList["Alderdyfi"] = Airport("Alderdyfi", 6)
    airportList["Stathmore"] = Airport("Stathmore", 6)
    airportList["Orilon"] = Airport("Orilon", 2)
    airportList["Hwen"] = Airport("Hwen", 2)
    airportList["Ecrin"] = Airport("Ecrin", 2)
    airportList["Erith"] = Airport("Erith", 2)

def calcTotalCompensation():
    comp = 0
    for flight in delayedList:
        if flight.wait <= 2:
            comp += flight.passngrs*100
        elif 2 < flight.wait <= 4:
            comp += flight.passngrs*200
        elif 4 < flight.wait <= 6:
            comp += flight.passngrs*300
        elif 6 < flight.wait <= 8:
            comp += flight.passngrs*400
        else:
            comp += flight.passngrs*600
    for flight in canceledList:
        comp += flight.passngrs*600
        print(comp)
    return comp

def checkAvailableSlots(time):
    global airportList, availableSlots
    for airport in airportList.keys():
        if not airportList[airport].full():
            if time not in availableSlots:
                availableSlots[time] = {}
            availableSlots[time][airport] = airportList[airport].slotsAvail

def runSim():
    global delayedList, flightsInAir, airportList, availableSlots, delayedQueue, canceledList
    oneDSched = pd.read_excel("FlightSchedule.xlsx", "One Day Schedule").values # convert dataframe to np array
    setup()
    time = None
    firstRound = True
    depList = []
    countPontheugh = 0

    # iterate through the one-day flight schedule
    for flight in oneDSched:
        replacedFlight = False
        depTime = flight[3]
        dep, arr = flight[1].strip(), flight[2].strip()
        flight = Flight(flight[0].strip(), dep, arr, flight[3], flight[4], flight[6], [random() < 0.5 for i in range(6)])

        if not time or depTime > time:
            if time:
                if countPontheugh < 6:
                    while countPontheugh < 6 and not delayedQueue.empty():
                        priority, flight = delayedQueue.get()
                        replacedFlight = True
                        added = airportList["Pontheugh"].addActivePlane()
                        min = dt.date.min
                        waitTime = (dt.datetime.combine(min, time) - dt.datetime.combine(min, flight.depTime)).total_seconds()/3600
                        if waitTime < 0:
                            flight.wait = waitTime + 24
                        else:
                            flight.wait = waitTime
                        flight.arrTime = calcArrivalTime(time, flight)
                        flight.depTime = time
                        countPontheugh += 1
                checkAvailableSlots(time)
            countPontheugh = 0
            time = depTime # update current time
            # planes in departure list take off
            for depFlight in depList:
                flightsInAir.put((depFlight.arrTime, depFlight))
            depList = []
            # reset slots available for new time
            for airport in airportList.keys():
                airportList[airport].clearSlotsAvail()
            # add in the new plane 'flight' to the departure list
            depList.append(flight)
            if not airportList[flight.dep].addActivePlane(): # if airport has enough room
                if dep == "Pontheugh":
                    canceledList.append(flight)
            # check if flight arrival time equals now
            while not flightsInAir.empty() and flightsInAir.queue[0][0] == time:
                arrTime, arriving = flightsInAir.get() # get next arriving flight
                # pop unnecessary duplicates off queue
                if not airportList[arriving.arr].addActivePlane(): # if airport has enough room
                    if dep == "Pontheugh":
                        canceledList.append(flight)
        else:
            depList.append(flight)
            if dep == "Pontheugh":
                countPontheugh += 1
            depAirport = airportList[flight.dep]
            if not airportList[flight.dep].addActivePlane(): # if airport has enough room
                if dep == "Pontheugh":
                    canceledList.append(flight)

    # flights have been processed, but many still remain on flightsInAir and need to land
    while not flightsInAir.empty():
        depTime = flightsInAir.queue[0][0]
        if depTime > time:
            checkAvailableSlots(time)
            time = depTime
            # reset slots available for new time
            for airport in airportList.keys():
                airportList[airport].clearSlotsAvail()
            while not flightsInAir.empty() and flightsInAir.queue[0][0] == time:
                arrTime, arriving = flightsInAir.get()
                if not airportList[arriving.arr].addActivePlane(): # if airport has enough room
                    if dep == "Pontheugh":
                        canceledList.append(flight)
    checkAvailableSlots(time)

def calcArrivalTime(time, flight):
    depTime, arrTime = flight.depTime, flight.arrTime
    min = dt.date.min
    flightLen = dt.datetime.combine(min, arrTime) - dt.datetime.combine(min, depTime)
    arrivalDateTime = dt.datetime.combine(min, time) + flightLen
    return arrivalDateTime.time()

"""
Greedy: put flight in earliest possible spot
return values:
- True: successfully put delayed flight
- False: could not put a delayed flight, cannot fit flight into the day
"""
def putDelayedFlight(flight):
    global availableSlots
    for time in availableSlots.keys():
        arrivalTime = calcArrivalTime(time, flight)
        if arrivalTime < time:
            return False
        # all airports may be full so we must check if available slots exist for the times
        if (arrivalTime in availableSlots and
            flight.dep in availableSlots[time]
            and flight.arr in availableSlots[arrivalTime]
            and availableSlots[time][flight.dep] > 0
            and availableSlots[arrivalTime][flight.arr] > 0):
            availableSlots[time][flight.dep] -= 1
            availableSlots[arrivalTime][flight.arr] -= 1
            # wait time influences priority later
            min = dt.date.min
            flight.wait = (dt.datetime.combine(min, time) - dt.datetime.combine(min, flight.depTime)).total_seconds()/3600
            return True
    return False

def findSequence():
    global LEARN_RATE, TEMP, delayedList, delayedQueue, canceledList
    comp = float('inf')
    lastIter = [random() < 0.5 for i in range(6)] # True: increase, False: decrease
    flightsDelayed = pd.read_excel("FlightSchedule.xlsx", "Flights Delayed").values
    pontheughDelay = flightsDelayed[np.where(flightsDelayed[:, 1] == "Pontheugh ")] # select only pontheugh instances
    for flight in pontheughDelay:
        dep, arr = flight[1].strip(), flight[2].strip()
        depTime, arrTime = flight[3], flight[4]
        flight = Flight(flight[0], dep, arr, depTime, arrTime, flight[6], [random() for i in range(6)])
        delayedQueue.put((-flight.priority(), flight))
        delayedList.append(flight)
    for i in range(MAX_ROUNDS):
        canceledList = []
        runSim()
        for flight in delayedList:
            for j in range(5):
                if lastIter[j] or (flight.params[j] - LEARN_RATE < 0):
                    flight.params[j] = (flight.params[j] + LEARN_RATE)
                else:
                    flight.params[j] =  (flight.params[j] - LEARN_RATE)
        newComp = calcTotalCompensation()
        if newComp < comp:
            comp = newComp
            print()
            delayedList.sort(key=lambda e: e.depTime)
            for flight in delayedList:
                print(flight.depTime, flight.flightNum)
            print(calcTotalCompensation())
        else:
            if random() < math.exp(-K*(newComp - comp)/TEMP):
                if lastIter[j] or (flight.params[j] - LEARN_RATE < 0):
                    flight.params[j] = (flight.params[j] + LEARN_RATE)
                else:
                    flight.params[j] =  (flight.params[j] - LEARN_RATE)
                comp = newComp
            else:
                if not lastIter[j] or (flight.params[j] - LEARN_RATE < 0):
                    flight.params[j] =  (flight.params[j] + LEARN_RATE)
                else:
                    flight.params[j] = (flight.params[j] - LEARN_RATE)
                comp = newComp
        if GRAPH:
            compList.append(comp)
        LEARN_RATE *= LEARN_DECAY
        TEMP *= TEMP_DECAY

        # reset all data but the flight's parameters
        newDelayedList = []
        for i in range(len(pontheughDelay)):
            flight = pontheughDelay[i]
            dep, arr = flight[1].strip(), flight[2].strip()
            depTime, arrTime = flight[3], flight[4]
            flight = Flight(flight[0], dep, arr, depTime, arrTime, flight[6], delayedList[i].params)
            flight.wait = delayedList[i].wait
            delayedQueue.put((-flight.priority(), flight))
            newDelayedList.append(flight)
        delayedList = newDelayedList

if __name__ == "__main__":
    findSequence()
