import random
from typing import Dict
import time
from collections import deque


class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_history: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        if user_id in self.user_history:
            history = self.user_history[user_id]
            while history and history[0] <= current_time - self.window_size:
                history.popleft()
            if not history:
                del self.user_history[user_id]

    def can_send_message(self, user_id: str) -> bool:
        self._cleanup_window(user_id, time.monotonic())
        history = self.user_history.get(user_id)
        return history is None or len(history) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        if self.can_send_message(user_id):
            if user_id not in self.user_history:
                self.user_history[user_id] = deque()
            self.user_history[user_id].append(time.monotonic())
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        current_time = time.monotonic()
        self._cleanup_window(user_id, current_time)
        history = self.user_history.get(user_id)
        if not history or len(history) < self.max_requests:
            return 0.0
        return history[0] + self.window_size - current_time


def test_rate_limiter():
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    print("\n=== Messages flow simulation ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Message {message_id:2d} | User {user_id} | {'✓' if result else f'× (waiting {wait_time:.1f}s)'}")
        time.sleep(random.uniform(0.1, 1.0))

    print("\nWaiting 4 seconds...")
    time.sleep(4)

    print("\n=== New series of messages after waiting ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Message {message_id:2d} | User {user_id} | {'✓' if result else f'× (waiting {wait_time:.1f}s)'}")
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()
