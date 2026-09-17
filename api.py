"""Маршруты REST API устройства."""

try:
    import ujson as json
except ImportError:
    # Этот вариант удобен при локальной проверке файла обычным Python.
    import json

import blink
import fan
import rgb


def _json_response(status, data):
    """Сформировать ответ маршрутизатора в едином формате."""
    return status, "application/json; charset=utf-8", json.dumps(data)


def _fan_response():
    """Вернуть текущее состояние вентилятора в общем формате."""
    speed = fan.get_speed()
    return _json_response(200, {
        "ok": True,
        "fan": "on" if fan.is_on() else "off",
        "speed": speed,
    })


def _rgb_response():
    """Вернуть состояния каналов RGB в общем формате."""
    states = rgb.get_states()
    return _json_response(200, {
        "ok": True,
        "rgb": {
            color: "on" if is_on else "off"
            for color, is_on in states.items()
        },
    })


def handle_request(method, path):
    """Обработать HTTP-метод и путь; вернуть status, content-type и body."""
    # Query string не участвует в выборе маршрута. Например,
    # /api/blink/toggle?source=test обрабатывается тем же методом.
    clean_path = path.split("?", 1)[0]

    if clean_path == "/api/blink/toggle":
        if method != "GET":
            return _json_response(405, {
                "error": "method_not_allowed",
                "allowed": ["GET"],
            })

        new_state = blink.toggle()
        print("[api] Светодиод", "включён" if new_state else "выключен")
        return _json_response(200, {
            "ok": True,
            "led": "on" if new_state else "off",
        })

    if clean_path == "/api/rgb/status":
        if method != "GET":
            return _json_response(405, {
                "error": "method_not_allowed",
                "allowed": ["GET"],
            })

        return _rgb_response()

    rgb_toggle_prefix = "/api/rgb/"
    if clean_path.startswith(rgb_toggle_prefix) and clean_path.endswith("/toggle"):
        if method != "GET":
            return _json_response(405, {
                "error": "method_not_allowed",
                "allowed": ["GET"],
            })

        color = clean_path[len(rgb_toggle_prefix):-len("/toggle")]
        if color not in ("red", "green", "blue"):
            return _json_response(404, {"error": "not_found"})

        is_on = rgb.toggle(color)
        print("[api] RGB", color, "включён" if is_on else "выключен")
        return _rgb_response()

    if clean_path == "/api/fan/toggle":
        if method != "GET":
            return _json_response(405, {
                "error": "method_not_allowed",
                "allowed": ["GET"],
            })

        is_on = fan.toggle()
        print("[api] Вентилятор", "включён" if is_on else "выключен")
        return _fan_response()

    if clean_path == "/api/fan/status":
        if method != "GET":
            return _json_response(405, {
                "error": "method_not_allowed",
                "allowed": ["GET"],
            })

        # Страница использует этот маршрут после загрузки, чтобы отобразить
        # реальное состояние даже после обновления вкладки браузера.
        return _fan_response()

    speed_prefix = "/api/fan/speed/"
    if clean_path.startswith(speed_prefix):
        if method != "GET":
            return _json_response(405, {
                "error": "method_not_allowed",
                "allowed": ["GET"],
            })

        # API принимает пользовательские 0–100%. Преобразование в реальный
        # рабочий диапазон PWM выполняется внутри fan.py.
        speed_text = clean_path[len(speed_prefix):]
        try:
            speed = int(speed_text)
            fan.set_speed(speed)
        except (TypeError, ValueError):
            return _json_response(400, {
                "error": "invalid_speed",
                "message": "speed must be an integer from 0 to 100",
            })

        print("[api] Скорость вентилятора:", speed, "%")
        return _fan_response()

    return _json_response(404, {"error": "not_found"})
