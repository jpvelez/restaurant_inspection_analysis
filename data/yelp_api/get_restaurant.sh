#!/bin/bash

NAME="restaurant"
LOCATION='935 W Webster Ave, Chicago, IL, 60614'

python search.py --consumer_key="88Ql36BiQPTsKqqUuIgIRA" --consumer_secret="d1Q1raKJppyMnDrRlTLj1cj2ygc" --token="vcge_k4r6cIFFPTt0AX1Elde6izhLtv0" --token_secret="5qFxwx4vmMU_86lI6ftxDdFo0Pc" --location="$LOCATION" --term="$NAME" --offset=0 --limit=20
