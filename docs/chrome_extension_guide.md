# Project-S Agent Chrome Bővítmény Telepítési Útmutató

Ez az útmutató segít a Project-S Agent Chrome bővítmény telepítésében, amely lehetővé teszi Claude és más AI asszisztensek számára, hogy közvetlenül kommunikáljanak a Project-S rendszerrel a böngészőből.

## Előfeltételek

- Google Chrome böngésző
- Futó Project-S rendszer

## Telepítési lépések

1. Nyissa meg a Chrome böngészőt és navigáljon a `chrome://extensions` címre
2. Kapcsolja be a "Fejlesztői mód" opciót a jobb felső sarokban
3. Kattintson a "Kicsomagolt bővítmény betöltése" gombra
4. Válassza ki a `chrome_extension` mappát a Project-S repository-ból
5. A bővítmény most telepítve van, és megjelenik a böngésző eszköztárán

## Konfiguráció

1. Kattintson a Project-S ikonra az eszköztáron
2. Állítsa be az API URL-t (alapértelmezetten `http://localhost:8000/api/dom`)
3. Állítsa be a lekérdezési intervallumot (alapértelmezetten 1000 ms)
4. Kattintson a "Save Settings" gombra

## Használat

A bővítmény automatikusan figyeli a Claude és ChatGPT chat felületeit a következő formátumú parancsok után:

### Példa parancsok Claude-tól

Claude-ot például így kérheti kód generálására a Project-S rendszeren keresztül:
[S_COMMAND]
{
"type": "code",
"content": "Készíts egy Python függvényt, amely ellenőrzi, hogy egy szám prím-e",
"options": {
"language": "python"
}
}
[/S_COMMAND]

Vagy fájlművelet végrehajtására:
[S_COMMAND]
{
"type": "file",
"operation": "read",
"path": "README.md"
}
[/S_COMMAND]

## Hibaelhárítás

- Ellenőrizze, hogy a Project-S rendszer fut-e
- Ellenőrizze az API szerver állapotát (alapértelmezetten `http://localhost:8000/api/status`)
- Ellenőrizze a Chrome bővítmény konzoljában a hiba

### A Chrome bővítmény hibakeresési tippjei:
- Nyisson egy új lapot a chrome://extensions címen és kattintson a "háttér és hibakeresés" linkre a Project-S bővítménynél
- Ellenőrizze a konzolon lévő hibaüzeneteket
- Ellenőrizze, hogy a DOM parancsok megfelelő formátumúak-e

## Claude-integráció

Ezzel a bővítménnyel Claude képes lesz közvetlenül utasítani a Project-S rendszert, miközben folytatja a beszélgetést a felhasználóval. Claude természetes módon tud majd válaszolni a felhasználó kérdéseire, miközben a háttérben végrehajtja a Project-S műveleteket.