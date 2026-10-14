"""Независимое управление левым и правым моторами через PWM/0 или 0/PWM."""

from machine import Pin, PWM
from config import (MOTOR_ENABLED, MOTOR_AIN1_PIN, MOTOR_AIN2_PIN,
                    MOTOR_RIGHT_AIN1_PIN, MOTOR_RIGHT_AIN2_PIN,
                    MOTOR_PWM_FREQUENCY, MOTOR_DEFAULT_SPEED)


class Motor:
    def __init__(self, ain1_pin, ain2_pin):
        self._direction = "stop"
        self._speed = MOTOR_DEFAULT_SPEED
        self._ain1 = None
        self._ain2 = None
        if MOTOR_ENABLED:
            pin1 = Pin(ain1_pin, Pin.OUT, value=0)
            pin2 = Pin(ain2_pin, Pin.OUT, value=0)
            self._ain1 = PWM(pin1, freq=MOTOR_PWM_FREQUENCY, duty_u16=0)
            self._ain2 = PWM(pin2, freq=MOTOR_PWM_FREQUENCY, duty_u16=0)

    def _apply_output(self):
        if not MOTOR_ENABLED:
            return
        # Сначала обнуляем оба входа, затем включаем выбранное направление.
        self._ain1.duty_u16(0)
        self._ain2.duty_u16(0)
        duty = (self._speed * 65535 + 50) // 100
        if self._direction == "forward":
            self._ain1.duty_u16(duty)
        elif self._direction == "reverse":
            self._ain2.duty_u16(duty)


    def set_direction(self, direction):
        if direction not in ("forward", "reverse", "stop"):
            raise ValueError("invalid direction")
        if not MOTOR_ENABLED and direction != "stop":
            raise ValueError("motor is disabled")
        # При реверсе работающего мотора сначала требуется явная остановка.
        if (self._speed > 0 and self._direction != "stop" and direction != "stop"
                and direction != self._direction):
            raise ValueError("stop motor before reversing")
        self._direction = direction
        self._apply_output()


    def set_speed(self, speed):
        if not isinstance(speed, int) or isinstance(speed, bool) or not 0 <= speed <= 100:
            raise ValueError("speed must be an integer from 0 to 100")
        self._speed = speed
        if speed == 0:
            self._direction = "stop"
        self._apply_output()


    def get_state(self):
        return {"enabled": MOTOR_ENABLED, "direction": self._direction, "speed": self._speed}


_motors = {
    "left": Motor(MOTOR_AIN1_PIN, MOTOR_AIN2_PIN),
    "right": Motor(MOTOR_RIGHT_AIN1_PIN, MOTOR_RIGHT_AIN2_PIN),
}


def set_direction(direction, side="left"):
    _motors[side].set_direction(direction)


def set_speed(speed, side="left"):
    _motors[side].set_speed(speed)


def get_state(side="left"):
    return _motors[side].get_state()


def stop():
    """Остановить оба мотора при завершении программы."""
    for device in _motors.values():
        device.set_direction("stop")
