# -*- coding: utf-8 -*-

from dnslib import A, TXT, QTYPE, RCODE, server


class DNSLogger(object):
    def __init__(self, log_callback):
        self.log_callback = log_callback

    def log_pass(self, *args):
        pass

    def log_recv(self, handler, data):
        pass

    def log_send(self, handler, data):
        pass

    def log_request(self, handler, request):
        self.log_callback("DNS Request: [{0}:{1}] ({2}) <{3}> : {4}".format(handler.client_address[0], handler.client_address[1], handler.protocol, request.q.qname, QTYPE[request.q.qtype]), data=str(request.toZone("")).split('\n'))

    def log_reply(self, handler, reply):
        if reply.header.rcode == RCODE.NOERROR:
            self.log_callback("DNS Reply: [{0}:{1}] ({2}) / '{3}' ({4}) / RRs: {5}".format(handler.client_address[0], handler.client_address[1], handler.protocol, reply.q.qname, QTYPE[reply.q.qtype], ",".join([QTYPE[a.rtype] for a in reply.rr])), data=str(reply.toZone("")).split('\n'))
        else:
            self.log_callback("DNS Reply: [{0}:{1}] ({2}) / '{3}' ({4}) / {5}".format(handler.client_address[0], handler.client_address[1], handler.protocol, reply.q.qname, QTYPE[reply.q.qtype], RCODE[reply.header.rcode]), data=str(reply.toZone("")).split('\n'))

    def log_truncated(self, handler, reply):
        self.log_callback("DNS Truncated Reply: [{0}:{1}] ({2}) / '{3}' ({4}) / RRs: {5}".format(handler.client_address[0], handler.client_address[1], handler.protocol, reply.q.qname, QTYPE[reply.q.qtype], ",".join([QTYPE[a.rtype] for a in reply.rr])), data=str(reply.toZone("")).split('\n'))

    def log_error(self, handler, e):
        self.log_callback("DNS Invalid Request: [{0}:{1}] ({2}) :: {3}".format(handler.client_address[0], handler.client_address[1], handler.protocol, e))


class DNSServer(object):
    def resolve(self, request, handler):
        reply = request.reply()
        if request.q.qtype == QTYPE.ANY or request.q.qtype == QTYPE.A:
            reply.add_answer(server.RR(rname=request.q.qname, rtype=QTYPE.A, rdata=A(self.own_ip), ttl=10))
        return reply

    def __init__(self, port, log_callback=None):
        if log_callback is None:
            def f(msg, data=None):
                print(msg)
                if data is not None:
                    print(data)

            log_callback = f

        import socket
        self.own_ip = socket.gethostbyname(socket.gethostname())
        log_callback('Own IP:', self.own_ip)

        self.log_callback = log_callback
        self.port = port
        self.logger = DNSLogger(self.log_callback)
        self.servers = [
            server.DNSServer(self, address="0.0.0.0", port=self.port, tcp=False, logger=self.logger),
            server.DNSServer(self, address="0.0.0.0", port=self.port, tcp=True, logger=self.logger),
        ]
        for ds in self.servers:
            ds.start_thread()
