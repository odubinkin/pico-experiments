"""Минимальный асинхронный HTTP-сервер для REST API."""

import uasyncio as asyncio

import api
import page
from config import WEB_PORT


_STATUS_TEXT = {
    200: "OK",
    400: "Bad Request",
    404: "Not Found",
    405: "Method Not Allowed",
    500: "Internal Server Error",
}


def _dispatch_request(method, path):
    """Направить главную страницу в page.py, а REST-запросы — в api.py."""
    clean_path = path.split("?", 1)[0]

    if clean_path == "/":
        if method != "GET":
            return 405, "text/plain; charset=utf-8", "Method Not Allowed"

        return 200, "text/html; charset=utf-8", page.get_html()

    return api.handle_request(method, path)


async def _close_writer(writer):
    """Закрыть соединение совместимо с разными версиями uasyncio."""
    try:
        writer.close()
    except (AttributeError, OSError):
        pass

    try:
        await writer.wait_closed()
    except (AttributeError, OSError):
        pass


async def _handle_client(reader, writer):
    """Прочитать один HTTP-запрос, вызвать API и отправить HTTP-ответ."""
    try:
        request_line = await reader.readline()
        if not request_line:
            return

        try:
            # Первая строка имеет вид: GET /api/blink/toggle HTTP/1.1
            method, path, _http_version = request_line.decode().strip().split()
        except (ValueError, UnicodeError):
            method, path = "", ""
            status = 400
            content_type = "application/json; charset=utf-8"
            body = '{"error":"bad_request"}'
        else:
            # В этом проекте заголовки пока не используются, но их необходимо
            # считать до пустой строки, чтобы корректно завершить HTTP-запрос.
            while True:
                header = await reader.readline()
                if not header or header == b"\r\n":
                    break

            try:
                status, content_type, body = _dispatch_request(method, path)
            except Exception as error:
                # Ошибка одного клиента не должна остановить весь сервер.
                print("[webserver] Ошибка REST API:", error)
                status = 500
                content_type = "application/json; charset=utf-8"
                body = '{"error":"internal_server_error"}'

        body_bytes = body.encode("utf-8")
        reason = _STATUS_TEXT.get(status, "Error")
        response_headers = (
            "HTTP/1.1 {} {}\r\n"
            "Content-Type: {}\r\n"
            "Content-Length: {}\r\n"
            "Connection: close\r\n"
            "Access-Control-Allow-Origin: *\r\n"
            "\r\n"
        ).format(status, reason, content_type, len(body_bytes))

        writer.write(response_headers.encode("utf-8"))
        writer.write(body_bytes)
        await writer.drain()
    except Exception as error:
        print("[webserver] Ошибка HTTP-соединения:", error)
    finally:
        await _close_writer(writer)


async def serve_forever():
    """Запустить сервер на всех сетевых интерфейсах и ждать запросы."""
    # Обычно сокет можно открыть ещё до получения Wi-Fi-адреса. Если конкретная
    # версия прошивки возвращает OSError, повторяем попытку вместо завершения
    # программы — физическая кнопка тем временем продолжает работать.
    while True:
        try:
            _server = await asyncio.start_server(
                _handle_client, "0.0.0.0", WEB_PORT
            )
            break
        except OSError as error:
            print("[webserver] Не удалось открыть порт:", error)
            await asyncio.sleep(5)

    print("[webserver] Сервер запущен на порту", WEB_PORT)

    # У MicroPython Server нет обязательного метода serve_forever(), поэтому
    # удерживаем задачу живой переносимым бесконечным ожиданием.
    while True:
        await asyncio.sleep(3600)
