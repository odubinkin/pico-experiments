"""Управление скоростью вентилятора с помощью аппаратного PWM."""

from machine import Pin, PWM

from config import (
    FAN_DEFAULT_SPEED,
    FAN_INA_PIN,
    FAN_INB_PIN,
    FAN_MIN_DUTY_PERCENT,
    FAN_PWM_FREQUENCY,
)


# Это исходная проверенная схема подключения: INA получает PWM-сигнал, а INB
# остаётся обычным цифровым выходом с постоянным уровнем 0.
_ina = PWM(Pin(FAN_INA_PIN))
_inb = Pin(FAN_INB_PIN, Pin.OUT)
_ina.freq(FAN_PWM_FREQUENCY)
_inb.value(0)

# При загрузке контроллера вентилятор безопасно остаётся выключенным.
_is_on = False
_speed = FAN_DEFAULT_SPEED
_ina.duty_u16(0)


def _percent_to_duty(speed):
    """Преобразовать пользовательские 0–100% в рабочий PWM 60–100%."""
    # Нижняя часть физического диапазона бесполезна для этого вентилятора.
    # Например, пользовательские 0% дают 60% PWM, а 50% дают 80% PWM.
    duty_range = 100 - FAN_MIN_DUTY_PERCENT
    physical_percent = (
        FAN_MIN_DUTY_PERCENT + (speed * duty_range + 50) // 100
    )
    return (physical_percent * 65535 + 50) // 100


def _apply_output():
    """Применить выбранную скорость либо полностью отключить PWM."""
    _inb.value(0)
    _ina.duty_u16(_percent_to_duty(_speed) if _is_on else 0)


def set_speed(speed):
    """Выбрать скорость по пользовательской шкале 0–100%."""
    global _speed

    # Явная проверка защищает драйвер и упрощает обработку неверного REST URL.
    if not isinstance(speed, int) or isinstance(speed, bool):
        raise ValueError("speed must be an integer")
    if speed < 0 or speed > 100:
        raise ValueError("speed must be between 0 and 100")

    _speed = speed
    # Изменение ползунка не включает выключенный вентилятор, но для уже
    # включённого устройства новая скорость применяется немедленно.
    _apply_output()
    return _speed


def set_state(is_on):
    """Включить или выключить вентилятор, сохранив выбранную скорость."""
    global _is_on

    _is_on = bool(is_on)
    _apply_output()
    return _is_on


def toggle():
    """Переключить питание вентилятора и вернуть новое состояние."""
    return set_state(not _is_on)


def get_speed():
    """Вернуть текущую скорость в процентах."""
    return _speed


def is_on():
    """Вернуть True, если вентилятор включён."""
    return _is_on
