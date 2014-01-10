Testing the Long Access Client
=============================


This document describes the procedures in place for testing the command line client.

Basic operation (after installing the requirements below): `./scripts/nose.sh`

For more detail keep reading.

Environment variables
---------------------

The following environment variables modify the client's behavior and could be usefull for testing:

* `LA_API_VERIFY`. If this environment variable is equal to the number zero the client will not attempt to verify the API server SSL certificate.
* `LA_BATCH_OPERATION`. If this environment variable is defined then the client will not attempt user interaction in any case.
* `LA_API_URL`. Overrides the default API server url.
* `LA_SAFE`. If equal to the number zero then the client will disable certain sanity checks.

Requirements
------------

1. Python requirements: run `pip install -r requirements-test.txt`
2. Node.js requirements (for mock API): run `npm install robohydra/robohydra`

Unit testing
------------

You can run unit tests separately via `nose`: 

    nosetests

Feature testing
---------------

In order to run the feature tests you need the mock API server. It is available on github and you can install it locally like this:

    npm install robohydra/robohydra

Run it like this:

    ./node_modules/.bin/robohydra mockapi.conf

Then you can run the feature tests:

    behave

This will run the application under various scenarios, using a mock AWS API and a mock Long Access API. If you want to run the application using the mock Long Access API together with the real AWS API then you cannot simply call `behave`. You must first activate the [`realToken` test in robohydra](http://localhost:3000/robohydra-admin/tests/) and then run something like this:

    env LA_API_URL=http://localhost:3000/path/to/api python -m lacli.main /tmp/file 
