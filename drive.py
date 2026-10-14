"""Смешивание осей джойстика и безопасное переключение направления моторов."""

import motor
from config import (JOYSTICK_DEADZONE, JOYSTICK_INVERT_X, JOYSTICK_INVERT_Y,
                    JOYSTICK_DEBOUNCE_MS, MOTOR_REVERSE_PAUSE_MS)


def axis(raw, invert=False):
    value = max(-1.0, min(1.0, (raw - 32768) / 32767))
    if abs(value) <= JOYSTICK_DEADZONE:
        return 0.0
    value = (1 if value > 0 else -1) * (abs(value) - JOYSTICK_DEADZONE) / (1 - JOYSTICK_DEADZONE)
    return -value if invert else value


def mix(x, y):
    turn = axis(x, JOYSTICK_INVERT_X)
    throttle = axis(y, JOYSTICK_INVERT_Y)
    left, right = throttle + turn, throttle - turn
    scale = max(1.0, abs(left), abs(right))
    return round(left / scale * 100), round(right / scale * 100)


class Drive:
    def __init__(self):
        self.enabled = False
        self._stable_sw = 1
        self._candidate_sw = 1
        self._debounce_ms = 0
        self._last_direction = {side: 'stop' for side in ('left', 'right')}
        self._stopped_ms = {side: MOTOR_REVERSE_PAUSE_MS for side in ('left', 'right')}

    def update(self, x, y, sw, elapsed_ms):
        if sw != self._candidate_sw:
            self._candidate_sw = sw
            self._debounce_ms = 0
        else:
            self._debounce_ms += elapsed_ms
        if self._debounce_ms >= JOYSTICK_DEBOUNCE_MS and sw != self._stable_sw:
            self._stable_sw = sw
            if sw == 0:
                self.enabled = not self.enabled
                print('[joystick] motors', 'ON' if self.enabled else 'OFF')

        commands = mix(x, y) if self.enabled else (0, 0)
        for side, command in zip(('left', 'right'), commands):
            state = motor.get_state(side)
            if state['direction'] != 'stop':
                self._last_direction[side] = state['direction']
                self._stopped_ms[side] = 0
            else:
                self._stopped_ms[side] += elapsed_ms
            direction = 'forward' if command > 0 else 'reverse' if command < 0 else 'stop'
            reversing = (direction != 'stop' and self._last_direction[side] != 'stop'
                         and direction != self._last_direction[side]
                         and self._stopped_ms[side] < MOTOR_REVERSE_PAUSE_MS)
            if not state['enabled'] or direction == 'stop' or reversing:
                motor.set_direction('stop', side)
                continue
            motor.set_speed(abs(command), side)
            motor.set_direction(direction, side)
