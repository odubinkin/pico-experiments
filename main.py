"""Точка входа: MicroPython автоматически запускает main.py после загрузки."""

import uasyncio as asyncio

# Сначала импортируем встроенный драйвер. На Pico W встроенные модули имеют
# приоритет над одноимёнными файлами, поэтому здесь получаем именно WLAN API.
import network as micropython_network

import button
import webserver


def _load_network_module():
    """Загрузить наш network.py под именем wifi_manager без конфликта имён."""
    namespace = {
        "__name__": "wifi_manager",
        "_network": micropython_network,
    }

    with open("network.py", "r") as source_file:
        source = source_file.read()

    exec(compile(source, "network.py", "exec"), namespace)
    return namespace


async def main():
    """Запустить независимые фоновые задачи устройства."""
    wifi_manager = _load_network_module()

    # Кнопка начинает работать сразу, даже если Wi-Fi отсутствует.
    asyncio.create_task(button.watch())
    asyncio.create_task(wifi_manager["keep_connected"]())

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
