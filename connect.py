import socket
import ssl
import os
import queue
import threading
import time
import mpd


#Define connection class
class ConnectionMan:
    def __init__(self, global_confman):
        self.confman = global_confman

	#connect to mpd server
        self.mpc = mpd.MPDClient()
        try:
            self.mpc.connect(self.confman.get("MPD", "HOST"), self.confman.get("MPD", "PORT"))
        except (KeyError, ConnectionRefusedError) as e:
            if self.confman.get("MPD", "ENABLED"):
                raise e
            else:
                pass

        self.queue = queue.Queue()
        self.connect_irc()


    # message management functions ###
    def queue_raw(self, text):
        self.queue.put(str(text) + "\r\n", True)


    # You may bypass the queue, if needed.
    def send_raw(self, text):
        self.lock.acquire()
        print("%s >>> %s" % (time.strftime("%Y-%m-%d %H:%M", time.localtime()), text.strip()))
        self.s.send(bytes(text, "UTF-8"))
        self.lock.release()


    def queue_tick(self):
        OUTGOING_DELAY = self.confman.get("IRC", "OUTGOING_DELAY", 300)
        while True:
            self.send_raw(self.queue.get(True))
            time.sleep(OUTGOING_DELAY / 1000.0)
    ##################################


    # function for joining channels
    def join_irc(self, chan, nick=None, record=True):
        self.queue_raw("JOIN " + chan)

        while 1:
            try:
                line = self.s.recv(2048).decode("UTF-8")
            except UnicodeDecodeError:
                continue
            line = line.strip("\r\n")
            if "End of /NAMES list." in line:
                print("\n*** %s joined! ***\n" % chan)
                break
            else:
                print(line)
                
        time.sleep(1) # allows chan join to complete before messages are sent

        if not nick == None:
            self.privmsg("Invited by %s" % nick, chan)
            self.privmsg("Home channel: %s" % HOME_CHANNEL, chan)
            self.privmsg("Joined %s, invited by %s" % (chan, nick), HOME_CHANNEL)
	
        self.joined_chans.append(chan)

        if record:
            self.confman.setv("IRC", "CHANS", list(chan for chan in self.joined_chans if not chan == self.confman.get("IRC", "HOME_CHANNEL")))


    # parting channels
    def leave_irc(self, chan, nick, kicked=False):
        if chan == self.confman.get("IRC", "HOME_CHANNEL") and kicked:
            del self.joined_chans[self.joined_chans.index(chan)]
            self.join_irc(self.confman.get("IRC", "HOME_CHANNEL"), None, False)
        elif chan == HOME_CHANNEL:
            self.privmsg("Can't be PART'd from home channel")
        else:
            if kicked:
                self.privmsg("Kicked from %s by %s" % (chan, nick))
            else:
                partmsg = ("PART'd from %s by %s" % (chan, nick))
                self.queue_raw("PART %s %s" % (chan, partmsg))
                self.privmsg(partmsg)

            del self.joined_chans[self.joined_chans.index(chan)]
            self.confman.setv("IRC", "CHANS", list(set(chan for chan in self.joined_chans if not chan == self.confman.get("IRC", "HOME_CHANNEL"))))

            print("\n*** %s left! ***\n" % chan)


    # connect to IRC server, join HOME_CHANNEL
    def connect_irc(self):
	#If SSL is enabled use ssl
        if self.confman.get("IRC", "SSL", False):
            self.s = ssl.wrap_socket(socket.socket())
        else:
            self.s = socket.socket()

        self.s.connect((self.confman.get("IRC", "HOST"), self.confman.get("IRC", "PORT", 6669)))
        self.lock = threading.Lock()
        self.joined_chans = []

        thread = threading.Thread(target = self.queue_tick)
        thread.daemon = True
        thread.start()

        # As of RFC 2812, USER message params are: <user> <mode> <unused> <realname>
        self.queue_raw("USER " + self.confman.get("IRC", "NICK") + " 0 * :" + self.confman.get("IRC", "NICK"))
        self.queue_raw("NICK " + self.confman.get("IRC", "NICK"))

        print("*** Connecting... ***\n")

        while 1:
            try:
                line = self.s.recv(2048).decode("UTF-8")
            except UnicodeDecodeError:
                continue
            line = line.strip("\r\n")
            if "Nickname is already in use" in line:
                self.confman.setv("IRC", "NICK", self.confman.get("IRC", "NICK")+"_", True)
                self.queue_raw("NICK " + self.confman.get("IRC", "NICK"))
            elif "PING" in line:
                self.queue_raw("PONG :%s" % line[6:])
            elif "End of /MOTD command." in line:
                break
            print(line)

        self.join_irc(chan = self.confman.get("IRC", "HOME_CHANNEL"), record = False)
        for channel in self.confman.get("IRC", "CHANS", []):
            self.join_irc(chan = channel, record = False)


    # reconnect to MPD
    def reconnect_mpd(self):
        try:
            self.mpc.disconnect()
        except mpd.ConnectionError:
            pass
        self.mpc.connect(self.confman.get("MPD", "HOST"), self.confman.get("MPD", "PORT"))


    # reconnect to IRC
    def reconnect_irc(self):
        try:
            self.s.close()
        except:
            pass
        self.s = None
        self.connect_irc()


    # generic send function
    def gen_send(self, text, msginfo):
        try:
            self.privmsg("%s: %s" % (msginfo["prefix"], text), msginfo["chan"])
        except KeyError:
            self.privmsg(text, msginfo["chan"])


    #Define private message function
    # Splitting is something that should be taken care of beforehand.
    def privmsg(self, text, channel=None):
        if channel == None:
            channel = self.confman.get("IRC", "HOME_CHANNEL")
        if "\n" in text:
            raise Exception("connect.py:privmsg() no longer accepts multi-line messages")
        else:
            self.queue_raw("PRIVMSG " + channel + " :" + text)
