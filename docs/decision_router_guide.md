# Hibrid Rendszer Döntéshozatali Logikája

Ez a dokumentum a Project-S rendszer hibrid döntéshozatali logikáját ismerteti, amely a LangGraph keretrendszert használja.

## Áttekintés

A döntéshozatali rendszer három fő komponensből áll:

1. **Alap Döntési Router** (`decision_router.py`) - Alapvető döntéshozatali logikát biztosít a munkafolyamatok irányításához
2. **Fejlett Döntési Router** (`advanced_decision_router.py`) - Kiterjesztett funkcionalitást ad adaptív döntéshozatallal és mintafelismeréssel
3. **Kognitív Döntési Integráció** (`cognitive_decision_integration.py`) - Összeköti a döntéshozatali rendszert a kognitív maggal

Ezek a komponensek együttesen biztosítják a rugalmas, adaptív döntéshozatalt, amely képes különböző kritériumok alapján dönteni, és integrálódik a Project-S eseménykezelő rendszerével.

## Fő funkciók

### 1. Rugalmas Router Funkció

A rendszer rugalmas router funkciókat biztosít, amelyek irányítják a munkafolyamatot a különböző komponensek között:

```python
# Döntési csomópont létrehozása
decision_router.add_decision_node(
    graph=graph,
    node_name="content_type_decision",
    criteria_func=input_type_router,  # Ez a függvény határozza meg a döntési kritériumot
    destinations={
        "text": "process_text",  # Célcsomópontok a különböző döntési értékekhez
        "code": "process_code"
    },
    default="process_text"  # Alapértelmezett célcsomópont
)
```

### 2. Feltételes Élek a LangGraph Gráfban

A rendszer automatikusan létrehozza a megfelelő feltételes éleket a LangGraph gráfban:

```python
# Feltételes él létrehozása a döntési kritérium alapján
graph.add_conditional_edges(
    node_name,                   # Forrás csomópont
    condition_func,              # Feltétel-függvény
    conditional_map              # Érték -> célcsomópont leképezés
)
```

### 3. Integráció a Project-S Event Bus Rendszerével

A döntéshozatali rendszer eseményeket publikál és fogad, ezáltal integrálódik a Project-S eseménykezelő rendszerével:

```python
# Esemény publikálása a döntésről
await event_bus.publish("workflow.decision.made", {
    "graph_id": graph_id,
    "decision_id": decision_id,
    "source_node": name,
    "decision": next_node,
    "criterion_value": str(result),
    "options": list(options.keys()),
    "timestamp": asyncio.get_event_loop().time()
})
```

### 4. Dinamikus Döntéshozatali Kritériumok

A rendszer támogatja a dinamikus, kontextus-függő döntéshozatali kritériumokat:

```python
# Adaptív döntési csomópont többféle kritérium-forrással
advanced_decision_router.add_adaptive_decision_node(
    graph=graph,
    node_name="complex_decision",
    criteria_sources=[
        {"type": "function", "name": "registered_criteria"},  # Regisztrált kritérium-függvény
        {"type": "path", "path": "context.some_value"},      # Érték a gráf állapotából
        {"type": "cognitive", "question": "Döntési kérdés"}  # Kognitív rendszerre bízott döntés
    ],
    destinations={...},
    fallback="default_destination"
)
```

### 5. Döntéshozatal Naplózása és Elemzése

A rendszer naplózza a döntéseket és lehetővé teszi azok elemzését:

```python
# Döntéstörténet lekérése
decision_history = decision_router.get_decision_history(graph_id)

# Döntési minták felismerése
patterns = advanced_decision_router.detect_decision_patterns(graph_id)

# Globális döntési trendek elemzése
trends = advanced_decision_router.analyze_global_decision_trends()
```

## Döntési Kritériumok

A döntési kritériumok olyan függvények, amelyek a munkafolyamat állapota alapján meghatározzák, hogy melyik úton haladjon tovább a folyamat:

```python
def route_by_content_type(state: GraphState) -> str:
    """Bemenet típusa alapján dönt."""
    content_type = state["context"].get("content_type", "")
    
    if "code" in content_type.lower():
        return "code"
    elif "image" in content_type.lower():
        return "image"
    else:
        return "text"
```

