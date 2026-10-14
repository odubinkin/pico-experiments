"""HTML-страница управления светодиодами, вентилятором и мотором.

Страница хранится прямо в исходном коде, поэтому Pico не нужно отдельно
читать HTML, CSS и JavaScript с файловой системы при каждом запросе.
"""

from config import FAN_DEFAULT_SPEED, MOTOR_DEFAULT_SPEED


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

    .color-buttons {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
    }

    .color-button {
      padding: 14px 8px;
    }

    .color-button.red { background: #df4c55; }
    .color-button.green { background: #35a66f; }
    .color-button.blue { background: #3c7ee9; }
    .color-button.red:hover { background: #c83d47; }
    .color-button.green:hover { background: #278b5a; }
    .color-button.blue:hover { background: #2869cf; }
    .color-button.is-on { box-shadow: inset 0 0 0 3px #fff; }
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
      <h2>RGB-светодиод</h2>
      <div class="color-buttons">
        <button class="color-button red" data-color="red" type="button">Красный</button>
        <button class="color-button green" data-color="green" type="button">Зелёный</button>
        <button class="color-button blue" data-color="blue" type="button">Синий</button>
      </div>
      <p id="rgb-status" class="status" role="status">Все цвета выключены</p>
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
    <section>
      <h2>Левый</h2>
      <div class="color-buttons">
        <button id="motor-left-forward" type="button" disabled>Вперёд</button>
        <button id="motor-left-stop" type="button">Стоп</button>
        <button id="motor-left-reverse" type="button" disabled>Назад</button>
      </div>
      <label class="speed-row">
        <input id="motor-left-speed" type="range" min="0" max="100"
               value="__MOTOR_DEFAULT_SPEED__" aria-label="Скорость левый мотора" disabled>
        <output id="motor-left-speed-value" for="motor-left-speed">__MOTOR_DEFAULT_SPEED__%</output>
      </label>
      <p id="motor-left-status" class="status" role="status">Получение состояния мотора…</p>
      <p class="status">Перед сменой направления нажмите «Стоп» и дождитесь остановки.</p>
    </section>
    <section>
      <h2>Правый</h2>
      <div class="color-buttons">
        <button id="motor-right-forward" type="button" disabled>Вперёд</button>
        <button id="motor-right-stop" type="button">Стоп</button>
        <button id="motor-right-reverse" type="button" disabled>Назад</button>
      </div>
      <label class="speed-row">
        <input id="motor-right-speed" type="range" min="0" max="100"
               value="__MOTOR_DEFAULT_SPEED__" aria-label="Скорость правый мотора" disabled>
        <output id="motor-right-speed-value" for="motor-right-speed">__MOTOR_DEFAULT_SPEED__%</output>
      </label>
      <p id="motor-right-status" class="status" role="status">Получение состояния мотора…</p>
      <p class="status">Перед сменой направления нажмите «Стоп» и дождитесь остановки.</p>
    </section>
  </main>

  <script>
    const ledButton = document.querySelector('#led-toggle');
    const ledStatus = document.querySelector('#led-status');
    const rgbButtons = document.querySelectorAll('.color-button');
    const rgbStatus = document.querySelector('#rgb-status');
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

    function showRgbState(result) {
      const enabled = [];
      const names = { red: 'Красный', green: 'Зелёный', blue: 'Синий' };

      rgbButtons.forEach((button) => {
        const isOn = result.rgb[button.dataset.color] === 'on';
        button.classList.toggle('is-on', isOn);
        button.setAttribute('aria-pressed', isOn ? 'true' : 'false');
        if (isOn) enabled.push(names[button.dataset.color]);
      });

      rgbStatus.textContent = enabled.length
        ? 'Включены: ' + enabled.join(', ')
        : 'Все цвета выключены';
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

    rgbButtons.forEach((button) => {
      button.addEventListener('click', async () => {
        const color = button.dataset.color;
        button.disabled = true;
        rgbStatus.textContent = 'Отправка команды…';

        try {
          const response = await fetch('/api/rgb/' + color + '/toggle', {
            method: 'GET',
            cache: 'no-store'
          });
          if (!response.ok) throw new Error('HTTP ' + response.status);
          showRgbState(await response.json());
        } catch (error) {
          console.error(error);
          rgbStatus.textContent = 'Не удалось связаться с Pico';
        } finally {
          button.disabled = false;
        }
      });
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

    async function loadRgbState() {
      try {
        const response = await fetch('/api/rgb/status', {
          method: 'GET',
          cache: 'no-store'
        });
        if (!response.ok) throw new Error('HTTP ' + response.status);
        showRgbState(await response.json());
      } catch (error) {
        console.error(error);
        rgbStatus.textContent = 'Не удалось получить состояние RGB';
      }
    }

    function setupMotor(side) {
      const motorForward = document.querySelector('#motor-' + side + '-forward');
      const motorReverse = document.querySelector('#motor-' + side + '-reverse');
      const motorStop = document.querySelector('#motor-' + side + '-stop');
      const motorSlider = document.querySelector('#motor-' + side + '-speed');
      const motorSpeedValue = document.querySelector('#motor-' + side + '-speed-value');
      const motorStatus = document.querySelector('#motor-' + side + '-status');
      let motorRequest = 0;

      function showMotorState(result) {
        motorSlider.value = result.speed;
        motorSpeedValue.value = result.speed + '%';
        motorSlider.disabled = !result.enabled;
        motorForward.disabled = !result.enabled || result.direction === 'reverse';
        motorReverse.disabled = !result.enabled || result.direction === 'forward';
        motorForward.setAttribute('aria-pressed', result.direction === 'forward');
        motorReverse.setAttribute('aria-pressed', result.direction === 'reverse');
        motorStatus.textContent = !result.enabled ? 'Модуль мотора отключён'
          : result.direction === 'stop' ? 'Мотор остановлен'
          : (result.direction === 'forward' ? 'Вперёд: ' : 'Назад: ') + result.speed + '%';
      }

      async function motorCommand(action) {
        const request = ++motorRequest;
        motorForward.disabled = true;
        motorReverse.disabled = true;
        motorSlider.disabled = true;
        // «Стоп» доступен даже во время запроса или после сетевой ошибки.
        try {
          const response = await fetch('/api/motor/' + side + '/' + action, { cache: 'no-store' });
          const result = await response.json();
          if (!response.ok) throw new Error(result.message || result.error);
          if (request === motorRequest) showMotorState(result);
        } catch (error) {
          console.error(error);
          if (request === motorRequest) {
            motorStatus.textContent = 'Команда не подтверждена. Нажмите «Стоп» для повторной связи.';
          }
        }
      }

      motorForward.addEventListener('click', () => motorCommand('forward'));
      motorReverse.addEventListener('click', () => motorCommand('reverse'));
      motorStop.addEventListener('click', () => motorCommand('stop'));
      motorSlider.addEventListener('input', () => {
        motorSpeedValue.value = motorSlider.value + '%';
      });
      motorSlider.addEventListener('change', () => motorCommand('speed/' + motorSlider.value));
      motorCommand('status');
    }

    setupMotor('left');
    setupMotor('right');
    loadFanState();
    loadRgbState();
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
        .replace("__MOTOR_DEFAULT_SPEED__", str(MOTOR_DEFAULT_SPEED))
    )
