#!/usr/bin/python
from gpiozero import MotionSensor
from time import sleep
from datetime import datetime, timedelta
from stairs import Stairs


class MOTIONDetector:

    def __init__(self):
        self.stairs = Stairs("MOTION", "sensors")
        
        self.stairs.init("conf/active_time", 15)
        self.stairs.init("conf/new_signal_read_after", 3)
        self.stairs.init("conf/step_sleep", 0.01)
        self.stairs.init("out/activated", False, True)

        self.stairs.init("conf/sensorUP_isON", True)
        self.stairs.init("conf/sensorDOWN_isON", True)
        self.stairs.init("conf/sensors_isON", True)
        self.stairs.init("in/ignoreSensors", False, True)
        self.stairs.init("in/ignoreSensors/output", True, True)

        self.pirDown = MotionSensor(4)
        self.pirUp = MotionSensor(17)


    def main(self):
        self.stairs.log("[    ] START!")

        while True:    
            sleep(self.stairs.get("conf/step_sleep"))

            if self.stairs.get("in/ignoreSensors"):
                if self.stairs.get("in/ignoreSensors/output") != self.stairs.get("out/activated"):
                    if self.stairs.get("in/ignoreSensors/output"):
                        self.stairs.log("[CONS] Activated!", start_active)
                    else:
                        self.stairs.log("[CONS] Deactivated!", start_active)
                    self.stairs.set("out/activated", stairs.get("in/ignoreSensors/output"))

            elif self.stairs.get("conf/sensors_isON"):

                if not self.stairs.get("out/activated"):
                    if self.stairs.get("conf/sensorUP_isON") and self.pirUp.motion_detected:
                        start_active = datetime.now()
                        self.stairs.set("out/activated", True)
                        self.stairs.log("[UP  ] Activated!", start_active)
                    elif self.stairs.get("conf/sensorDOWN_isON") and self.pirDown.motion_detected:
                        start_active = datetime.now()
                        self.stairs.set("out/activated", True)
                        self.stairs.log("[DOWN] Activated!", start_active)
                else:
                    current_time = datetime.now()
                    if self.stairs.get("conf/sensorUP_isON") and self.pirUp.motion_detected and current_time > start_active + timedelta(seconds=self.stairs.get("conf/new_signal_read_after")):
                        start_active = datetime.now()
                        self.stairs.log("[UP  ] Extend activation");
                    elif self.stairs.get("conf/sensorDOWN_isON") and self.pirDown.motion_detected and current_time > start_active + timedelta(seconds=self.stairs.get("conf/new_signal_read_after")):
                        start_active = datetime.now()
                        self.stairs.log("[DOWN] Extend activation");
                    if (current_time > start_active + timedelta(seconds=self.stairs.get("conf/active_time"))):
                        self.stairs.set("out/activated", False)
                        self.stairs.log("[    ] Deactivated!", current_time)

        self.stairs.log("[    ] END!")

if __name__ == "__main__":
    motion = MOTIONDetector()
    motion.main()   
