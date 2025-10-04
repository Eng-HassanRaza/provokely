from queue import Queue
from typing import Dict, List, Any


_subscribers: Dict[int, List[Queue]] = {}


def subscribe(user_id: int) -> Queue:
    q: Queue = Queue()
    _subscribers.setdefault(user_id, []).append(q)
    return q


def unsubscribe(user_id: int, q: Queue) -> None:
    try:
        lst = _subscribers.get(user_id, [])
        if q in lst:
            lst.remove(q)
        if not lst and user_id in _subscribers:
            del _subscribers[user_id]
    except Exception:
        pass


def publish(user_id: int, data: Any) -> None:
    for q in list(_subscribers.get(user_id, [])):
        try:
            q.put_nowait(data)
        except Exception:
            # drop broken subscribers
            try:
                _subscribers[user_id].remove(q)
            except Exception:
                pass



