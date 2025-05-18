#!/bin/bash

# Aktiválja a virtuális környezetet, ha létezik
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Elindítja a Project-S agentet
python main.py