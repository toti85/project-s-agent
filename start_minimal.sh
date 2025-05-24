#!/bin/bash
# Project-S Minimális Verzió Indító

# Ellenőrizzük a virtuális környezetet
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Környezeti változók beállítása - API kulcsok
# Töltsd ki ezeket a saját API kulcsaiddal!
export OPENAI_API_KEY=""
export OPENROUTER_API_KEY=""

echo
echo "==============================================================="
echo "Project-S Agent - Minimális Verzió Indítása"
echo "==============================================================="
echo

if [ -z "$OPENAI_API_KEY" ] && [ -z "$OPENROUTER_API_KEY" ]; then
    echo "FIGYELEM: Nincsenek API kulcsok beállítva!"
    echo "Nyisd meg ezt a fájlt és add meg az API kulcsaidat."
fi

echo "Válassz indítási módot:"
echo "1 - Csak alaprendszer (eseménykezelés)"
echo "2 - LangGraph integráció (folyamatkezelés)"
echo "3 - Teljes minimális verzió (AI integráció)"

read -p "Válassz (1-3): " mode

if [ "$mode" == "1" ]; then
    python main_minimal.py
elif [ "$mode" == "2" ]; then
    python main_minimal_langgraph.py
elif [ "$mode" == "3" ]; then
    python main_minimal_full.py
else
    echo "Érvénytelen választás!"
fi
