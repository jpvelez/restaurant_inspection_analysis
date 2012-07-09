#!/bin/bash

COUNT=80
OFFSET=120

while [ $COUNT -gt 0 ]; do
    python search.py --consumer_key="88Ql36BiQPTsKqqUuIgIRA" --consumer_secret="d1Q1raKJppyMnDrRlTLj1cj2ygc" --token="vcge_k4r6cIFFPTt0AX1Elde6izhLtv0" --token_secret="5qFxwx4vmMU_86lI6ftxDdFo0Pc" --location="chicago" --term="restaurants" --offset=$OFFSET --limit=20

    echo Now querying with offset $OFFSET 
    echo Now querying with offset $OFFSET >> querying_log.txt

    let COUNT=COUNT-1
    let OFFSET=OFFSET+20

    sleep 60
done
