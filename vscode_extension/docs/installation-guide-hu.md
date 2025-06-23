# Project-S VSCode Kiterjesztés Telepítési és Konfigurációs Útmutató

Ez az útmutató lépésről lépésre ismerteti a Project-S VSCode kiterjesztés telepítését, konfigurálását és használatát kódelemzéshez, kódgeneráláshoz és dokumentációhoz.

## Telepítés

### Előfeltételek

A kiterjesztés telepítése előtt győződjön meg arról, hogy rendelkezik:

1. Visual Studio Code 1.60.0 vagy újabb verzióval
2. Node.js 14.0.0 vagy újabb verzióval
3. Futó és elérhető Project-S szerverrel

### Telepítési Módszerek

#### VSIX Fájlból

1. Töltse le a legújabb `project-s-extension.vsix` fájlt a kiadások oldalról
2. Nyissa meg a Visual Studio Code-ot
3. Navigáljon a Bővítmények nézetre (Ctrl+Shift+X vagy Cmd+Shift+X)
4. Kattintson a "..." menüre a Bővítmények nézet jobb felső sarkában
5. Válassza a "Telepítés VSIX-ből..." lehetőséget
6. Navigáljon a letöltött VSIX fájlhoz és válassza ki
7. Indítsa újra a VSCode-ot, amikor a rendszer kéri

#### Forráskódból

1. Klónozza a repository-t:
   ```bash
   git clone https://github.com/organization/project-s-vscode-extension.git
   ```

2. Navigáljon a kiterjesztés könyvtárába:
   ```bash
   cd project-s-vscode-extension
   ```

3. Telepítse a függőségeket:
   ```bash
   npm install
   ```

4. Építse a kiterjesztést:
   ```bash
   npm run compile
   ```

5. Csomagolja a kiterjesztést:
   ```bash
   npm run package
   ```

6. Telepítse a csomagolt kiterjesztést:
   ```bash
   code --install-extension project-s-extension-*.vsix
   ```

## Konfiguráció

A telepítés után konfigurálnia kell a kiterjesztést a Project-S szerverhez való kapcsolódáshoz:

1. Nyissa meg a VSCode Beállításokat (Fájl > Beállítások > Beállítások vagy Ctrl+,)
2. Keressen rá a "Project-S" kifejezésre
3. Konfigurálja a következő beállításokat:
   - **Project-S: Server URL**: A Project-S szerver URL-je (pl. `http://localhost:8000`)
   - **Project-S: API Key**: Az API kulcs a hitelesítéshez (ha alkalmazandó)
   - **Project-S: Auto Connect**: Automatikusan kapcsolódjon-e a szerverhez a VSCode indításakor

Alternatívaként hozzáadhatja ezeket a beállításokat a `settings.json` fájljához:

```json
{
  "project-s.serverUrl": "http://localhost:8000",
  "project-s.apiKey": "your-api-key",
  "project-s.autoConnect": true
}
```

## Használat

### Kapcsolódás a Project-S szerverhez

1. Nyissa meg a Project-S oldalsáv nézetet a Project-S ikonra kattintva az Activity Bar-ban
2. Kattintson a "Connect" gombra az oldalsávban
3. Ha a kapcsolat sikeres, az állapotjelző zöldre vált és a "Connected" felirat jelenik meg

### Munkafolyamatok Kezelése

A Project-S oldalsáv megjeleníti az összes elérhető munkafolyamatot a szerverről.

#### Új Munkafolyamat Létrehozása

1. Kattintson a "+" gombra a Munkafolyamatok szekció fejlécében
2. Kövesse az utasításokat a név megadásához és a munkafolyamat típusának kiválasztásához
3. Az új munkafolyamat megjelenik a munkafolyamatok listájában

#### Munkafolyamat Végrehajtása

1. Keresse meg a futtatni kívánt munkafolyamatot a munkafolyamatok listájában
2. Kattintson a lejátszás gombra (▶) a munkafolyamat mellett
3. A munkafolyamat végrehajtásra kerül az aktuális fájlon vagy kijelölésen

#### Munkafolyamat Törlése

1. Keresse meg a törölni kívánt munkafolyamatot a munkafolyamatok listájában
2. Kattintson a "✕" gombra a munkafolyamat mellett
3. Erősítse meg a törlést, amikor a rendszer kéri

### Eszközök Használata

A Project-S oldalsáv gyors hozzáférést biztosít a gyakori eszközökhöz:

#### Kódelemzés

1. Válassza ki az elemezni kívánt kódot vagy helyezze a kurzort egy fájlba
2. Kattintson az "Analyze Code" gombra az oldalsávban
3. Tekintse meg az elemzési eredményeket a kimeneti panelen

#### Kódgenerálás

1. Helyezze a kurzort oda, ahova a generált kódot szeretné beszúrni
2. Kattintson a "Generate Code" gombra az oldalsávban
3. Kövesse az utasításokat, hogy meghatározza, milyen kódot szeretne generálni
4. A generált kód beszúrásra kerül a kurzor pozíciójába

#### Kóddokumentáció

1. Válassza ki a dokumentálni kívánt kódot vagy helyezze a kurzort egy fájlba
2. Kattintson a "Document Code" gombra az oldalsávban
3. A dokumentáció generálásra és kommentekként beszúrásra kerül

## Hibaelhárítás

### Kapcsolódási Problémák

Ha nem tud kapcsolódni a Project-S szerverhez:

1. Ellenőrizze, hogy a beállításokban szereplő szerver URL helyes-e
2. Ellenőrizze, hogy a szerver fut és elérhető-e
3. Győződjön meg arról, hogy az API kulcs érvényes
4. Ellenőrizze, hogy nincsenek-e hálózati problémák vagy tűzfalak, amelyek blokkolják a kapcsolatot

### A Kiterjesztés Nem Működik

Ha a kiterjesztés nem működik megfelelően:

1. Indítsa újra a VSCode-ot
2. Ellenőrizze a Kimenet panelt (Nézet > Kimenet) és válassza a "Project-S" opciót a legördülő menüből
3. Keressen hibaüzeneteket a naplóban
4. Próbálja újratelepíteni a kiterjesztést

## Támogatás

További segítségért:

- Küldjön be problémákat a [GitHub repository-nkban](https://github.com/organization/project-s-vscode-extension/issues)
- Vegye fel a kapcsolatot a támogatással a support@project-s.example.com címen
- Ellenőrizze a [dokumentációs webhelyet](https://docs.project-s.example.com) a részletes útmutatókért
