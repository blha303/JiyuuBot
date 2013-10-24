def display_help(self, command):
    cmdlist = "Available commands: "
    for keys in self.commandlist.keys():
        cmdlist += ".%s " % keys
    self.conman.privmsg(cmdlist)
    if not command == "":
        self.conman.privmsg(self.helplist[command])

self.map_command("help", display_help)
self.map_help("help", ".help - displays help")
