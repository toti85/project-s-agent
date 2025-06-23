
        # Project-S Felhasználói Felület Tesztelési Útmutató
        
        Ez az útmutató segít a Project-S felhasználói felületének manuális tesztelésében.
        
        ## Alapvető funkciók tesztelése
        
        1. **Parancs bevitel**
           - Nyisd meg a felhasználói felületet
           - Írj be egy egyszerű parancsot a beviteli mezőbe: "Írj egy 'Hello, Project-S!' üzenetet"
           - Ellenőrizd, hogy a válasz megfelelően jelenik meg
        
        2. **Korábbi parancsok megjelenítése**
           - Ellenőrizd, hogy a korábban beírt parancsok láthatóak-e
           - Próbáld meg újra elküldeni valamelyik korábbi parancsot
        
        3. **Munkafolyamat állapotának megjelenítése**
           - Készíts egy többlépéses munkafolyamatot: "Hozz létre egy listát 3 országról, add meg a fővárosaikat, majd mentsd el egy countries.txt fájlba"
           - Ellenőrizd, hogy a munkafolyamat állapota megfelelően jelenik-e meg
        
        4. **Eszközök használata**
           - Teszteld az elérhető eszközöket: "Mutasd meg, milyen eszközöket tudsz használni"
           - Próbálj ki egy konkrét eszközt, pl. "Listázd a jelenlegi könyvtár tartalmát"
        
        5. **Hosszú válaszok megjelenítése**
           - Kérj egy hosszabb választ: "Írj egy 500 szavas esszét a mesterséges intelligenciáról"
           - Ellenőrizd, hogy a hosszú válasz megfelelően jelenik-e meg (görgetés, formázás)
        
        6. **Munkamenetek kezelése**
           - Próbálj új munkamenetet létrehozni
           - Váltogass a munkamenetek között
           - Ellenőrizd, hogy a munkamenetek között megmarad-e a kontextus
           
        ## Hibaesetek tesztelése
        
        1. **Hálózati hiba**
           - Kapcsold ki ideiglenesen az internetkapcsolatot
           - Küldj egy parancsot
           - Ellenőrizd, hogy a rendszer megfelelően kezeli-e a hálózati hibát
        
        2. **Hosszú feldolgozási idő**
           - Küldj egy bonyolult parancsot, ami várhatóan hosszabb feldolgozási időt igényel
           - Ellenőrizd, hogy van-e folyamatjelző vagy visszajelzés
        
        ## Teljesítmény tesztelése
        
        1. **Válaszidők**
           - Mérd meg, mennyi ideig tart egy egyszerű parancs feldolgozása
           - Mérd meg egy összetettebb parancs feldolgozási idejét
        
        2. **Böngészőterhelés**
           - Figyeld meg a CPU és memóriahasználatot hosszú interakciók során
           
        ## Mobilkompatibilitás (ha releváns)
        
        1. **Reszponzív megjelenés**
           - Nyisd meg a felületet különböző képernyőméreteken (mobil, tablet, desktop)
           - Ellenőrizd, hogy minden funkció elérhető és használható-e
        