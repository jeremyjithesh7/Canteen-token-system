import time
from threading import Lock
from typing import Dict, Tuple, Optional
from fastapi import HTTPException, status

class LoginRateLimiter:
    """
    In-memory thread-safe rate limiter for authentication endpoints.
    Limits failed login attempts per key (email or IP).
    """
    def __init__(self, max_attempts: int = 5, window_seconds: int = 300, lockout_seconds: int = 900):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds # 5 minutes
        self.lockout_seconds = lockout_seconds # 15 minutes lockout
        # Map: key -> (failed_count, first_attempt_time, locked_until_time)
        self.records: Dict[str, Tuple[int, float, float]] = {}
        self.lock = Lock()

    def check_rate_limit(self, key: str):
        now = time.time()
        with self.lock:
            if key in self.records:
                attempts, first_time, locked_until = self.records[key]
                if locked_until > now:
                    remaining_mins = int((locked_until - now) / 60) + 1
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Too many failed login attempts. Account temporarily locked. Try again in {remaining_mins} minutes."
                    )
                elif now - first_time > self.window_seconds:
                    # Reset window after time expiry
                    del self.records[key]

    def record_failure(self, key: str):
        now = time.time()
        with self.lock:
            if key in self.records:
                attempts, first_time, _ = self.records[key]
                if now - first_time <= self.window_seconds:
                    attempts += 1
                    locked_until = now + self.lockout_seconds if attempts >= self.max_attempts else 0
                    self.records[key] = (attempts, first_time, locked_until)
                    if attempts >= self.max_attempts:
                        remaining_mins = int(self.lockout_seconds / 60)
                        raise HTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail=f"Too many failed login attempts. Account temporarily locked. Try again in {remaining_mins} minutes."
                        )
                else:
                    self.records[key] = (1, now, 0)
            else:
                self.records[key] = (1, now, 0)

    def record_success(self, key: str):
        with self.lock:
            if key in self.records:
                del self.records[key]

# Singleton instance for login rate limiting
login_rate_limiter = LoginRateLimiter(max_attempts=5, window_seconds=300, lockout_seconds=900)
