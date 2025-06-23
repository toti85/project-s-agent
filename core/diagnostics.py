"""
Project-S + LangGraph Hibrid Rendszer - Diagnosztikai Modul
----------------------------------------------------------
Ez a modul átfogó diagnosztikai és hibakeresési képességeket biztosít a Project-S + LangGraph hibrid rendszerhez.
Magában foglalja a részletes naplózást, teljesítmény monitorozást, hibajelentést és értesítési mechanizmusokat.
"""

import os
import logging
import logging.config
import time
import json
import traceback
import socket
import psutil
import threading
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Union, Callable
from pathlib import Path

# Próbáljuk importálni a vizualizációs könyvtárakat - ha nem sikerül, akkor is működik a modul
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from rich.logging import RichHandler
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Alapvető konstansok
DEFAULT_LOG_DIR = "logs"
DEFAULT_DIAGNOSTICS_DIR = "diagnostics"
MAX_ERROR_HISTORY = 100
ALERT_COOLDOWN_SECONDS = 300  # 5 perc ugyanazon típusú riasztás között

# Naplózási szintek és típusok
class LogLevel(Enum):
    """Naplózási szintek"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

class AlertLevel(Enum):
    """Figyelmeztetések súlyossága"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

# Hibajelentés és diagnosztikai adatszerkezetek
@dataclass
class ErrorContext:
    """Hiba kontextus részletes információkkal"""
    error_type: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    traceback: Optional[str] = None
    component: Optional[str] = None
    workflow_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    related_errors: List[str] = field(default_factory=list)
    additional_info: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertálja a hibakontextust szótárrá"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result

@dataclass
class PerformanceMetrics:
    """Teljesítmény méréseket tartalmazó osztály"""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_mb: float = 0.0
    threads_count: int = 0
    open_file_descriptors: int = 0
    process_uptime_seconds: float = 0.0
    event_processing_rate: float = 0.0  # események / másodperc
    response_times_ms: Dict[str, float] = field(default_factory=dict)
    graph_processing_times_ms: Dict[str, float] = field(default_factory=dict)
    active_workflows: int = 0
    pending_workflows: int = 0
    completed_workflows: int = 0
    failed_workflows: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertálja a metrikákat szótárrá"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result

@dataclass
class Alert:
    """Riasztás osztály"""
    level: AlertLevel
    message: str
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    alert_id: str = None
    
    def __post_init__(self):
        if not self.alert_id:
            # Egyedi azonosító generálása a riasztáshoz
            self.alert_id = f"{self.source}_{self.level.value}_{int(time.time())}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertálja a riasztást szótárrá"""
        result = asdict(self)
        result['level'] = self.level.value
        result['timestamp'] = self.timestamp.isoformat()
        return result

