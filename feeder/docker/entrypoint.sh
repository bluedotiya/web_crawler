#!/bin/bash

kernprof -l /app/feeder.py
python -m line_profiler /app/feeder.py.lprof