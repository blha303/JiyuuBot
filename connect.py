import socket
import mpd
import ssl
import os

exec(open(os.path.join(os.path.dirname(__file__), "config.py"), "r").read())

class ConnectionMan:
    def __init__(self):
        self.mpc = mpd.MPDClient()
        self.mpc.connect(MPD_HOST, MPD_PORT)

        if(SSL):
            self.s = ssl.wrap_socket(socket.socket( ))
        else:
            self.s = socket.socket( )
        self.s.connect((HOST, PORT))
        self.s.send("USER " + NICK + " " + NICK + " " + NICK + " :" + NICK + "\n")
        self.s.send("NICK " + NICK + "\r\n")
        self.s.send("JOIN " + HOME_CHANNEL + "\r\n")

    def privmsg(self, text):
        self.s.send("PRIVMSG " + HOME_CHANNEL + " :\r\n")
        #can only send 5 lines at a time on Rizon before being kicked for flood
        text=str(text)
        for msg in text.split("\n"):
            self.s.send("PRIVMSG " + HOME_CHANNEL + " :" + str(msg) + "\r\n")

    def reconnect_mpd(self):
        try:
            self.mpc.disconnect()
        except mpd.ConnectionError:
            pass
        self.mpc.connect(MPD_HOST, MPD_PORT)
