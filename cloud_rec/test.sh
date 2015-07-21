#!/bin/bash

echo "lame -f -b 128 -m s --decode $1 $2"

sleep 1

lame -f -b 128 -m s --decode $1 $2

exit $?
