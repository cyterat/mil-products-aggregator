#!/bin/bash
find /data/__pycache__ -maxdepth 0 -mmin +30 -exec rm -fr {} +