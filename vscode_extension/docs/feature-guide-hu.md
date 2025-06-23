# Project-S VSCode Kiterjesztés Funkció Útmutató

Ez a dokumentum részletes információkat tartalmaz a Project-S VSCode kiterjesztés minden funkciójának használatáról. Ismerje meg, hogyan használhatja hatékonyan a kódelemzést, kódgenerálást, dokumentációt és a LangGraph munkafolyamatokat.

## Kódelemzési Funkciók

A kódelemzési funkciók segítenek megérteni, optimalizálni és javítani a kódbázist.

### Alapvető Kódelemzés

**Célja:** Kódminőség, struktúra és potenciális problémák elemzése.

**Használata:**
1. Nyisson meg egy elemezni kívánt fájlt
2. Válassza ki az elemezni kívánt kódot (vagy a teljes fájlt)
3. Kattintson az "Analyze Code" gombra az oldalsávban
4. Tekintse át az elemzés eredményét a kimeneti panelen

**Példa felhasználási esetek:**
- Kódszagok és antiminták azonosítása
- Potenciális teljesítmény szűkkeresztmetszetek megtalálása
- Komplex kódstruktúra megértése

### Speciális Elemzési Beállítások

Célzottabb elemzéshez használja a parancs palettát:

1. Nyomja meg a `Ctrl+Shift+P` (Windows/Linux) vagy `Cmd+Shift+P` (Mac) billentyűket
2. Írja be: "Project-S: Advanced Analysis"
3. Válasszon az alábbi lehetőségek közül:
   - Biztonsági elemzés
   - Teljesítmény elemzés
   - Architektúra elemzés
   - Függőségi elemzés

## Kódgenerálási Funkciók

Kiváló minőségű kódrészletek és teljes funkciók generálása a kódgenerálási funkciókkal.

### Alapvető Kódgenerálás

**Célja:** Kód generálása természetes nyelvi leírások vagy meglévő minták alapján.

**Használata:**
1. Helyezze a kurzort oda, ahova a generált kódot szeretné beszúrni
2. Kattintson a "Generate Code" gombra az oldalsávban
3. Írja le, mit szeretne generálni a beviteli promptban
4. Tekintse át és fogadja el a generált kódot

**Példa felhasználási esetek:**
- Boilerplate kód létrehozása
- Interfészek implementálása
- Tesztesetek írása
- Programozási nyelvek közötti konverzió

### Kontextuális Kódgenerálás

A kiterjesztés képes megérteni a projekt kontextusát az intelligensebb generáláshoz:

1. Válasszon ki meglévő kódot kontextusként
2. Nyomja meg a `Ctrl+Shift+P` (Windows/Linux) vagy `Cmd+Shift+P` (Mac) billentyűket
3. Írja be: "Project-S: Contextual Generate"
4. Írja le, mit szeretne generálni a kiválasztott kóddal kapcsolatban

## Dokumentációs Funkciók

Automatikusan generáljon és tartson karban kóddokumentációt ezekkel a funkciókkal.

### Kóddokumentáció

**Célja:** Dokumentáció létrehozása vagy frissítése függvényekhez, osztályokhoz és modulokhoz.

**Használata:**
1. Válassza ki a dokumentálni kívánt kódot
2. Kattintson a "Document Code" gombra az oldalsávban
3. A dokumentáció kommentként kerül beszúrásra a kiválasztott kód fölé

**Példa felhasználási esetek:**
- JSDoc/PyDoc kommentek hozzáadása függvényekhez
- README fájlok generálása
- API dokumentáció készítése

### Dokumentációs Beállítások

A dokumentációs stílus magasabb szintű vezérléséhez:

1. Nyomja meg a `Ctrl+Shift+P` (Windows/Linux) vagy `Cmd+Shift+P` (Mac) billentyűket
2. Írja be: "Project-S: Document Options"
3. Válasszon az alábbi lehetőségek közül:
   - Dokumentációs stílus (JSDoc, PyDoc, stb.)
   - Részletességi szint (rövid, részletes, átfogó)
   - Példák beszúrása (igen/nem)

## LangGraph Munkafolyamatok Használata

A LangGraph munkafolyamatok lehetővé teszik komplex, többlépcsős AI műveletek létrehozását a kódon.

### Munkafolyamatok Létrehozása

**Célja:** Egyéni műveletsorozatok definiálása az Ön specifikus igényeihez.

**Használata:**
1. Kattintson a "+" gombra a Munkafolyamatok szekció fejlécében
2. Adja meg a munkafolyamat nevét
3. Válasszon egy munkafolyamat típust vagy sablont
4. Konfigurálja a munkafolyamat csomópontokat és kapcsolatokat
5. Mentse a munkafolyamatot

