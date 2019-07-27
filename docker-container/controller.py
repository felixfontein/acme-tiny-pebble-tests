#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import ssl
import sys
import urllib

from functools import partial

from flask import Flask

from dns_server import DNSServer


app = Flask(__name__)
app.config['LOGGER_HANDLER_POLICY'] = 'always'

PEBBLE_PATH = os.path.join(os.path.abspath(os.environ.get('GOPATH', '.')), 'src', 'github.com', 'letsencrypt', 'pebble')


def log(message, data=None, program='Controller'):
    sys.stdout.write('[{0}] {1}\n'.format(program, message))
    if data:
        if not isinstance(data, list):
            data = [data]
        while data and not data[-1]:
            data = data[:-1]
        for value in data:
            sys.stdout.write('[{0}] | {1}\n'.format(program, value))
    sys.stdout.flush()


def setup_loggers():
    class SimpleLogger(logging.StreamHandler):
        def emit(self, record):
            try:
                msg = self.format(record)
                log(msg)
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as _:
                self.handleError(record)

    log_handler = SimpleLogger()
    log_handler.setLevel(logging.DEBUG)
    app.logger.handlers = []
    app.logger.propagate = False
    app.logger.addHandler(log_handler)
    logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.propagate = False
    logger.addHandler(log_handler)


setup_loggers()


@app.route('/')
def m_index():
    return 'ACME test environment controller'


dns_server = DNSServer(port=53, log_callback=partial(log, program='DNS Server'))


@app.route('/.well-known/acme-challenge/<string:filename>')
def get_http_challenge(filename):
    try:
        with open(os.path.join("/challenges", filename), "rb") as f:
            data = f.read()
            log('Reading challenge {0} ({1} bytes)'.format(filename, len(data)))
            return data, 204 if len(data) == 0 else 200
    except FileNotFoundError:
        log('Cannot find challenge {0}'.format(filename))
        return 'not found', 404


@app.route('/root-certificate-for-acme-endpoint')
def get_root_certificate_minica():
    with open(os.path.join(PEBBLE_PATH, 'test', 'certs', 'pebble.minica.pem'), 'rt') as f:
        return f.read()


@app.route('/root-certificate-for-ca')
def get_root_certificate_pebble():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return urllib.request.urlopen("https://localhost:15000/roots/0", context=ctx).read()


if __name__ == "__main__":
    app.run(debug=False, host='::', port=int(os.environ.get('CONTROLLER_PORT', 80)))
