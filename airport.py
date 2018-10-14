from flight import Flight

class Airport:
    def __init__(self, name, numSlots):
        self.name = name
        self.numSlots = numSlots
        self.slotsAvail = numSlots

    def empty(self):
        return self.slotsAvail >= self.numSlots

    def full(self):
        return self.slotsAvail <= 0

    # return value: successfully added active plane to an airport arrival slot
    def addActivePlane(self):
        hasRoom = not self.full()
        if hasRoom:
            self.slotsAvail -= 1
        return hasRoom

    def clearSlotsAvail(self):
        self.slotsAvail = self.numSlots
