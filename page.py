"""HTML-страница управления светодиодом и вентилятором.

Страница хранится прямо в исходном коде, поэтому Pico не нужно отдельно
читать HTML, CSS и JavaScript с файловой системы при каждом запросе.
"""

from config import FAN_DEFAULT_SPEED


# Весь интерфейс автономен и не загружает библиотеки, шрифты или стили из
# интернета. Это позволяет управлять Pico даже в локальной сети без интернета.
HTML = """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Управление Raspberry Pi Pico</title>
  <style>
    :root {
      color-scheme: light dark;
      font-family: system-ui, -apple-system, sans-serif;
    }

    body {
      min-height: 100vh;
      margin: 0;
      display: grid;
      place-items: center;
      background: #18212f;
      color: #f7f9fc;
    }

    main {
      width: min(88vw, 420px);
      padding: 32px;
      text-align: center;
      background: #243044;
      border-radius: 20px;
      box-shadow: 0 16px 50px #0006;
    }

    h1 {
      margin: 0;
      font-size: 1.5rem;
    }

    section {
      margin-top: 28px;
      padding-top: 24px;
      border-top: 1px solid #ffffff1f;
    }

    h2 {
      margin: 0 0 16px;
      font-size: 1.1rem;
    }

    button {
      width: 100%;
      padding: 16px 20px;
      border: 0;
      border-radius: 12px;
      background: #4f8cff;
      color: white;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }

    button:hover { background: #3977e8; }
    button:disabled { cursor: wait; opacity: 0.65; }

    .status {
      min-height: 1.5em;
      margin: 14px 0 0;
      color: #c9d4e8;
    }

    .speed-row {
      display: grid;
      grid-template-columns: 1fr 4rem;
      gap: 14px;
      align-items: center;
      margin-top: 20px;
    }

    input[type="range"] {
      width: 100%;
      accent-color: #4f8cff;
      cursor: pointer;
    }

    output {
      font-variant-numeric: tabular-nums;
      font-weight: 700;
    }
  </style>
</head>
<body>
  <main>
    <h1>Управление Pico 2 W</h1>

    <section>
      <h2>Светодиод</h2>
      <button id="led-toggle" type="button">Переключить светодиод</button>
      <p id="led-status" class="status" role="status">Готово к управлению</p>
    </section>

    <section>
      <h2>Вентилятор</h2>
      <button id="fan-toggle" type="button">Включить вентилятор</button>
      <label class="speed-row">
        <input id="fan-speed" type="range" min="0" max="100"
               value="__FAN_DEFAULT_SPEED__"
               aria-label="Скорость вентилятора">
        <output id="fan-speed-value" for="fan-speed">__FAN_DEFAULT_SPEED__%</output>
      </label>
      <p id="fan-status" class="status" role="status">Вентилятор выключен</p>
    </section>
  </main>

  <script>
    const ledButton = document.querySelector('#led-toggle');
    const ledStatus = document.querySelector('#led-status');
    const fanButton = document.querySelector('#fan-toggle');
    const fanSlider = document.querySelector('#fan-speed');
    const fanSpeedValue = document.querySelector('#fan-speed-value');
    const fanStatus = document.querySelector('#fan-status');

    // Обновляем все связанные элементы из единого ответа REST API.
    function showFanState(result) {
      fanSlider.value = result.speed;
      fanSpeedValue.value = result.speed + '%';
      fanButton.textContent = result.fan === 'on'
        ? 'Выключить вентилятор'
        : 'Включить вентилятор';
      fanStatus.textContent = result.fan === 'on'
        ? 'Вентилятор включён: ' + result.speed + '%'
        : 'Вентилятор выключен';
    }

    ledButton.addEventListener('click', async () => {
      // Блокируем повторное нажатие, пока Pico обрабатывает текущий запрос.
      ledButton.disabled = true;
      ledStatus.textContent = 'Отправка команды…';

      try {
        // Относительный URL работает и с IP-адресом, и с maxpico.local.
        const response = await fetch('/api/blink/toggle', {
          method: 'GET',
          cache: 'no-store'
        });

        if (!response.ok) {
          throw new Error('HTTP ' + response.status);
        }

        const result = await response.json();
        ledStatus.textContent = result.led === 'on'
          ? 'Светодиод включён'
          : 'Светодиод выключен';
      } catch (error) {
        console.error(error);
        ledStatus.textContent = 'Не удалось связаться с Pico';
      } finally {
        ledButton.disabled = false;
      }
    });

    fanButton.addEventListener('click', async () => {
      fanButton.disabled = true;
      fanStatus.textContent = 'Отправка команды…';

      try {
        const response = await fetch('/api/fan/toggle', {
          method: 'GET',
          cache: 'no-store'
        });
        if (!response.ok) throw new Error('HTTP ' + response.status);
        showFanState(await response.json());
      } catch (error) {
        console.error(error);
        fanStatus.textContent = 'Не удалось связаться с Pico';
      } finally {
        fanButton.disabled = false;
      }
    });

    // Во время движения ползунка сразу показываем выбранное значение, но
    // отправляем его только после короткой паузы, чтобы не перегружать Pico.
    let speedTimer;
    fanSlider.addEventListener('input', () => {
      const speed = fanSlider.value;
      fanSpeedValue.value = speed + '%';
      clearTimeout(speedTimer);

      speedTimer = setTimeout(async () => {
        fanSlider.disabled = true;
        fanStatus.textContent = 'Установка скорости…';

        try {
          const response = await fetch('/api/fan/speed/' + speed, {
            method: 'GET',
            cache: 'no-store'
          });
          if (!response.ok) throw new Error('HTTP ' + response.status);
          showFanState(await response.json());
        } catch (error) {
          console.error(error);
          fanStatus.textContent = 'Не удалось установить скорость';
        } finally {
          fanSlider.disabled = false;
        }
      }, 180);
    });

    // После перезагрузки страницы читаем фактическое состояние устройства:
    // вентилятор мог быть включён из другой вкладки или прямым REST-запросом.
    async function loadFanState() {
      try {
        const response = await fetch('/api/fan/status', {
          method: 'GET',
          cache: 'no-store'
        });
        if (!response.ok) throw new Error('HTTP ' + response.status);
        showFanState(await response.json());
      } catch (error) {
        console.error(error);
        fanStatus.textContent = 'Не удалось получить состояние вентилятора';
      }
    }

    loadFanState();
  </script>
</body>
</html>
"""


def get_html():
    """Вернуть содержимое главной страницы веб-интерфейса."""
    # Начальное положение ползунка берётся из config.py, чтобы его не пришлось
    # отдельно менять в HTML после настройки контроллера.
    return (
        HTML.replace("__FAN_DEFAULT_SPEED__", str(FAN_DEFAULT_SPEED))
    )