**Példa munkafolyamat típusok:**
- Kód felülvizsgálati munkafolyamat
- Refaktorálási munkafolyamat
- Hibajavítási munkafolyamat
- Funkció implementációs munkafolyamat

### Munkafolyamatok Végrehajtása

**Célja:** Munkafolyamatok futtatása kiválasztott kódon vagy fájlokon.

**Használata:**
1. Keresse meg a munkafolyamatot a munkafolyamatok listájában
2. Kattintson a lejátszás gombra (▶) a munkafolyamat mellett
3. Ha kérdezi, válassza ki a feldolgozandó kódot vagy fájlokat
4. Kövesse a munkafolyamat által megkövetelt interaktív lépéseket
5. Tekintse át az eredményeket

### Egyéni Munkafolyamat Fejlesztés

Haladó felhasználók számára, akik egyéni munkafolyamatokat szeretnének létrehozni:

1. Férjen hozzá a munkafolyamat szerkesztőhöz a parancs palettán keresztül:
   - Nyomja meg a `Ctrl+Shift+P` (Windows/Linux) vagy `Cmd+Shift+P` (Mac) billentyűket
   - Írja be: "Project-S: Edit Workflow"
2. Használja a grafikus szerkesztőt a következőkre:
   - Csomópontok hozzáadása és összekötése
   - Csomópontok paramétereinek konfigurálása
   - Bemenet/kimenet leképezések beállítása
3. Tesztelje és finomítsa a munkafolyamatot
4. Ossza meg a munkafolyamatokat a csapatával

## Valós idejű Együttműködés

A Project-S kiterjesztés támogatja a valós idejű együttműködést másokkal.

### Elemzési Eredmények Megosztása

**Célja:** Együttműködés a csapattagokkal a kódelemzésben.

**Használata:**
1. Futtasson egy elemzést a kódon
2. A kimeneti panelen kattintson a "Share Results" gombra
3. Válassza ki a megosztási lehetőségeket (csapattagok, csatornák)
4. Adjon hozzá opcionális megjegyzéseket
5. Kattintson a "Share" gombra

### Együttműködő Munkafolyamatok

**Célja:** Együtt dolgozni csapattagokkal összetett feladatokon.

**Használata:**
1. Hozzon létre vagy válasszon ki egy munkafolyamatot
2. Kattintson a "Collaborate" gombra
3. Hívja meg a csapattagokat
4. Rendeljen lépéseket különböző csapattagokhoz
5. Kövesse nyomon a folyamatot és kommunikáljon a beépített csevegésen keresztül

## Billentyűparancsok

Gyorsabb működéshez használja ezeket a billentyűparancsokat:

- `Ctrl+Alt+A` (Windows/Linux) vagy `Cmd+Alt+A` (Mac): Aktuális fájl elemzése
- `Ctrl+Alt+G` (Windows/Linux) vagy `Cmd+Alt+G` (Mac): Kód generálása a kurzor pozíciójában
- `Ctrl+Alt+D` (Windows/Linux) vagy `Cmd+Alt+D` (Mac): Kiválasztott kód dokumentálása
- `Ctrl+Alt+W` (Windows/Linux) vagy `Cmd+Alt+W` (Mac): Munkafolyamat panel megjelenítése
- `Ctrl+Alt+R` (Windows/Linux) vagy `Cmd+Alt+R` (Mac): Utolsó munkafolyamat futtatása

Ezeket a billentyűparancsokat testreszabhatja a VSCode billentyűparancs beállításaiban.

## Legjobb Gyakorlatok

A Project-S kiterjesztés legjobb kihasználása érdekében:

1. **Kezdjen kicsivel:** Kezdje egyszerű elemzésekkel és generálásokkal, mielőtt összetett munkafolyamatokra térne át
2. **Használjon kontextust:** Válasszon ki releváns kódot az eszközök futtatása előtt a jobb eredményekért
3. **Iteráljon:** Finomítsa a generált kódot és dokumentációt ahelyett, hogy tökéletes eredményeket várna azonnal
4. **Kombinálja az eszközöket:** Használja az elemzési eredményeket a kódgenerálási kérések megfogalmazásához
5. **Mentsen munkafolyamatokat:** Hozzon létre és mentsen munkafolyamatokat ismétlődő feladatokhoz
6. **Adjon visszajelzést:** Használja a visszajelzési mechanizmusokat az AI modellek fejlesztésének segítésére
