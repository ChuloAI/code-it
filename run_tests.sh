#!/bin/bash

if [ -z "$1" ]; then
    export PYTHONPATH=${PYTHONPATH}:code_it && pytest -vvvv
else
    export PYTHONPATH=${PYTHONPATH}:code_it && pytest $1 -vvvv
fi