# Fő diagnosztikai osztály
class DiagnosticsManager:
    """
    Központi diagnosztikai menedzser osztály a Project-S + LangGraph hibrid rendszerhez.
    
    Funkciók:
    - Részletes, konfigurálható naplózás
    - Teljesítmény metrikák gyűjtése és vizualizálása
    - Hibakövetés és kontextus gyűjtés
    - Riasztási rendszer kritikus hibákhoz
    - Diagnosztikai jelentések generálása
    - Munkafolyamat vizualizáció
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """Singleton minta - mindig ugyanazt a példányt adjuk vissza"""
        if cls._instance is None:
            cls._instance = super(DiagnosticsManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None, 
                log_dir: str = DEFAULT_LOG_DIR, 
                diagnostics_dir: str = DEFAULT_DIAGNOSTICS_DIR,
                enable_console: bool = True,
                default_log_level: LogLevel = LogLevel.INFO,
                enable_performance_monitoring: bool = True,
                monitoring_interval_seconds: int = 60,
                enable_alerts: bool = True):
        """
        Inicializálja a diagnosztikai menedzsert
        
        Args:
            config_path: Opcionális útvonal a részletes naplózási konfigurációhoz (YAML vagy JSON)
            log_dir: A napló fájlok könyvtára
            diagnostics_dir: A diagnosztikai kimenetek könyvtára
            enable_console: Konzolra is legyen kiírva a napló
            default_log_level: Alapértelmezett naplózási szint
            enable_performance_monitoring: Teljesítmény monitorozás bekapcsolása
            monitoring_interval_seconds: Teljesítmény mérések közötti idő másodpercben
            enable_alerts: Riasztások bekapcsolása
        """
        # Csak egyszer inicializáljuk
        if self._initialized:
            return
            
        self.log_dir = log_dir
        self.diagnostics_dir = diagnostics_dir
        self.enable_console = enable_console
        self.default_log_level = default_log_level
        self.enable_performance_monitoring = enable_performance_monitoring
        self.monitoring_interval_seconds = monitoring_interval_seconds
        self.enable_alerts = enable_alerts
        
        # Adattárolók inicializálása
        self.error_history: List[ErrorContext] = []
        self.performance_history: List[PerformanceMetrics] = []
        self.alert_history: List[Alert] = []
        self.alert_cooldowns: Dict[str, datetime] = {}  # alert_type -> utolsó riasztás ideje
        
        # Könyvtárak létrehozása, ha szükséges
        os.makedirs(log_dir, exist_ok=True)
        os.makedirs(diagnostics_dir, exist_ok=True)
        os.makedirs(os.path.join(diagnostics_dir, "graphs"), exist_ok=True)
        os.makedirs(os.path.join(diagnostics_dir, "reports"), exist_ok=True)
        os.makedirs(os.path.join(diagnostics_dir, "errors"), exist_ok=True)
        
        # Naplózás beállítása
        self._setup_logging(config_path)
        
        # Létrehozzuk a loggert
        self.logger = logging.getLogger("project_s.diagnostics")
        self.logger.info("Diagnosztikai menedzser inicializálva")
        
        # Indítási idő rögzítése
        self.start_time = time.time()
        
        # Teljesítmény monitorozó szál indítása, ha engedélyezve van
        if enable_performance_monitoring:
            self._start_performance_monitoring()
        
        # Sikeres inicializálás jelzése
        self._initialized = True
    
    def _setup_logging(self, config_path: Optional[str] = None) -> None:
        """
        Beállítja a naplózási rendszert
        
        Args:
            config_path: Opcionális konfigurációs fájl útvonala
        """
        # Ha van konfigurációs fájl, azt használjuk
        if config_path and os.path.exists(config_path):
            if config_path.endswith('.json'):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logging.config.dictConfig(config)
            elif config_path.endswith(('.yaml', '.yml')):
                import yaml  # Lazy import
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                logging.config.dictConfig(config)
        # Egyébként alapértelmezett konfigurációt használunk
        else:
            # Alapvető formátum
            log_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            date_format = '%Y-%m-%d %H:%M:%S'
            
            # Handler-ek létrehozása
            handlers = {}
            
            # Fájl handler minden szinthez
            file_handler = logging.FileHandler(
                os.path.join(self.log_dir, 'project_s_full.log'),
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(log_format, date_format)
            file_handler.setFormatter(file_formatter)
            handlers['file'] = file_handler
            
            # Külön fájl a hibáknak
            error_handler = logging.FileHandler(
                os.path.join(self.log_dir, 'project_s_errors.log'),
                encoding='utf-8'
            )
            error_handler.setLevel(logging.WARNING)
            error_handler.setFormatter(file_formatter)
            handlers['error_file'] = error_handler
            
            # Konzol handler, ha engedélyezve van
            if self.enable_console:
                if RICH_AVAILABLE:
                    console_handler = RichHandler(rich_tracebacks=True)
                    console_format = '%(message)s'
                    console_formatter = logging.Formatter(console_format)
                else:
                    console_handler = logging.StreamHandler()
                    console_formatter = file_formatter
                
                console_handler.setLevel(self.default_log_level.value)
                console_handler.setFormatter(console_formatter)
                handlers['console'] = console_handler
            
            # Konfiguráció alkalmazása
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.DEBUG)
            
            # Meglévő handlerek törlése (hogy ne legyen duplikáció)
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            
            # Új handlerek hozzáadása
            for handler in handlers.values():
                root_logger.addHandler(handler)
    
    def _start_performance_monitoring(self) -> None:
        """Elindítja a teljesítmény monitorozó háttérszálat"""
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(
            target=self._performance_monitoring_loop,
            daemon=True,
            name="perf-monitor"
        )
        self._monitoring_thread.start()
        self.logger.info(f"Teljesítmény monitorozás elindítva ({self.monitoring_interval_seconds} másodpercenkénti mintavétellel)")
    
    def _performance_monitoring_loop(self) -> None:
        """Háttérszál a teljesítmény metrikák rendszeres gyűjtésére"""
        process = psutil.Process()
        while self._monitoring_active:
            try:
                # Rendszer metrikák gyűjtése
                metrics = PerformanceMetrics(
                    cpu_percent=process.cpu_percent(),
                    memory_percent=process.memory_percent(),
                    memory_used_mb=process.memory_info().rss / (1024 * 1024),
                    threads_count=process.num_threads(),
                    open_file_descriptors=len(process.open_files()),
                    process_uptime_seconds=time.time() - self.start_time
                )
                
                # Metrikák tárolása
                self.performance_history.append(metrics)
                
                # Limitáljuk a tárolt metrikák számát (utolsó 24 óra, percenkénti mintavétellel)
                max_samples = 24 * 60 * 60 // self.monitoring_interval_seconds
                if len(self.performance_history) > max_samples:
                    self.performance_history = self.performance_history[-max_samples:]
                
                # Ellenőrizzük a kritikus határértékeket, és küldünk riasztást, ha kell
                if metrics.cpu_percent > 80:
                    self.send_alert(
                        level=AlertLevel.WARNING,
                        message=f"Magas CPU használat: {metrics.cpu_percent:.1f}%",
                        source="performance_monitor",
                        details={"cpu_percent": metrics.cpu_percent}                    )
                
                if metrics.memory_percent > 80:
                    self.send_alert(
                        level=AlertLevel.WARNING,
                        message=f"Magas memória használat: {metrics.memory_percent:.1f}%",
                        source="performance_monitor",
                        details={"memory_percent": metrics.memory_percent}
                    )
                
            except Exception as e:
                self.logger.error(f"Hiba a teljesítmény monitorozás közben: {e}")
                
            # Várunk a következő mintavételig
            time.sleep(self.monitoring_interval_seconds)
    
    def stop_performance_monitoring(self) -> None:
        """Leállítja a teljesítmény monitorozást"""
        if hasattr(self, '_monitoring_active'):
            self._monitoring_active = False
            if hasattr(self, '_monitoring_thread'):
                self._monitoring_thread.join(timeout=1.0)
            self.logger.info("Teljesítmény monitorozás leállítva")

    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """
        Visszaadja a legfrissebb teljesítmény metrikákat
        
        Returns:
            PerformanceMetrics: A legfrissebb metrikák vagy None, ha nincsenek
        """
        if self.performance_history:
            return self.performance_history[-1]
        return None

    def get_uptime_seconds(self) -> float:
        """
        Visszaadja a rendszer üzemidejét másodpercekben
        
        Returns:
            float: Az üzemidő másodpercekben
        """
        return time.time() - self.start_time
    
    def register_error(self, error: Exception, component: Optional[str] = None,
                     workflow_id: Optional[str] = None, additional_info: Optional[Dict[str, Any]] = None,
                     alert_level: Optional[AlertLevel] = None) -> ErrorContext:
        """
        Regisztrál egy hibát a diagnosztikai rendszerben
        
        Args:
            error: A kivétel objektum
            component: A komponens neve, ahol a hiba történt
            workflow_id: Opcionális munkafolyamat azonosító
            additional_info: Bármilyen további információ a hibáról
            alert_level: Ha meg van adva, riasztást is küld a megadott szinten
        
        Returns:
            ErrorContext: A létrehozott hibakontextus objektum
        """
        error_type = type(error).__name__
        error_message = str(error)
        error_traceback = traceback.format_exc()
        
        # Hibakontextus létrehozása
        error_context = ErrorContext(
            error_type=error_type,
            message=error_message,
            traceback=error_traceback,
            component=component,
            workflow_id=workflow_id,
            additional_info=additional_info or {}
        )
        
        # Hozzáadás a hibaelőzményekhez
        self.error_history.append(error_context)
        
        # Limitáljuk a tárolt hibák számát
        if len(self.error_history) > MAX_ERROR_HISTORY:
            self.error_history = self.error_history[-MAX_ERROR_HISTORY:]
        
        # Napló bejegyzés
        self.logger.error(
            f"Hiba a(z) {component or 'ismeretlen'} komponensben: {error_message}", 
            exc_info=error
        )
        
        # Hibafájl létrehozása
        self._save_error_details(error_context)
        
        # Riasztás küldése, ha kérték
        if alert_level:
            self.send_alert(
                level=alert_level,
                message=f"Hiba a(z) {component or 'ismeretlen'} komponensben: {error_message}",
                source=component or "unknown",
                details={"error_context": error_context.to_dict()}
            )
        
        return error_context
    
    def _save_error_details(self, error_context: ErrorContext) -> None:
        """
        Elmenti a részletes hibaadatokat egy JSON fájlba
        
        Args:
            error_context: A hibakontextus objektum
        """
        try:
            timestamp_str = error_context.timestamp.strftime("%Y%m%d_%H%M%S")
            component_name = error_context.component or "unknown"
            filename = f"error_{timestamp_str}_{component_name}_{error_context.error_type}.json"
            filepath = os.path.join(self.diagnostics_dir, "errors", filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(error_context.to_dict(), f, indent=2)
                
            self.logger.debug(f"Hiba részletei elmentve: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Nem sikerült menteni a hiba részleteit: {e}")
    
    def send_alert(self, level: AlertLevel, message: str, source: str, 
                 details: Optional[Dict[str, Any]] = None) -> Optional[Alert]:
        """
        Riasztást küld a megadott szinten
        
        Args:
            level: A riasztás súlyossága
            message: A riasztás üzenete
            source: A riasztás forrása (komponens)
            details: Opcionális részletek a riasztáshoz
            
        Returns:
            Alert: A létrehozott riasztás objektum, vagy None, ha nem lett létrehozva
        """
        if not self.enable_alerts:
            return None
        
        # Ellenőrizzük, hogy nem küldtünk-e hasonló riasztást a közelmúltban
        alert_key = f"{source}_{level.value}_{message}"
        if alert_key in self.alert_cooldowns:
            last_time = self.alert_cooldowns[alert_key]
            time_diff = (datetime.now() - last_time).total_seconds()
            
            if time_diff < ALERT_COOLDOWN_SECONDS:
                self.logger.debug(f"Riasztás figyelmen kívül hagyva (cooldown): {message}")
                return None
        
        # Riasztás létrehozása
        alert = Alert(
            level=level,
            message=message,
            source=source,
            details=details or {}
        )
        
        # Riasztás tárolása
        self.alert_history.append(alert)
        self.alert_cooldowns[alert_key] = datetime.now()
        
        # Napló bejegyzés
        log_method = {
            AlertLevel.INFO: self.logger.info,
            AlertLevel.WARNING: self.logger.warning,
            AlertLevel.CRITICAL: self.logger.critical
        }.get(level, self.logger.warning)
        
        log_method(f"RIASZTÁS [{source}]: {message}")
        
        # TODO: Külső értesítési mechanizmusok hívása (email, webhook, stb.)
        # Itt lehet implementálni a különböző értesítési csatornákat
        
        return alert
    
    def update_workflow_metrics(self, workflow_id: str, execution_time_ms: float, 
                              status: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Frissíti egy munkafolyamat teljesítmény metrikáit
        
        Args:
            workflow_id: A munkafolyamat azonosítója
            execution_time_ms: A végrehajtási idő milliszekundumban
            status: A munkafolyamat státusza (completed, error, cancelled)
            context: Opcionális kontextus a munkafolyamatról
        """
        # Ha nincs aktív teljesítménymérés, nem csinálunk semmit
        if not self.enable_performance_monitoring:
            return
        
        # Ha vannak már metrikák, az utolsót frissítjük
        if self.performance_history:
            latest = self.performance_history[-1]
            latest.graph_processing_times_ms[workflow_id] = execution_time_ms
            
            # Aktív munkafolyamatok számának frissítése
            if status == "completed":
                latest.completed_workflows += 1
            elif status == "error":
                latest.failed_workflows += 1
            
            self.logger.debug(f"Munkafolyamat metrikák frissítve: {workflow_id} ({execution_time_ms:.2f} ms, {status})")
    
    def update_response_time(self, endpoint: str, response_time_ms: float) -> None:
        """
        Frissíti egy API végpont válaszidejének metrikáját
        
        Args:
            endpoint: Az API végpont neve vagy azonosítója
            response_time_ms: A válaszidő milliszekundumban
        """
        # Ha nincs aktív teljesítménymérés, nem csinálunk semmit
        if not self.enable_performance_monitoring:
            return
        
        # Ha vannak már metrikák, az utolsót frissítjük
        if self.performance_history:
            latest = self.performance_history[-1]
            
            # Ha még nincs ilyen végpont, új átlagot kezdünk
            if endpoint not in latest.response_times_ms:
                latest.response_times_ms[endpoint] = response_time_ms
            # Egyébként frissítjük a mozgó átlagot (70% régi, 30% új érték)
            else:
                old_avg = latest.response_times_ms[endpoint]
                latest.response_times_ms[endpoint] = old_avg * 0.7 + response_time_ms * 0.3
    
    def generate_performance_report(self, output_path: Optional[str] = None, 
                                  include_graphs: bool = True) -> Dict[str, Any]:
        """
        Teljesítmény jelentést generál az összegyűjtött metrikákból
        
        Args:
            output_path: Ha meg van adva, a jelentést ide menti JSON formátumban
            include_graphs: Ha igaz, grafikonokat is generál (matplotlib kell hozzá)
        
        Returns:
            Dict: A jelentés adatai
        """
        if not self.performance_history:
            self.logger.warning("Nincs elegendő teljesítmény-adat a jelentéshez")
            return {"error": "No performance data available"}
        
        # Alapvető statisztikák számítása
        latest = self.performance_history[-1]
        
        # Átlagok számítása
        avg_cpu = sum(m.cpu_percent for m in self.performance_history) / len(self.performance_history)
        avg_memory = sum(m.memory_percent for m in self.performance_history) / len(self.performance_history)
        avg_memory_mb = sum(m.memory_used_mb for m in self.performance_history) / len(self.performance_history)
        
        # Válaszidők átlaga
        response_times = {}
        endpoint_counts = {}
        
        for metrics in self.performance_history:
            for endpoint, time_ms in metrics.response_times_ms.items():
                if endpoint not in response_times:
                    response_times[endpoint] = 0
                    endpoint_counts[endpoint] = 0
                
                response_times[endpoint] += time_ms
                endpoint_counts[endpoint] += 1
        
        avg_response_times = {
            endpoint: response_times[endpoint] / endpoint_counts[endpoint]
            for endpoint in response_times
        }
        
        # Munkafolyamat statisztikák
        completed = sum(m.completed_workflows for m in self.performance_history)
        failed = sum(m.failed_workflows for m in self.performance_history)
        total_workflows = completed + failed
        success_rate = (completed / total_workflows * 100) if total_workflows > 0 else 0
        
        # Jelentés összeállítása
        report = {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": latest.process_uptime_seconds,
            "uptime_human": self._format_duration(latest.process_uptime_seconds),
            "current_metrics": {
                "cpu_percent": latest.cpu_percent,
                "memory_percent": latest.memory_percent,
                "memory_used_mb": latest.memory_used_mb,
                "threads_count": latest.threads_count,
                "open_files": latest.open_file_descriptors,
            },
            "averages": {
                "cpu_percent": avg_cpu,
                "memory_percent": avg_memory,
                "memory_used_mb": avg_memory_mb,
            },
            "response_times_ms": avg_response_times,
            "workflows": {
                "completed": completed,
                "failed": failed,
                "total": total_workflows,
                "success_rate_percent": success_rate
            },
            "sampling_info": {
                "samples_count": len(self.performance_history),
                "interval_seconds": self.monitoring_interval_seconds
            }
        }
        
        # Grafikonok generálása, ha kérték
        if include_graphs and MATPLOTLIB_AVAILABLE:
            graph_paths = self._generate_performance_graphs()
            report["graph_paths"] = graph_paths
        
        # Jelentés mentése, ha kérték
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2)
                self.logger.info(f"Teljesítmény jelentés elmentve: {output_path}")
            except Exception as e:
                self.logger.error(f"Nem sikerült menteni a teljesítmény jelentést: {e}")
        
        return report
    
    def _generate_performance_graphs(self) -> Dict[str, str]:
        """
        Grafikonokat generál a teljesítmény adatokból
        
        Returns:
            Dict[str, str]: Grafikon típus -> fájl útvonala
        """
        if not MATPLOTLIB_AVAILABLE:
            self.logger.warning("Matplotlib nem elérhető, a grafikonok nem generálhatók")
            return {}
        
        if not self.performance_history:
            return {}
        
        graph_paths = {}
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # 1. CPU és memória használat időbeli alakulása
            plt.figure(figsize=(10, 6))
            cpu_values = [m.cpu_percent for m in self.performance_history]
            memory_values = [m.memory_percent for m in self.performance_history]
            timestamps = [i for i in range(len(self.performance_history))]
            
            plt.plot(timestamps, cpu_values, label="CPU (%)")
            plt.plot(timestamps, memory_values, label="Memória (%)")
            plt.title("Erőforrás használat időbeli alakulása")
            plt.xlabel("Minták")
            plt.ylabel("Használat (%)")
            plt.legend()
            plt.grid(True)
            
            cpu_mem_path = os.path.join(self.diagnostics_dir, "graphs", f"resources_{timestamp_str}.png")
            plt.savefig(cpu_mem_path)
            plt.close()
            graph_paths["resources"] = cpu_mem_path
            
            # 2. Válaszidők grafikonja
            if any(m.response_times_ms for m in self.performance_history):
                plt.figure(figsize=(10, 6))
                
                # Végpontok kinyerése
                all_endpoints = set()
                for m in self.performance_history:
                    all_endpoints.update(m.response_times_ms.keys())
                
                # Minden végpont adatsora
                for endpoint in all_endpoints:
                    values = []
                    for m in self.performance_history:
                        if endpoint in m.response_times_ms:
                            values.append(m.response_times_ms[endpoint])
                        else:
                            values.append(None)  # Nincs adat ennél a mintánál
                    
                    # None értékek szűrése
                    timestamps = []
                    filtered_values = []
                    for i, v in enumerate(values):
                        if v is not None:
                            timestamps.append(i)
                            filtered_values.append(v)
                    
                    if filtered_values:
                        plt.plot(timestamps, filtered_values, label=endpoint)
                
                plt.title("API válaszidők alakulása")
                plt.xlabel("Minták")
                plt.ylabel("Válaszidő (ms)")
                plt.legend()
                plt.grid(True)
                
                response_path = os.path.join(self.diagnostics_dir, "graphs", f"response_times_{timestamp_str}.png")
                plt.savefig(response_path)
                plt.close()
                graph_paths["response_times"] = response_path
            
            # 3. Munkafolyamat statisztikák (kördiagram)
            completed = sum(m.completed_workflows for m in self.performance_history)
            failed = sum(m.failed_workflows for m in self.performance_history)
            
            if completed + failed > 0:
                plt.figure(figsize=(8, 8))
                plt.pie(
                    [completed, failed], 
                    labels=["Sikeres", "Sikertelen"], 
                    autopct='%1.1f%%',
                    colors=['#4CAF50', '#F44336']
                )
                plt.title("Munkafolyamat végrehajtási statisztika")
                
                workflow_path = os.path.join(self.diagnostics_dir, "graphs", f"workflows_{timestamp_str}.png")
                plt.savefig(workflow_path)
                plt.close()
                graph_paths["workflows"] = workflow_path
        
        except Exception as e:
            self.logger.error(f"Hiba a teljesítmény grafikonok generálása közben: {e}")
        
        return graph_paths
    
    def visualize_workflow(self, workflow_id: str, workflow_data: Dict[str, Any], 
                         output_path: Optional[str] = None) -> Optional[str]:
        """
        Vizualizálja egy munkafolyamat állapotgráfját és végrehajtási útvonalát
        
        Args:
            workflow_id: A munkafolyamat azonosítója
            workflow_data: A munkafolyamat adatai (lépések, állapotok, stb.)
            output_path: Ha meg van adva, ide menti a képet
            
        Returns:
            str: A generált kép útvonala, vagy None, ha nem sikerült
        """
        if not MATPLOTLIB_AVAILABLE:
            self.logger.warning("Matplotlib nem elérhető, a munkafolyamat vizualizáció nem lehetséges")
            return None
        
        try:
            import networkx as nx
            
            # Alapértelmezett kimeneti útvonal, ha nincs megadva
            if not output_path:
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(
                    self.diagnostics_dir, 
                    "graphs", 
                    f"workflow_{workflow_id}_{timestamp_str}.png"
                )
            
            # Egyszerű gráf létrehozása a lépésekből
            G = nx.DiGraph()
            
            # Csúcsok hozzáadása
            steps = workflow_data.get('steps', [])
            for i, step in enumerate(steps):
                step_name = step.get('name', f"Step {i+1}")
                step_type = step.get('type', 'unknown')
                G.add_node(step_name, type=step_type)
            
            # Élek hozzáadása (az egymást követő lépések között)
            for i in range(len(steps) - 1):
                G.add_edge(
                    steps[i].get('name', f"Step {i+1}"),
                    steps[i+1].get('name', f"Step {i+2}")
                )
            
            # Vizualizáció
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(G, seed=42)  # Elrendezés
            
            # Csúcsok színezése a típus alapján
            node_colors = []
            for node in G.nodes():
                node_type = G.nodes[node]['type']
                if node_type == 'command':
                    node_colors.append('#2196F3')  # Kék a parancsokhoz
                elif node_type == 'decision':
                    node_colors.append('#FFC107')  # Sárga a döntési pontokhoz
                else:
                    node_colors.append('#9C27B0')  # Lila az egyéb típusokhoz
            
            # Gráf kirajzolása
            nx.draw(
                G, pos,
                with_labels=True,
                node_color=node_colors,
                node_size=2000,
                font_size=10,
                font_weight='bold',
                arrowsize=20
            )
            
            # Workflow státusz és információ
            status = workflow_data.get('status', 'unknown')
            title = f"Munkafolyamat: {workflow_id} (Státusz: {status})"
            plt.title(title)
            
            # Mentés és bezárás
            plt.savefig(output_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Munkafolyamat vizualizáció mentve: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Hiba a munkafolyamat vizualizálása közben: {e}", exc_info=True)
            return None
    
    def _format_duration(self, seconds: float) -> str:
        """
        Olvasható formátumba alakít egy időtartamot másodpercben
        
        Args:
            seconds: Az időtartam másodpercben
            
        Returns:
            str: Olvasható időformátum
        """
        if seconds < 60:
            return f"{seconds:.1f} másodperc"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} perc"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f} óra"
        else:
            days = seconds / 86400
            return f"{days:.1f} nap"
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Statisztikákat gyűjt a rendszerben előforduló hibákról
        
        Returns:
            Dict: A hibastatisztikák
        """
        if not self.error_history:
            return {"total_errors": 0}
        
        # Hibatípusok számolása
        error_types = {}
        components = {}
        error_timeline = {}
        
        for error in self.error_history:
            # Hibatípus számolása
            error_type = error.error_type
            error_types[error_type] = error_types.get(error_type, 0) + 1
            
            # Komponens számolása
            component = error.component or "unknown"
            components[component] = components.get(component, 0) + 1
            
            # Időbeli eloszlás (óránként)
            hour = error.timestamp.strftime("%Y-%m-%d %H:00")
            error_timeline[hour] = error_timeline.get(hour, 0) + 1
          # Top 5 hibatípus
        sorted_types = sorted(error_types.items(), key=lambda x: x[1], reverse=True)
        top_types = dict(sorted_types[:5])
        
        # Top 5 komponens
        sorted_components = sorted(components.items(), key=lambda x: x[1], reverse=True)
        top_components = dict(sorted_components[:5])
        
        # Recent errors (last 24 hours)
        now = datetime.now()
        recent_errors = [error for error in self.error_history 
                        if (now - error.timestamp).total_seconds() < 86400]
        
        # Error rate calculation (errors per hour)
        uptime_hours = self.get_uptime_seconds() / 3600
        error_rate = len(self.error_history) / uptime_hours if uptime_hours > 0 else 0
        
        # Statisztikák összeállítása
        stats = {
            "total_errors": len(self.error_history),
            "recent_errors": len(recent_errors),
            "error_rate": error_rate,
            "top_error_types": top_types,
            "top_error_components": top_components,
            "error_timeline": error_timeline,
            "newest_error": self.error_history[-1].to_dict() if self.error_history else None,
            "oldest_error": self.error_history[0].to_dict() if self.error_history else None
        }
        
        return stats

# A diagnosztikai menedzser globális példánya
diagnostics_manager = DiagnosticsManager()

# Hasznos dekorátorok
def log_execution_time(logger=None, threshold_ms=None):
    """
    Dekorátor, amely naplózza egy függvény végrehajtási idejét
    
    Args:
        logger: Logger objektum, vagy None az alapértelmezett loggerhez
        threshold_ms: Ha meg van adva, csak akkor naplóz, ha a végrehajtási idő 
                      meghaladja ezt az értéket milliszekundumban
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            execution_time_ms = (end_time - start_time) * 1000
            
            if threshold_ms is None or execution_time_ms > threshold_ms:
                log = logger.info if logger else logging.getLogger().info
                log(f"{func.__name__} végrehajtási ideje: {execution_time_ms:.2f} ms")
            
            return result
        return wrapper
    return decorator

def track_workflow_execution(func):
    """
    Dekorátor, amely nyomon követi egy munkafolyamat végrehajtását
    és frissíti a teljesítmény metrikákat
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        workflow_id = kwargs.get('workflow_id', None)
        if not workflow_id and args and isinstance(args[0], str):
            workflow_id = args[0]
        
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000
            
            if workflow_id:
                diagnostics_manager.update_workflow_metrics(
                    workflow_id=workflow_id,
                    execution_time_ms=execution_time_ms,
                    status="completed",
                    context={"result": "success"}
                )
            
            return result
            
        except Exception as e:
            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000
            
            if workflow_id:
                diagnostics_manager.update_workflow_metrics(
                    workflow_id=workflow_id,
                    execution_time_ms=execution_time_ms,
                    status="error",
                    context={"error": str(e)}
                )
                
                diagnostics_manager.register_error(
                    error=e,
                    component="workflow_execution",
                    workflow_id=workflow_id
                )
            
            raise
    
    return wrapper

# Importok
import functools
