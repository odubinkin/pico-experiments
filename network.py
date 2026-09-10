"""Настройка сетевого имени и подключение Raspberry Pi Pico 2 W к Wi-Fi.

Важно: файл называется network.py по условию задачи, но такое же имя имеет
встроенный модуль MicroPython. Поэтому main.py загружает этот файл явно и
передаёт встроенный модуль через переменную ``_network``.
"""

import uasyncio as asyncio

from config import (
    DEVICE_HOSTNAME,
    WIFI_CONNECT_TIMEOUT,
    WIFI_PASSWORD,
    WIFI_RETRY_INTERVAL,
    WIFI_SSID,
)

# main.py заранее помещает сюда встроенный модуль MicroPython ``network``.
# Явное присваивание также объясняет это Pylance и убирает предупреждение о
# якобы неопределённом имени. Напрямую импортировать данный файл не следует.
_network = globals().get("_network")
if _network is None:
    raise RuntimeError("network.py должен загружаться через main.py")


def _set_hostname(wlan):
    """Задать hostname с учётом различий между версиями MicroPython."""
    try:
        # В актуальных сборках MicroPython hostname настраивается функцией
        # встроенного модуля network.
        _network.hostname(DEVICE_HOSTNAME)
    except (AttributeError, OSError):
        try:
            # В некоторых старых сборках параметр принадлежит интерфейсу WLAN.
            wlan.config(hostname=DEVICE_HOSTNAME)
        except (AttributeError, OSError):
            print("[network] Не удалось задать сетевое имя:", DEVICE_HOSTNAME)


async def connect():
    """Выполнить одну попытку подключения и вернуть активный интерфейс WLAN.

    Функция не выбрасывает ошибку при отсутствии сети: она пишет причину в
    консоль и возвращает интерфейс. Поэтому остальные части программы — кнопка
    и веб-сервер — могут продолжать работу.
    """
    wlan = _network.WLAN(_network.STA_IF)

    # Hostname обязательно задаётся ДО активации и подключения интерфейса.
    # Иначе DHCP и mDNS продолжат использовать прежнее имя до переподключения.
    _set_hostname(wlan)
    wlan.active(True)

    if wlan.isconnected():
        print("[network] Wi-Fi уже подключён, IP:", wlan.ifconfig()[0])
        return wlan

    print("[network] Подключение к Wi-Fi:", WIFI_SSID)
    try:
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    except OSError as error:
        print("[network] Не удалось начать подключение:", error)
        return wlan

    # Ожидание асинхронное: event loop продолжает опрашивать кнопку и
    # обслуживать другие задачи, пока сетевой чип устанавливает соединение.
    for _ in range(WIFI_CONNECT_TIMEOUT * 2):
        if wlan.isconnected():
            print("[network] Подключено, IP:", wlan.ifconfig()[0])
            return wlan
        await asyncio.sleep_ms(500)

    # status() содержит код ошибки драйвера, полезный при диагностике.
    print("[network] Не удалось подключиться, status =", wlan.status())
    return wlan


async def keep_connected():
    """Поддерживать Wi-Fi: после обрыва периодически подключаться повторно."""
    wlan = await connect()

    while True:
        if not wlan.isconnected():
            print("[network] Wi-Fi недоступен; следующая попытка подключения")
            await asyncio.sleep(WIFI_RETRY_INTERVAL)
            wlan = await connect()
        else:
            # Проверяем соединение не слишком часто, чтобы не занимать CPU.
            await asyncio.sleep(5)
