"""Управление трёхканальным RGB-светодиодом с инверсной логикой."""

from machine import Pin

from config import RGB_BLUE_PIN, RGB_GREEN_PIN, RGB_RED_PIN


# Каналы RGB подключены к GPIO со стороны «минуса». Поэтому высокий уровень
# отключает ток через светодиод, а низкий — включает соответствующий цвет.
_pins = {
    "red": Pin(RGB_RED_PIN, Pin.OUT),
    "green": Pin(RGB_GREEN_PIN, Pin.OUT),
    "blue": Pin(RGB_BLUE_PIN, Pin.OUT),
}
_states = {
    "red": False,
    "green": False,
    "blue": False,
}


def set_state(color, is_on):
    """Включить или выключить один цвет и вернуть его новое состояние."""
    if color not in _pins:
        raise ValueError("unknown RGB color")

    _states[color] = bool(is_on)
    # Active-low: 0 включает канал, 1 выключает его.
    _pins[color].value(0 if _states[color] else 1)
    return _states[color]


def toggle(color):
    """Переключить один цвет и вернуть его новое состояние."""
    if color not in _pins:
        raise ValueError("unknown RGB color")
    return set_state(color, not _states[color])


def get_state(color):
    """Вернуть состояние одного цвета."""
    if color not in _pins:
        raise ValueError("unknown RGB color")
    return _states[color]


def get_states():
    """Вернуть состояния всех трёх каналов RGB."""
    return _states.copy()


def set_all(is_on):
    """Одновременно установить состояние всех RGB-каналов."""
    for color in _pins:
        set_state(color, is_on)


# Сразу после создания выходов удерживаем все катоды в высоком уровне, чтобы
# RGB-светодиод при загрузке гарантированно оставался выключенным.
set_all(False)
