def isup(self, msginfo):
    domains = msginfo["msg"].split(" ")[1:]
    import socket
    for domain in domains:
        domain = re.sub(".*://", "", domain)
        domain = domain.split("/")[0]
        try:
            domain_split = domain.split(":")
            domain, port = domain_split[0], int(domain_split[1]) if len(domain_split) > 1 else 80
            host = socket.gethostbyname(domain)
        except socket.gaierror:
            self.conman.gen_send("Couldn't resolve %s to IP" % domain, msginfo)
            continue
        except ValueError:
            self.conman.gen_send("Couldn't get port number from %s" % domain, msginfo)
            continue
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            s.connect((host, port))
        except socket.error as e:
            if e.strerror == "Connection refused":
                self.conman.gen_send("Port %s doesn't appear to be open on %s (%s)" % (str(port), domain, host), msginfo)
            else:
                self.conman.gen_send("Connection to %s:%s (%s) failed: %s" % (domain, str(port), host, e.strerror), msginfo)
        except socket.timeout:
            self.conman.gen_send("%s (%s) timed out" % (domain, host), msginfo)
        else:
            self.conman.gen_send("%s:%s (%s) is reachable!" % (domain, str(port), host), msginfo)
        finally:
            s.close()

self.commandlist["isup"] = {
        "type": MAPTYPE_COMMAND,
        "function": isup,
        "help": "Check whether website is up"
        }
