"""
    Author: Ayzalme
    Github: Tooya12
"""
import base64
import calendar
from datetime import datetime

class zalsTime():
    def __init__(self):
        """ Time stuff Variable """
        self.time = datetime.now()
        self.day = self.time.strftime("%A")
        self.date = self.time.strftime("%d")
        self.hour = self.time.strftime("%H")
        self.minute = self.time.strftime("%M")
        self.month = self.time.strftime("%B")
        self.year = self.time.strftime("%Y")

        """ Point Variable """
        self.hourPoint = 0
        self.dayPoint = 0
        self.monthPoint = 0
        self.yearPoint = 0

        """ List name Date and Month """
        self.listOfDay = list(calendar.day_name)
        self.listOfMonth = list(calendar.month_name)

    def update(self):
        """ Update all time stuff Variable """
        self.time = datetime.now()
        self.day = self.time.strftime("%A")
        self.date = self.time.strftime("%d")
        self.hour = self.time.strftime("%H")
        self.minute = self.time.strftime("%M")
        self.month = self.time.strftime("%B")
        self.year = self.time.strftime("%Y")
        self.hourPoint = 0
        self.dayPoint = 0
        self.monthPoint = 0
        self.yearPoint = 0

    def timeNow(self, encode=False):
        self.result = [self.day, self.hour + ":" + self.minute, self.date, self.month, self.year]
        self.result = " ".join(self.result)
        self.update()

        if (encode):
            self.resultEncoded = base64.b64encode(bytes(self.result, "utf-8")).decode()

            return self.resultEncoded

        return self.result

    def timeIncrease(self, incMinute=None, incHour=None, incDay=None, incMonth=None, incYear=None, encode=False):

        """ Dynamic Increasing Time """
        def increasingTime(current, increase, maximum):
            timePlus = int(current) + increase
            point = 0

            if (timePlus == maximum):
                point += 1
                current = "00"

            if (timePlus > maximum):
                while True:
                    timePlus -= maximum

                    if (timePlus < maximum):
                        current = str(timePlus)
                        point += 1
                        break

                    point += 1
            else:
                if (timePlus == maximum):
                    pass

                else:
                    current = str(timePlus)

            if (len(current) == 1):
                current = "0" + current

            return current, point

        """ Dynamic Day Increase """
        def increasingDay(current, increase):
            monthIndex = self.listOfMonth.index(str(self.month))
            maximum = calendar.monthrange(int(self.year), monthIndex)[1]
            dayPlus = int(current) + increase
            yearPlus = 0
            point = 0

            while True:
                if (dayPlus > maximum):
                    monthIndex += 1

                    if (monthIndex > 12):
                        yearPlus += 1
                        point += 1
                        monthIndex = 1

                        maximum = calendar.monthrange(int(self.year) + yearPlus, monthIndex)[1]
                        dayPlus -= maximum

                    else:
                        point += 1
                        monthIndex += 1

                        if (monthIndex > 12):
                            yearPlus += 1
                            monthIndex = 1
                            maximum = calendar.monthrange(int(self.year) + yearPlus, monthIndex)[1]
                            dayPlus -= maximum

                        else:
                            maximum = calendar.monthrange(int(self.year) + yearPlus, monthIndex)[1]
                            dayPlus -= maximum

                else:
                    current = str(dayPlus)
                    break

            return current, point

        """ Dynamic Increasing Month """
        def increasingMonth(current, increase):
            monthPlus = self.listOfMonth.index(current) + increase
            maximum = 12
            point = 0

            if (monthPlus > maximum):
                while True:
                    monthPlus -= maximum

                    if (monthPlus < maximum):
                        current = calendar.month_name[monthPlus]
                        point += 1
                        break

                    if (monthPlus == 12):
                        current = calendar.month_name[monthPlus]
                        point += 1
                        break

                    point += 1
            else:
                current = calendar.month_name[monthPlus]

            return current, point


        """ Check parameter of this Function """
        if (incMinute):
            if (not isinstance(incMinute, int)):
                raise ValueError("Hanya bisa memasukan bilangan integer!")

            self.minute, self.hourPoint = increasingTime(self.minute, incMinute, 60)

        if (incHour):
            if (not isinstance(incHour, int)):
                raise ValueError("Hanya bisa memasukan bilangan integer!")

            self.hour, self.dayPoint = increasingTime(self.hour, incHour, 24)

        if (incDay):
            if (not isinstance(incDay, int)):
                raise ValueError("Hanya bisa memasukan bilangan integer!")

            self.date, self.monthPoint = increasingDay(self.date, incDay)

        if (incMonth):
            if (not isinstance(incMonth, int)):
                raise ValueError("Hanya bisa memasukan bilangan integer!")

            self.month, self.yearPoint = increasingMonth(self.month, incMonth)

        if (incYear):
            if (not isinstance(incYear, int)):
                raise ValueError("Hanya bisa memasukan bilangan integer!")

            """ Simple way :) """
            self.year = str(int(self.year) + incYear)

        """ Check point of Hour, Day, Month, Year """
        if (self.hourPoint > 0):
            self.hour, self.anotherDay = increasingTime(self.hour, self.hourPoint, 24)
            self.dayPoint = self.dayPoint + self.anotherDay

        if (self.dayPoint > 0):
            self.date, self.anotherMonth = increasingDay(self.date, self.dayPoint)
            self.monthPoint = self.monthPoint + self.anotherMonth

        if (self.monthPoint > 0):
            self.month, self.anotherYear = increasingMonth(self.month, self.monthPoint)
            self.yearPoint = self.yearPoint + self.anotherYear

        if (self.yearPoint > 0):
            self.year = str(int(self.year) + self.yearPoint)

        """ Change Day when all of point has been added """
        self.monthIndex = self.listOfMonth.index(str(self.month))
        self.day = self.listOfDay[calendar.weekday(int(self.year), self.monthIndex, int(self.date))]

        self.result = [self.day, self.hour + ":" + self.minute, self.date, self.month, self.year]
        self.result = " ".join(self.result)
        self.update()

        if (encode):
            self.resultEncoded = base64.b64encode(bytes(self.result, "utf-8")).decode()

            return self.resultEncoded

        return self.result

    def timeCompare(self, increaseTime, defaultTime, decode=False):
        """ Split time """
        if (decode):
            increaseTime = base64.b64decode(increaseTime).decode().split()
            defaultTime = base64.b64decode(defaultTime).decode().split()

        else:
            increaseTime = increaseTime.split()
            defaultTime = defaultTime.split()

        for increase, default in zip(increaseTime, defaultTime):
            if (":" in increase or ":" in default):
                """ Remove ':'' """
                increase = increase.split(":")
                increase = "".join(increase)

                """ Remove ':' """
                default = default.split(":")
                default = "".join(default)

                increaseTime = [increaseTime[0], increase, increaseTime[2], increaseTime[3], increaseTime[4]]
                defaultTime = [defaultTime[0], default, defaultTime[2], defaultTime[3], defaultTime[4]]
                break

        """ Day Date Month Year (DDMY)"""
        increaseDDMY = [increaseTime[0], increaseTime[2], increaseTime[3], increaseTime[4]]
        defaultDDMY = [defaultTime[0], defaultTime[2], defaultTime[3], defaultTime[4]]

        """ Time Power """
        increasePower = int(increaseTime[1])
        defaultPower = int(defaultTime[1])

        """ Length Time """
        increaseLength = len(str(increasePower))
        defaultLength = len(str(defaultPower))

        """ If DDMY same """
        if (increaseDDMY == defaultDDMY):
            if (increaseLength > defaultLength):
                return True

            if (increaseLength == defaultLength):
                if (increasePower > defaultPower):
                    return True

                else:
                    return False

            return False

        else:
            """ Inceease DDMY """
            self.increaseDate = int(increaseTime[2])
            self.increaseMonth = self.listOfMonth.index(str(increaseTime[3]))
            self.increaseYear = int(increaseTime[4])

            """ Default DDMY """
            self.defaultDate = int(defaultTime[2])
            self.defaultMonth = self.listOfMonth.index(str(defaultTime[3]))
            self.defaultYear = int(defaultTime[4])

            """ DDMY Power """
            self.increasePower = 0
            self.defaultPower = 0

            """ Compare """
            if (self.increaseDate > self.defaultDate):
                self.increasePower += 1

            if (self.increaseDate < self.defaultDate):
                self.defaultPower += 1

            if (self.increaseMonth > self.defaultMonth):
                self.increasePower += 1

            if (self.increaseMonth < self.defaultMonth):
                self.defaultPower += 1

            """ Year will add 100 point  """
            if (self.increaseYear > self.defaultYear):
                self.increasePower += 100

            if (self.increaseYear < self.defaultYear):
                self.defaultPower += 100

            """ Return a Value """
            if (self.increasePower > self.defaultPower):
                return True

            else:
                return False

if __name__ == "__main__":
    import pdb

    obj = zalsTime()
    inc = obj.timeIncrease(incYear=9999)
    defa = obj.timeNow()
    print(inc)
    #print(obj.timeCompare(inc, defa))
