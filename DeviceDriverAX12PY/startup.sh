#!/bin/sh

cd /

cd "$(dirname "$0")"

sudo python AX12DynamixelInterface.py

cd /