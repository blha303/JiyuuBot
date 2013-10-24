import os
import glob
import connect
import mpd
import threading

exec(open(os.path.join(os.path.dirname(__file__), "config.py"), "r").read())

class PluginMan:
    def trywrapper(self, command, arg):
        try:
            self.commandlist[command](self, arg)
        except Exception as e:
            if type(e) == mpd.ConnectionError:
                self.conman.reconnect_mpd()
                t.start()
            else:
                self.conman.privmsg("Error: %s" % e)

    def execute_command(self, command):
        try:
            mapped = command[:command.index(" ")]
            arg = command[command.index(" ")+1:]
        except ValueError:
            mapped = command
            arg = ""
        t = threading.Thread(target = self.trywrapper, args = (mapped, arg))
        t.daemon = 1
        t.start()

    def map_help(self, command, message):
        self.helplist[command] = message

    def map_command(self, command, function):
        self.commandlist[command] = function

    def load(self, wut=None):
        pluginlist = glob.glob(self.modulespath + "*.py")
        for plugin in pluginlist:
            exec(open(plugin, "r").read())

    def __init__(self):
        self.modulespath = os.path.join(os.path.dirname(__file__), "modules") + os.sep
        self.commandlist = {"reload": self.load}
        self.helplist = {"reload": ".reload - reloads modules"}
        self.conman = connect.ConnectionMan()
        self.load()
