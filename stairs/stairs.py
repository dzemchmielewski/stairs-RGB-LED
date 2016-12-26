from datetime import datetime
import pylibmc

class Stairs:
    def __init__(self, logname, code):
        self.code = code
        self.logname = logname
        self.mc = pylibmc.Client(["127.0.0.1"], binary=True,
                            behaviors={"tcp_nodelay": True,
                                       "ketama": True})
        
    def log(self, msg, now = None):
        if now is None:
            now = datetime.now()
        print("[" + self.logname + "][" + "{:%Y-%m-%d %H:%M:%S.%f}".format(now) + "] " + msg)

    def get(self, name):
        return self.mc.get(self.code + "/" + name)

    def getBool(self, name):
        value = self.mc.get(self.code + "/" + name)
        if str(value).lower() in ("yes", "y", "true",  "t", "1"):
            return True
        if str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"):
            return False
        raise Exception('Invalid value for boolean conversion: ' + str(value))

    def set(self, name, value):
        self.mc.set(self.code + "/" + name, value)

    def getExternal(self, external_code, name):
        return self.mc.get(external_code + "/" + name)

    def init(self, name, value, force = False):
        if force or self.get(name) is None:
            self.log("INITIALIZE: " + self.code + "/" + name + ": " + str(value))
            self.set(name, value)
        else:
            self.log("CONFIGURATION: " + self.code + "/" + name + ": " + str(self.get(name)))
            

