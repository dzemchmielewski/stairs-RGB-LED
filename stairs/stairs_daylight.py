#!/usr/bin/python
from time import sleep
from datetime import datetime, timedelta
from stairs import Stairs
from astral import Astral, Location


class DayLight:

    def __init__(self):
        self.stairs = Stairs("DAYLIGHT", "daylight")
        self.stairs.init("conf/step_sleep", 30, True)
        #self.stairs.init("conf/program", "static", True)
        self.stairs.init("conf/program", "daylight", True)
        self.stairs.init("conf/program/static/start/hour", 8, True)
        self.stairs.init("conf/program/static/start/minute", 15, True)
        self.stairs.init("conf/program/static/end/hour", 15, True)
        self.stairs.init("conf/program/static/end/minute", 0, True)
        self.location = Location(('Torun', 'Poland', 53.01, 18.60, 'Europe/Warsaw', 0))
        ####self.stairs.setExternal("sensors", "conf/sensors_isON", False)
        

    def status(self, actualtime):
        (startOff, endOff) = self.getStartEndOFFDates(actualtime)
        return not (actualtime > startOff and actualtime < endOff)

    def getStartEndOFFDates(self, actualtime):
        if self.stairs.get("conf/program") == "static":
            startOff = datetime.now().replace(hour=self.stairs.get("conf/program/static/start/hour"), minute=self.stairs.get("conf/program/static/start/minute"), second=0, microsecond=0)
            endOff = datetime.now().replace(hour=self.stairs.get("conf/program/static/end/hour"), minute=self.stairs.get("conf/program/static/end/minute"), second=0, microsecond=0)
            return (startOff, endOff)
        elif self.stairs.get("conf/program") == "daylight":
            (startOff, endOff) = self.location.daylight(date=actualtime)
            (startOff, endOff) = (startOff.replace(tzinfo=None) + timedelta(minutes=30), endOff.replace(tzinfo=None) - timedelta(minutes=15))
            return (startOff, endOff)
        else:
            self.stairs.log("[FATAL] Daylight program name '" + self.stairs.get("conf/program") + "' is not recognized", actualtime)
            return None
        
    
    def main(self):
        self.stairs.log("[    ] START!")

        while True:    
            sleep(self.stairs.get("conf/step_sleep"))
            now = datetime.now()
            status = self.status(now)
            currentstatus = self.stairs.getExternal("sensors", "conf/sensors_isON")
            if status != currentstatus:
                self.stairs.setExternal("sensors", "conf/sensors_isON", status)
                (startOff, endOff) = self.getStartEndOFFDates(now)
                if status:
                    self.stairs.log("[  ON ] Switching sensor ON. Interval: [" + str(startOff) + " - " + str(endOff) + "]", now)
                else:
                    self.stairs.log("[ OFF ] Switching sensor OFF. Interval: [" + str(startOff) + " - " + str(endOff) + "]", now)
                    
        self.stairs.log("[    ] END!")

if __name__ == "__main__":
    daylight = DayLight()
    daylight.main()   
