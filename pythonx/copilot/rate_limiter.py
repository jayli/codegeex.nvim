#!/usr/bin/env python3
# encoding: utf-8
import time

class RateLimiter:
    # limit: 次数, 比如 10
    # duration: 时间间隔，单位秒，比如 5
    def __init__(self, limit, duration):
        self.limit = limit
        self.duration = duration
        self.timestamps = []

    def is_allowed(self):
        current_time = time.time()
        self.timestamps = [t for t in self.timestamps if t > current_time - self.duration]
        if len(self.timestamps) < self.limit:
            self.timestamps.append(current_time)
            return True
        else:
            return False
