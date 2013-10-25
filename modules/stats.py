def stats(self, cmd):
    self.conman.privmsg(self.conman.mpc.stats())

self.map_command("stats", stats)
self.map_help("stats", ".stats - prints MPD statistics")
