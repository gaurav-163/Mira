#!/bin/bash

# Stop all services

echo " Stopping all services..."

pkill -f "python api.py" 2>/dev/null
pkill -f "next dev" 2>/dev/null

sleep 2

echo " All services stopped"
