#!/usr/bin/env python
import acme_tiny
import ssl
import sys

original_urlopen = acme_tiny.urlopen

def monkeypatched_urlopen(*args, **kwarg):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return original_urlopen(*args, context=ctx, **kwarg)

acme_tiny.urlopen = monkeypatched_urlopen

acme_tiny.main(sys.argv[2:])