A kritérium-függvények regisztrálhatók, hogy később név szerint hivatkozni lehessen rájuk:

```python
# Kritérium regisztrálása
advanced_decision_router.register_decision_criteria(
    "content_type_check", route_by_content_type
)
```

## Kognitív Döntéshozatal

A kognitív integrációval a rendszer képes összetett kérdéseket feltéve döntéseket hozni:

```python
# Kognitív döntési csomópont létrehozása
cognitive_decision_integration.add_cognitive_decision_node(
    graph=graph,
    node_name="complex_decision",
    question="A bemeneti adatok alapján milyen folyamatot futtassunk?",
    options={
        "process_a": "node_a",
        "process_b": "node_b",
        "process_c": "node_c"
    },
    context_keys=["input_data", "user_preference"]
)
```

## Hibrid Döntéshozatal

A rendszer lehetőséget nyújt hibrid döntéshozatalra, ahol először egy egyszerű kritérium-függvény próbálkozik, és csak ha az nem tud dönteni, akkor kerül sor a kognitív rendszerre:

```python
# Hibrid döntési csomópont létrehozása
cognitive_decision_integration.combine_with_advanced_router(
    graph=graph,
    node_name="hybrid_decision",
    question="A következő lépés meghatározása az adatok alapján",
    decision_criteria=simple_criteria_function,
    options={
        "option_a": "node_a",
        "option_b": "node_b"
    },
    default_option="option_a"
)
```

## Példa Munkafolyamat

Az alábbi példa egy egyszerű döntési munkafolyamatot mutat be:

```python
async def create_decision_workflow():
    """Munkafolyamat létrehozása döntési logikával."""
    # Új gráf létrehozása
    graph = StateGraph(GraphState)
    
    # Csomópontok hozzáadása
    graph.add_node("start", start_node)
    graph.add_node("process_text", process_text_node)
    graph.add_node("process_code", process_code_node)
    graph.add_node("quality_check", quality_check_node)
    graph.add_node("enhance_content", enhance_content_node)
    graph.add_node("finalize", final_node)
    
    # Döntési csomópontok hozzáadása
    decision_router.add_decision_node(
        graph=graph,
        node_name="content_type_decision",
        criteria_func=input_type_router,
        destinations={
            "text": "process_text",
            "code": "process_code"
        },
        default="process_text"
    )
    
    decision_router.add_decision_node(
        graph=graph,
        node_name="quality_decision",
        criteria_func=quality_check_router,
        destinations={
            "passed": "finalize",
            "failed": "enhance_content"
        },
        default="enhance_content"
    )
    
    # Élek hozzáadása
    graph.add_edge("start", "content_type_decision")
    graph.add_edge("process_text", "quality_check")
    graph.add_edge("process_code", "quality_check")
    graph.add_edge("quality_check", "quality_decision")
    graph.add_edge("enhance_content", "finalize")
    
    # Belépési pont beállítása
    graph.set_entry_point("start")
    
    # Gráf fordítása
    return graph.compile()
```

## Események

A döntéshozatali rendszer a következő eseményeket publikálja az eseménybuszon:

- `workflow.decision.made` - Amikor egy döntés megszületik
- `workflow.decision.provided` - Amikor a kognitív rendszer döntést hoz
- `workflow.cognitive_decision.made` - Amikor kognitív döntés született
- `workflow.hybrid_decision.made` - Amikor hibrid döntés született
- `workflow.pattern_detected` - Amikor mintát ismer fel a rendszer

## Összefoglalás

A hibrid döntéshozatali rendszer rugalmas és adaptív irányítást biztosít a Project-S rendszer munkafolyamatai számára. Az egyszerű kritérium-alapú döntésektől a komplex, kognitív rendszer által támogatott döntésekig különböző szintű döntéshozatalt tesz lehetővé, miközben teljes integrációt biztosít a Project-S eseménykezelő rendszerével, és részletes naplózást, elemzést nyújt a döntésekről.
