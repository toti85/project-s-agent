# Project-S Architektúra

## Áttekintés

A Project-S egy moduláris, eseményvezérelt AI agent rendszer, amely különböző típusú parancsokat képes feldolgozni és végrehajtani. Az architektúra célja a rugalmasság, a bővíthetőség és a skálázhatóság biztosítása.

## Főbb komponensek

### CentralExecutor
A CentralExecutor felelős a parancsok végrehajtásáért. Ez a komponens koordinálja a különböző modulok közötti interakciókat, és biztosítja a feladatok megfelelő végrehajtását.

### CognitiveCore
A CognitiveCore a rendszer "agya". Ez a modul tartja fenn a kontextust, tervezi a feladatokat, és tanul az előző interakciókból. A kognitív mag képes komplex feladatok végrehajtására és a rendszer intelligenciájának növelésére.

### EventBus
Az EventBus egy eseményvezérelt kommunikációs rendszer, amely lehetővé teszi a modulok közötti laza csatolást. Az események segítségével a komponensek aszinkron módon kommunikálhatnak egymással.

### DOMListener
A DOMListener a böngészőből érkező parancsok kezeléséért felelős. Ez a modul lehetővé teszi a rendszer számára, hogy webes interakciókat hajtson végre és DOM-alapú eseményeket dolgozzon fel.

### VSCodeInterface
A VSCodeInterface a rendszer és a Visual Studio Code közötti integrációt biztosítja. Ez a modul lehetővé teszi a kód generálását, mentését és végrehajtását közvetlenül a VS Code környezetében.

## Moduláris felépítés

A rendszer moduláris felépítése lehetővé teszi az egyes komponensek független fejlesztését és tesztelését. Az alábbi diagram bemutatja a főbb komponensek közötti kapcsolatokat:

```
+----------------+       +----------------+
|  DOMListener   |<----->|   EventBus     |
+----------------+       +----------------+
        |                        |
        v                        v
+----------------+       +----------------+
| VSCodeInterface|<----->| CognitiveCore  |
+----------------+       +----------------+
        |                        |
        v                        v
+--------------------------------+
|         CentralExecutor        |
+--------------------------------+
```

## Eseményvezérelt architektúra

Az eseményvezérelt architektúra lehetővé teszi a komponensek közötti laza csatolást és a rugalmas kommunikációt. Az EventBus segítségével a modulok aszinkron módon küldhetnek és fogadhatnak eseményeket, ami növeli a rendszer skálázhatóságát és megbízhatóságát.