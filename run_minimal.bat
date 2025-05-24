@echo off
:: Project-S Minimális Verzió Közvetlen Indító

:: Ellenőrizzük a virtuális környezetet
if exist venv\Scripts\activate (
    call venv\Scripts\activate
)

:: Környezeti változók beállítása
set OPENAI_API_KEY=sk-prGWsA
set OPENROUTER_API_KEY=

echo.
echo ===============================================================
echo Project-S Agent - Minimális Verzió Közvetlen Indítása
echo ===============================================================
echo.

:: Elindítjuk a minimális rendszert (eseménykezelés)
python main_minimal.py

:: Deaktiváljuk a virtuális környezetet
if exist venv\Scripts\activate (
    deactivate
)
