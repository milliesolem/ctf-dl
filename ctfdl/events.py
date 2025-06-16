import asyncio
from collections import defaultdict
from typing import Callable, Any, DefaultDict, List


class EventEmitter:
    """A simple event emitter class for decoupling components."""

    def __init__(self):
        """Initializes the EventEmitter with a dictionary to hold listeners."""
        self._listeners: DefaultDict[str, List[Callable]] = defaultdict(list)

    def on(self, event_name: str, listener: Callable[..., Any]):
        """
        Registers a listener function to be called when an event is emitted.

        Args:
            event_name: The name of the event to listen for.
            listener: The function to be called when the event occurs.
        """
        self._listeners[event_name].append(listener)

    async def emit(self, event_name: str, *args: Any, **kwargs: Any):
        """
        Emits an event, calling all registered listeners for that event.
        Awaits listeners that are coroutines.
        """
        if event_name not in self._listeners:
            return

        for listener in self._listeners[event_name]:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(*args, **kwargs)
                else:
                    listener(*args, **kwargs)
            except Exception as e:
                print(f"Error in event listener for '{event_name}': {e}")
