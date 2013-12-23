def get_perm_argparser(self, args):
    args = args.split(" ")
    if args[0] == "nick":
        self.conman.privmsg("Permission level for %s: %s" % (args[1], self.permsman.get_nick_perms(args[1])))
    elif args[0] == "cmd":
        self.conman.privmsg("Permission level for %s: %s" % (args[1], self.permsman.get_cmd_perms(args[1])))

def set_perm_argparser(self, args):
    args = args.split(" ")
    nick = args[1]
    lvl = args[2]
    if args[0] == "nick":
        self.conman.privmsg("Setting permission level for %s: %s" % (nick, lvl))
        self.permsman.set_nick_perms(nick, lvl)
    elif args[0] == "cmd":
        self.conman.privmsg("Setting permission level for %s: %s" % (cmd, lvl))
        self.permsman.set_cmd_perms(cmd, lvl)

self.map_command("getperm", get_perm_argparser, False)
self.map_command("setperm", set_perm_argparser, False)
