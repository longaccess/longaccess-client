Testing the Long Access Client
=============================


This document describes the procedures in place for testing the command line client.

Basic operation (after installing the requirements below): `./scripts/nose.sh`

For more detail keep reading.

Requirements
------------

1. Python requirements: run `pip install -r requirements-test.txt`
2. Node.js requirements (for mock API): npm install robohydra

Unit testing
------------

You can run unit tests separately via `nose`: 

    nosetests

Feature testing
---------------

In order to run the feature tests you need the mock API server. Run it like this:

    ./node_modules/.bin/robohydra mockapi.conf

Then you can run the feature tests:

    behave


