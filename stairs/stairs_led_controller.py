#!/usr/bin/python

from gpiozero import RGBLED
from time import sleep
from decimal import Decimal as d
from stairs import Stairs
import random


class LEDController:

    def __init__(self):
        self.stairs = Stairs(" LED  ", "led")
        self.stairs.init("conf/program/fade/step_sleep", 0.005)
        self.stairs.init("conf/program/static/color", (d(1),d(1),d(1)))
        self.stairs.init("conf/program", "fadeBRG", True)
        self.stairs.init("conf/program/police/time", 0.2)
        self.stairs.init("conf/program/fade/lastcolor", (d(0),d(0),d(0)))
        self.led = RGBLED(26, 19, 13)
        self.check_period = 0
        self.exitNow = False
        self.debug = False
        self.currentProgram = None

        
    def sleep(self, sleep_time = None):
        if sleep_time is None:
            sleep_time = self.stairs.get("conf/program/fade/step_sleep")
        sleep(sleep_time)
        self.check_period = self.check_period + sleep_time
        if self.check_period >= 0.1:
            self.check_period = 0
            if (not self.stairs.getExternal("sensors", "out/activated")) or self.currentProgram != self.stairs.get("conf/program"):
                self.exitNow = True

    def __led__(self, (r,g,b)):
        if self.debug:
            print("[" + "{0:.3f}".format(r) + ", " + "{0:.3f}".format(g) + ", " + "{0:.3f}".format(b) + "]")
        self.led.color = (r,g,b)
        
    def __color__(self, step, f, t, numberOfSteps):
        if f <= t:
            return step*(t-f)/numberOfSteps
        else:
            return 1 - step*((f-t)/numberOfSteps)

    def __fade__(self, ((r_from, r_to), (g_from, g_to), (b_from, b_to))=((0,0),(0,0),(0,0))):
        numberOfSteps = 1000
        for step in xrange (0, numberOfSteps):
            self.sleep()
            if self.exitNow:
                self.stairs.set("conf/program/fade/lastcolor", (self.__color__(step, r_from, r_to, numberOfSteps), self.__color__(step, g_from, g_to, numberOfSteps), self.__color__(step, b_from, b_to, numberOfSteps)))
                return
            self.__led__((self.__color__(step, r_from, r_to, numberOfSteps), self.__color__(step, g_from, g_to, numberOfSteps), self.__color__(step, b_from, b_to, numberOfSteps)))
            
    def __fade_out__(self, (r_from, g_from, b_from)):
        numberOfSteps = 200
        sleep_time = self.stairs.get("conf/program/fade/step_sleep")
        for step in xrange (0, numberOfSteps):
            self.sleep()
            sleep(sleep_time)
            self.__led__((self.__color__(step, r_from, 0, numberOfSteps), self.__color__(step, g_from, 0, numberOfSteps), self.__color__(step, b_from, 0, numberOfSteps)))

    def __fade_in__(self, (r_to, g_to, b_to)):
        numberOfSteps = 200
        for step in xrange (0, numberOfSteps):
            self.sleep()
            if self.exitNow:
                self.stairs.set("conf/program/fade/lastcolor", (self.__color__(step, 0, r_to, numberOfSteps), self.__color__(step, 0, g_to, numberOfSteps), self.__color__(step, 0, b_to, numberOfSteps)))
                return
            self.__led__((self.__color__(step, 0, r_to, numberOfSteps), self.__color__(step, 0, g_to, numberOfSteps), self.__color__(step, 0, b_to, numberOfSteps)))
        

    def fade(self, ((r_from, r_to), (g_from, g_to), (b_from, b_to))=((0,0),(0,0),(0,0))):
        self.stairs.log("[FADE] started")
        while True:
            self.__fade__(((r_from, r_to), (g_from, g_to), (b_from, b_to)))
            if self.exitNow:
                self.stairs.log("[FADE] terminated")
                return
            self.__fade__(((r_to, r_from), (g_to, g_from), (b_to, b_from)))
            if self.exitNow:
                self.stairs.log("[FADE] terminated")
                return
        
    def fadeBRG(self):
        self.stairs.log("[FADE BRG] started")
        c = [((d(0),d(1)),(d(0),d(0)),(d(1),d(0))),
             ((d(1),d(0)),(d(0),d(1)),(d(0),d(0))),
             ((d(0),d(0)),(d(1),d(0)),(d(0),d(1)))]

        randint = random.randint(0,2)
        colors = []
        for i in range(len(c)):
            colors.append(c[(i + randint)%3])

        self.__fade_in__((colors[0][0][0], colors[0][1][0], colors[0][2][0]))
        if self.exitNow:
            self.stairs.log("[FADE BRG] terminated")
            #self.__fade_out__(self.stairs.get("conf/program/fade/lastcolor"))
            return

        while True:
            for c in colors:
                self.__fade__(c)
                if self.exitNow:
                    self.stairs.log("[FADE BRG] terminated")
                    #self.__fade_out__(self.stairs.get("conf/program/fade/lastcolor"))
                    return

    def static(self):
        self.stairs.log("[STATIC] started")
        color = self.stairs.get("conf/program/static/color")
        newcolor = color
        self.stairs.log("[STATIC] color: " + str(color))
        self.__led__(newcolor)
        while True:
            self.sleep(0.1)
            if self.exitNow:
                self.stairs.log("[STATIC] terminated")
                return
            newcolor = self.stairs.get("conf/program/static/color")
            if color != newcolor:
                self.stairs.log("[STATIC] new color: " + str(newcolor))
                self.__led__(newcolor)
                color = newcolor

    def police(self):
        self.stairs.log("[POLICE] started")
        color = ((1,0,0), (0,0,1))
        i = 0
        time = 0
        while True:
            self.__led__(color[i])
            self.sleep(0.1)
            time = time + 0.1
            if time > self.stairs.get("conf/program/police/time"):
                time = 0
                i = (i + 1) % 2
            if self.exitNow:
                self.stairs.log("[POLICE] terminated")
                return
                
    def main(self):
        while True:
            if self.stairs.getExternal("sensors", "out/activated"):
                program = self.stairs.get("conf/program")
                if program in ["static", "fadeBRG", "police"]:
                    self.currentProgram = program
                    getattr(self, program)()
                    self.__led__((0,0,0))
                    self.exitNow = False
                else:
                    self.stairs.log("[ERROR] unknown program: " + program)
                    sleep(5)
            else:
                sleep(0.1)

if __name__ == "__main__":
    led = LEDController()
    led.main()
