import numpy as np
import pandas as pd

def calcCompensation():
    return 0

def cost(flight):
    # cost stuff here

def main():
    flightsDelayed = pd.read_excel("FlightSchedule.xlsx", "Flights Delayed").values  # convert dataframe to np array
    oneDSched = pd.read_excel("FlightSchedule.xlsx", "One Day Schedule").values
    pontheughDelay = flightsDelayed[np.where(flightsDelayed[:, 1] == "Pontheugh ")] # select only pontheugh instances
    orderFlights(pontheughDelay)

def orderFlights(delayList, oneDSched):
    storedValues = np.full((len(delayList), len(oneDSched)), -1) # stores minimized costs of every situation
    soln = np.empty((len(delayList)))
    orderFlightsHelper(delayList, oneDSched, storedValues, soln, 0, 0)

def orderFlightsAux(delayList, oneDSched, storedValues, soln, i, j):
    if storedValues[i, j] >= 0:
        return storedValues[i, j]
    else if j == len(delayList):
        return 0

    minCost = float('inf')
    for i, flight in enumerate(delayList):
        delayCost = cost(flight) + orderFlightAux(np.delete(delayList, i), storedValues, soln, i, j+1)
        if delayCost < minCost:
            minCost = delayCost
    storedValues[i, j] = minCost
    return storedValues[i, j]

if __name__ == "__main__":
    main()
