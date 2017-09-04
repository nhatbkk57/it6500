#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import logging
import argparse

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


from download_model import download_tensorflow_model
download_tensorflow_model()


from uploadr.app import app


parser = argparse.ArgumentParser(description="Uploadr")
parser.add_argument(
    "--port", "-p",
    type=int,
    help="Port to listen on",
    default=8080,
)
args = parser.parse_args()
if __name__ == '__main__':
    
    flask_options = dict(   
        host='0.0.0.0',
        debug=True,
        port=args.port,
        threaded=True,
    )

    app.run(**flask_options)

