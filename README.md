# Smarterer

1. [Install](#install)
1. [Logs](#logs)
1. [Test](#test)
1. [Run](#run)
1. [Endpoints](#endpoints)

## Install

### Get code base

    git clone https://github.com/ziffusion/smarterer.git

### Software map

    smarterer/config    config files
    smarterer/logs      log files
    smarterer/run       run directory
    smarterer/server    flask webapp, endpoints
    smarterer/tests     unit tests

### Establish a virtual environment (optional)

### Install dependencies

    cd smarterer/config

    pip install -r REQUIREMENTS.TXT

### Change configuration (optional)

    cd smarterer/config

    vi system.py            # change base values

    -OR-

    vi system-custom.py     # override base values

## Logs

    cd smarterer/logs

    tail -f system.log

## Test

    cd smarterer/tests

    python -m unittest test_server

    -OR-

    python -m unittest discover

## Run

    cd smarterer/run

    python wsgi.py

## Endpoints

The application implements a single endpoint that supports various REST operations.

The endpoints consume and produce json objects.

The object in play is the question object, which has the following fields:

    question.id             unique object identifier
    question.n0             operand-1
    question.n1             operand-2
    question.n2             answer
    question.op             operator + - * /
    question.distractors    list of alternative answers

### CREATE a question

    PUT /question

json input example:

    {
        "distractors": [
            5, 
            6, 
            7
        ], 
        "n0": 1, 
        "n1": 2, 
        "n2": 3, 
        "op": "+", 
        "object": "ApiObject"
    }

The id of the newly created object is returned.

json output example:

    {
        "code": 200, 
        "msg": "OK", 
        "object": "ApiObject", 
        "question": {
            "distractors": [
                5, 
                6, 
                7
            ], 
            "id": 2, 
            "n0": 1, 
            "n1": 2, 
            "n2": 3, 
            "op": "+", 
            "object": "ApiObject"
        }
    }

### READ a question

    GET /question/<id>

json output similar to CREATE above.

### READ question list

    GET /question?where=<clause>&sort=<clause>&start=<number>&limit=<number>

The where clause is specified using a DSL that supports following operators against any of the fields.

    ==  equal to
    !=  not equal to
    >   greater than
    >=  greater than equal to
    <   less than
    <=  less than equal to
    ||  in
    &&  and

Example of where clause:

    n0 > 3008 && n1 <= 500 && op || * + - && n2 > 5000 && n0 || 7546 6345 9800

The sort clause specifies list of columns to sort by.

Example of sort clause:

    n1 op n0

The start and limit clauses control pagination of results.

json output example:

    {
        "code": 200, 
        "limit": 2, 
        "msg": "OK", 
        "object": "ApiObject", 
        "questions": [
            {
                "distractors": [
                    3572, 
                    8772, 
                    9415
                ], 
                "id": 2, 
                "n0": 3009, 
                "n1": 5075, 
                "n2": 15270675, 
                "op": "*", 
                "object": "ApiObject"
            }, 
            {
                "distractors": [
                    7360, 
                    2043, 
                    2982, 
                    1235
                ], 
                "id": 3, 
                "n0": 9702, 
                "n1": 9102, 
                "n2": 600, 
                "op": "-", 
                "object": "ApiObject"
            }
        ], 
        "sort": "op", 
        "start": 2, 
        "where": "n0 > 500"
    }

### UPDATE a question

    POST /question/<id>

json input similar to CREATE above.

### DELETE a question

    DELETE /question/<id>
