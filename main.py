"""Точка входа: MicroPython автоматически запускает main.py после загрузки."""

import uasyncio as asyncio

import button
import wifi
import webserver


async def main():
    """Запустить независимые фоновые задачи устройства."""
    # Кнопка начинает работать сразу, даже если Wi-Fi отсутствует.
    asyncio.create_task(button.watch())
    asyncio.create_task(wifi.keep_connected())

    # Сервер сам повторяет открытие порта при временной сетевой ошибке.
    await webserver.serve_forever()


try:
    asyncio.run(main())
except KeyboardInterrupt:
    # Ctrl+C в REPL аккуратно выключает все подключённые исполнительные
    # устройства перед остановкой программы.
    import blink
    import fan
    blink.set_state(False)
    fan.set_state(False)
finally:
    # Очищаем event loop для удобного повторного запуска из интерактивной REPL.
    asyncio.new_event_loop()
