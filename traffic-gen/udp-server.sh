#!/usr/bin/env bash

# Basic UDP server

PORT=30000 # port used to listen for client packets

echo "[INFO] Starting server"
nc -u -k -l $PORT # nc server
