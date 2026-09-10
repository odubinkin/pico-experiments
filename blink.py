"""Управление встроенным светодиодом Raspberry Pi Pico 2 W."""

from machine import Pin


# У Pico W встроенный светодиод подключён не к обычному номеру GPIO.
# MicroPython предоставляет для него переносимое символьное имя "LED".
_led = Pin("LED", Pin.OUT)

# Храним состояние отдельно, чтобы REST API мог вернуть новое значение сразу
# после переключения. При старте программы светодиод всегда выключен.
_is_on = False
_led.off()


def set_state(is_on):
    """Установить состояние светодиода и вернуть фактическое состояние."""
    global _is_on

    _is_on = bool(is_on)
    _led.value(1 if _is_on else 0)
    return _is_on


def toggle():
    """Переключить светодиод и вернуть его новое состояние."""
    return set_state(not _is_on)


def get_state():
    """Вернуть True, если светодиод включён, иначе False."""
    return _is_on
