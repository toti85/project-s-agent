"""
Project-S CommandProcessor
Köztes réteg a parancsok validálásához, kontextus-bővítéséhez és végrehajtásához.
"""
from typing import Optional, Dict, Any
from interfaces.api_server import Command, Response, Context
from core.command_router import router
import logging

logger = logging.getLogger("CommandProcessor")

class CommandProcessor:
    def __init__(self, event_bus=None):
        self.event_bus = event_bus  # későbbi integrációhoz

    async def process_command(
        self,
        command: Command,
        context: Optional[Context] = None,
        memory: Optional[Dict] = None,
        references: Optional[Dict] = None,
        async_mode: bool = False,
    ) -> Response:
        """
        Parancs validálás, kontextus-bővítés, végrehajtás és válasz formázás.
        """
        try:
            # 1. Parancs validálás és normalizálás
            cmd_dict = command.dict()
            cmd_type = cmd_dict.get("type", "").upper()
            if not cmd_type:
                return Response(status="error", error="Missing command type")

            # 2. Kontextus-bővítés (implicit paraméterek, hivatkozások)
            if context:
                # Példa: előző üzenetből implicit paraméter
                if cmd_type == "FILE" and not cmd_dict.get("path"):
                    # Próbáljuk megkeresni az utolsó FILE parancs path-ját
                    for msg in reversed(context.relevant_messages):
                        if msg.command and msg.command.type.upper() == "FILE" and msg.command.path:
                            cmd_dict["path"] = msg.command.path
                            break
                # További kontextus-bővítés helye

            # 3. Parancs végrehajtás delegálása
            # (async_mode később: háttérben futtatás, webhook, stb.)
            result = await router.route_command(cmd_dict)

            # 4. Válasz formázása
            return Response(status="success", result=result)
        except Exception as e:
            logger.error(f"Command processing error: {e}")
            return Response(status="error", error=str(e))

    # Későbbi bővítés: aszinkron futtatás, haladásjelentés, megszakítás, event bus
