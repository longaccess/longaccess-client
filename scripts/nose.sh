#!/bin/sh
echo "Cleaning .pyc files"
find . -type f -name "*.pyc" -print0 | xargs -r -0 rm
echo "Running PEP8 checks"
pep8 .
if [ $? -ne 0 ]
then
    echo "PEP8 violations detected. Stopping run."
    exit 1
fi
nosetests
if [ $? -ne 0 ]
then
    echo "nosetests failed. Stopping run."
    exit 1
fi
echo "nosetests passed"

./node_modules/.bin/robohydra mockapi.conf &
robohydra_pid=$!

behave -w

kill $robohydra_pid

exit 0
