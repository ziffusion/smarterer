#!/bin/bash

HOST=localhost:8080

TEST=${1:-update}
DATA=${2:-$TEST}

shift 2

DATA=data_$DATA.json

COOKIES=test.cookies


function mcurl
{
    echo -e "\n\n"

    set -x

    curl -b $COOKIES -c $COOKIES "$@"

    set +x

    echo -e "\n\n"
}

function test_update
{
    mcurl -H "Content-Type: application/json" -d @$DATA http://$HOST/question/2
}

function test_create
{
    mcurl -H "Content-Type: application/json" -d @$DATA -X PUT http://$HOST/question
}

function test_query
{
    local WHERE="n0 > 10 && n0 || 1754 3009"
    mcurl -H "Content-Type: application/json" --get --data-urlencode "where=$WHERE" http://$HOST/question
    local WHERE="n0 > 10 && n0 || 1754 3009 && op || * /"
    mcurl -H "Content-Type: application/json" --get --data-urlencode "where=$WHERE" http://$HOST/question
}

test_$TEST "$@"
