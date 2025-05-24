@echo off
:: Project-S Minimális Verzió Indító

:: Ellenőrizzük a virtuális környezetet
if exist venv\Scripts\activate (
    call venv\Scripts\activate
)

:: Környezeti változók beállítása - API kulcsok
:: A rendszer ellenőrzésekor egy OpenAI API kulcs már be volt állítva, használjuk azt
set OPENAI_API_KEY=sk-prGWsA
set OPENROUTER_API_KEY=

echo.
echo ===============================================================
echo Project-S Agent - Minimális Verzió Indítása
echo ===============================================================
echo.

if "%OPENAI_API_KEY%"=="" (
    if "%OPENROUTER_API_KEY%"=="" (
        echo FIGYELEM: Nincsenek API kulcsok beállítva!
        echo Nyisd meg ezt a fájlt és add meg az API kulcsaidat.
    )
)

echo Válassz indítási módot:
echo 1 - Csak alaprendszer (eseménykezelés)
echo 2 - LangGraph integráció (folyamatkezelés)
echo 3 - Teljes minimális verzió (AI integráció)

set /p mode="Válassz (1-3): "

if "%mode%"=="1" (
    python main_minimal.py
) else if "%mode%"=="2" (
    python main_minimal_langgraph.py
) else if "%mode%"=="3" (
    python main_minimal_full.py
) else (
    echo Érvénytelen választás!
)

:: Deaktiváljuk a virtuális környezetet
if exist venv\Scripts\activate (
    deactivate
)
