from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional
import functools
import importlib
import logging

from .config import LangfuseConfig

logger = logging.getLogger(__name__)


def bind_session_to_current_trace(session_id: str) -> None:
    """Attach the challenge session ID to the currently observed Langfuse trace."""
    try:
        decorators_module = importlib.import_module("langfuse.decorators")
        langfuse_context = getattr(decorators_module, "langfuse_context")
        langfuse_context.update_current_trace(session_id=session_id)
    except Exception as exc:
        logger.debug("[Langfuse] bind_session_to_current_trace failed: %s", exc)
        return


@dataclass
class TraceClient:
    enabled: bool
    langfuse: Optional[Any]
    session_id: Optional[str] = None
    trace_id: Optional[str] = None
    root_trace: Optional[Any] = None

    def start_run(self, session_id: str) -> None:
        self.session_id = session_id
        if not self.enabled or self.langfuse is None:
            logger.warning("[Langfuse] TraceClient disabled — traces will NOT be sent. "
                           "Check LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY / LANGFUSE_HOST.")
            return

        try:
            if hasattr(self.langfuse, "create_trace_id"):
                self.trace_id = self.langfuse.create_trace_id(seed=session_id)

            if hasattr(self.langfuse, "trace"):
                kwargs: dict[str, Any] = {
                    "name": "wellbeing_pipeline_run",
                    "session_id": session_id,
                    "input": {"session_id": session_id},
                }
                if self.trace_id:
                    kwargs["id"] = self.trace_id
                self.root_trace = self.langfuse.trace(**kwargs)
                logger.info("[Langfuse] Trace started — session_id=%s trace_id=%s", session_id, self.trace_id)
        except Exception as exc:
            logger.error("[Langfuse] Failed to start trace: %s", exc)

    def event(
        self,
        name: str,
        input_payload: Optional[dict[str, Any]] = None,
        output_payload: Optional[dict[str, Any]] = None,
    ) -> None:
        if not self.enabled or self.langfuse is None:
            return

        if self.root_trace is not None and hasattr(self.root_trace, "event"):
            self.root_trace.event(name=name, input=input_payload, output=output_payload)
            return

        if hasattr(self.langfuse, "create_event"):
            kwargs: dict[str, Any] = {
                "name": name,
                "input": input_payload,
                "output": output_payload,
                "metadata": {"session_id": self.session_id} if self.session_id else None,
            }
            if self.trace_id:
                kwargs["trace_context"] = {"trace_id": self.trace_id}
            self.langfuse.create_event(**kwargs)
            return

        if hasattr(self.langfuse, "trace"):
            self.langfuse.trace(
                name=name,
                input=input_payload,
                output=output_payload,
                session_id=self.session_id,
            )

    def flush(self) -> None:
        try:
            decorators_module = importlib.import_module("langfuse.decorators")
            langfuse_context = getattr(decorators_module, "langfuse_context")
            langfuse_context.flush()
            logger.info("[Langfuse] Decorator context flushed.")
        except Exception as exc:
            logger.debug("[Langfuse] Decorator flush skipped: %s", exc)

        if not self.enabled or self.langfuse is None:
            return
        if hasattr(self.langfuse, "flush"):
            try:
                self.langfuse.flush()
                logger.info("[Langfuse] Client flushed — traces sent to %s", self.langfuse.base_url if hasattr(self.langfuse, 'base_url') else '(unknown host)')
            except Exception as exc:
                logger.error("[Langfuse] Flush failed: %s", exc)


def build_trace_client(config: LangfuseConfig) -> TraceClient:
    if not config.enabled:
        return TraceClient(enabled=False, langfuse=None)

    from langfuse import Langfuse

    client = Langfuse(
        public_key=config.public_key,
        secret_key=config.secret_key,
        host=config.host,
    )
    return TraceClient(enabled=True, langfuse=client)


def observe_step(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Use Langfuse @observe when available; otherwise no-op."""

    try:
        decorators_module = importlib.import_module("langfuse.decorators")
        observe = getattr(decorators_module, "observe")
        return observe(name=name)
    except Exception:

        def passthrough(func: Callable[..., Any]) -> Callable[..., Any]:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                return func(*args, **kwargs)

            return wrapper

        return passthrough
