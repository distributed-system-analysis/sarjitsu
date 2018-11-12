#!/bin/bash

FILENAME=docker-compose.yml

services=$(awk '/services:/{getline; print}' $FILENAME)
services+=$'\n'

# services+=$(cat docker-compose.yml | grep -Pzo '\n\n(.+?)\n' | sed '/^\x0$/d' | sed '/^$/d' | sed '/\s#.*/d')

services+=$(grep -Pzo '\n\n(.+?)\n' $FILENAME | \
		sed '/^\x0$/d' | \
		sed '/^$/d' | \
		sed '/\s#.*/d')


echo "$services" | sed s/://g | cut -d' ' -f3
