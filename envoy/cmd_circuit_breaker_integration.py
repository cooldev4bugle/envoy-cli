"""Integration hooks: wrap vault push/pull with circuit breaker protection."""

from typing import Callable, Any

from envoy import circuit_breaker as cb


class CircuitOpenError(Exception):
    """Raised when a circuit breaker is open and the operation is blocked."""


def guarded(
    project: str,
    env: str,
    operation: Callable[[], Any],
    threshold: int = cb.DEFAULT_THRESHOLD,
    timeout: int = cb.DEFAULT_TIMEOUT,
) -> Any:
    """Execute *operation* guarded by the circuit breaker for project/env.

    Raises CircuitOpenError if the breaker is open.
    Records success or failure automatically.
    """
    if cb.is_open(project, env, timeout=timeout):
        state = cb.get_state(project, env)
        raise CircuitOpenError(
            f"Circuit breaker is OPEN for {project}/{env} "
            f"(failures={state['failures']}). Try again later."
        )
    try:
        result = operation()
        cb.record_success(project, env)
        return result
    except Exception as exc:
        cb.record_failure(project, env, threshold=threshold)
        raise exc


def guarded_push(project: str, env: str, push_fn: Callable, *args, **kwargs) -> Any:
    """Circuit-breaker-wrapped push."""
    return guarded(project, env, lambda: push_fn(*args, **kwargs))


def guarded_pull(project: str, env: str, pull_fn: Callable, *args, **kwargs) -> Any:
    """Circuit-breaker-wrapped pull."""
    return guarded(project, env, lambda: pull_fn(*args, **kwargs))
