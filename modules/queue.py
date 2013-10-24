def queue(self, command):
    queue = self.conman.mpc.playlist()
    queuestr = "Next 4 of %s tracks:\n" % len(queue)
    for track in queue[ : 4]:
        queuestr += str(track)+"\n"
    self.conman.privmsg(queuestr)

self.map_command("queue", queue)
