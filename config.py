"""Параметры проекта, которые обычно требуется менять пользователю."""

# Имя и пароль точки доступа Wi-Fi.
WIFI_SSID = "Network Name"
WIFI_PASSWORD = "Network Password"

# Сетевое имя контроллера. Если роутер и компьютер поддерживают mDNS/DHCP
# hostname, устройство можно будет найти в сети по этому имени.
DEVICE_HOSTNAME = "maxpico"

# TCP-порт HTTP-сервера. Порт 80 удобен тем, что его не нужно указывать в URL.
WEB_PORT = 80

# Кнопка подключается между этим GPIO и GND. Внешний резистор не нужен:
# button.py включает внутреннюю подтяжку входа к питанию.
BUTTON_PIN = 16

# Возвращаем проверенную схему: PWM подаётся только на INA, а INB постоянно
# удерживается в нуле обычным цифровым выходом.
FAN_INA_PIN = 1
FAN_INB_PIN = 2

# 20 кГц соответствует проверенному примеру и находится выше слышимого
# диапазона. Пользователь выбирает скорость 0–100%, а драйвер скрыто переводит
# её в рабочий диапазон заполнения PWM от 60 до 100%.
FAN_PWM_FREQUENCY = 20000
FAN_MIN_DUTY_PERCENT = 60
FAN_DEFAULT_SPEED = 50

# RGB-светодиод подключён катодами каналов к GPIO, поэтому он работает с
# инверсной логикой: уровень 1 выключает канал, а уровень 0 включает его.
RGB_RED_PIN = 20
RGB_GREEN_PIN = 19
RGB_BLUE_PIN = 18

# Максимальное время одной попытки подключения к Wi-Fi, в секундах.
WIFI_CONNECT_TIMEOUT = 15

# После неудачи фоновая задача повторяет подключение через этот интервал.
WIFI_RETRY_INTERVAL = 15

# Оба мотора доступны по умолчанию; при загрузке остановлены.
# Первый (левый) мотор.
MOTOR_ENABLED = True
MOTOR_AIN1_PIN = 3
MOTOR_AIN2_PIN = 4
# Второй (правый) мотор.
MOTOR_RIGHT_AIN1_PIN = 5
MOTOR_RIGHT_AIN2_PIN = 6
MOTOR_PWM_FREQUENCY = 20000
MOTOR_DEFAULT_SPEED = 50

if MOTOR_ENABLED:
    _motor_pins = (MOTOR_AIN1_PIN, MOTOR_AIN2_PIN,
                   MOTOR_RIGHT_AIN1_PIN, MOTOR_RIGHT_AIN2_PIN)
    if len(set(_motor_pins)) != 4:
        raise ValueError("Motor GPIO pins must not overlap")
    if set(_motor_pins) & {FAN_INA_PIN, FAN_INB_PIN}:
        raise ValueError("Motor and fan GPIO pins must not overlap")
