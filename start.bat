@echo off

:: Aktiválja a virtuális környezetet, ha létezik
if exist venv\Scripts\activate (
    call venv\Scripts\activate
)

:: Elindítja a Project-S agentet
python main.py