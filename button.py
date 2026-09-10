"""Асинхронный опрос кнопки, подключённой между GPIO и GND."""

import uasyncio as asyncio
from machine import Pin

import blink
from config import BUTTON_PIN


# PULL_UP удерживает вход в состоянии 1. При нажатии кнопка замыкает его на
# землю, поэтому нажатому состоянию соответствует значение 0.
_button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)


async def watch():
    """Бесконечно отслеживать нажатия, не блокируя веб-сервер."""
    while True:
        if _button.value() == 0:
            # Короткая пауза отсекает дребезг механических контактов.
            await asyncio.sleep_ms(30)

            if _button.value() == 0:
                new_state = blink.toggle()
                print("[button] Светодиод",
                      "включён" if new_state else "выключен")

                # Ждём отпускания: долгое удержание считается одним нажатием.
                while _button.value() == 0:
                    await asyncio.sleep_ms(10)

                # Защита от дребезга уже при отпускании кнопки.
                await asyncio.sleep_ms(30)

        # Небольшая пауза отдаёт управление другим задачам event loop.
        await asyncio.sleep_ms(10)
