# Project-S Agent

## Áttekintés

A Project-S egy moduláris, eseményvezérelt AI agent rendszer, amely különböző típusú parancsokat képes feldolgozni és végrehajtani. A rendszer célja, hogy intelligens, önálló internetes interakcióra képes agentet hozzon létre, amely képes a különböző AI modellek (mint a Qwen3, Claude, ChatGPT) képességeinek kombinálására.

## Főbb funkciók

- **Eseményvezérelt architektúra**: A komponensek közötti laza csatolás és rugalmas kommunikáció
- **Kognitív mag**: A rendszer "agya", amely kontextust tart fenn, feladatokat tervez és tanul
- **VS Code integráció**: Közvetlen kód generálás és végrehajtás a VS Code-ban
- **DOM-alapú kommunikáció**: Lehetővé teszi a böngészőből érkező parancsok feldolgozását
- **Plugin rendszer**: Könnyen bővíthető új képességekkel

## Komponensek

- **CentralExecutor**: A parancsok végrehajtásáért felelős központi komponens
- **CognitiveCore**: A rendszer "agya", amely fenntartja a kontextust és tervezi a feladatokat
- **EventBus**: Az eseményvezérelt kommunikációt lehetővé tevő komponens
- **DOMListener**: A böngészőből érkező parancsok kezeléséért felelős komponens
- **VSCodeInterface**: A VS Code integrációért felelős komponens

## Kezdeti lépések

### Telepítés

```bash
# Klónozza a repository-t
git clone https://github.com/toti85/project-s-agent.git
cd project-s-agent

# Telepítse a függőségeket
pip install -r requirements.txt
```