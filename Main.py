import network
import socket
import time
from machine import Pin, SPI, NVS
from sx127x import SX127x
import struct

# Настройки CRSF и LoRa
crsf_pin = Pin(16, Pin.IN)  # Пин для CRSF (полудуплекс)
spi = SPI(0, baudrate=1000000, polarity=0, phase=0, sck=Pin(2), mosi=Pin(3), miso=Pin(4))
lora = SX127x(spi, cs=Pin(5), reset=Pin(6), dio0=Pin(7))
nvs = NVS("lora_settings")  # NVS для сохранения настроек

# Константы CRSF
CRSF_DEVICE_ADDRESS = 0xEE
CRSF_COMMAND_SET = 0x10
CRSF_COMMAND_BIND = 0x20
DEFAULT_FREQUENCY = 868.0  # МГц
DEFAULT_POWER = 100  # мВт

# Функции для работы с NVS
def get_saved_settings():
    try:
        frequency = nvs.get_float("frequency")
        power = nvs.get_int("power")
        return frequency if frequency else DEFAULT_FREQUENCY, power if power else DEFAULT_POWER
    except:
        return DEFAULT_FREQUENCY, DEFAULT_POWER

def save_settings(frequency, power):
    nvs.set_float("frequency", frequency)
    nvs.set_int("power", power)
    nvs.commit()

# Установка начальных параметров
frequency, power = get_saved_settings()
lora.set_frequency(frequency)
lora.set_tx_power(power)
lora.set_spreading_factor(7)
lora.set_bandwidth(125000)
lora.set_coding_rate(5)
print(f"Начальная частота: {frequency} МГц, мощность: {power} мВт")

# Переключение пина CRSF между входом и выходом
def switch_to_receive():
    crsf_pin.init(Pin.IN)

def switch_to_transmit():
    crsf_pin.init(Pin.OUT)

# Прием CRSF-пакета
def receive_crsf_packet():
    switch_to_receive()
    time.sleep(0.01)  # Небольшая задержка для переключения

    data = bytearray()
    start_time = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start_time) < 100:  # Таймаут 100 мс
        if crsf_pin.value() == 0:  # Ждем начала передачи
            byte = 0
            for i in range(8):
                while crsf_pin.value() == 0:  # Ждем высокий уровень
                    pass
                time.sleep_us(58)  # Задержка для чтения середины бита
                if crsf_pin.value() == 1:
                    byte |= (1 << i)
                while crsf_pin.value() == 1:  # Ждем низкий уровень
                    pass
            data.append(byte)
            if len(data) >= 8 and data[-1] == 0:  # Проверка конца пакета
                break

    return data

# Отправка CRSF-пакета
def send_crsf_packet(packet):
    switch_to_transmit()
    time.sleep(0.01)  # Небольшая задержка для переключения

    for byte in packet:
        for i in range(8):
            crsf_pin.value(byte & (1 << i))
            time.sleep_us(58)  # Длительность бита
        time.sleep_us(100)  # Межбайтовый интервал

# Обработка CRSF-пакета
def process_crsf_packet(packet):
    if len(packet) < 6 or packet[0] != CRSF_DEVICE_ADDRESS:
        print("Неверный пакет")
        return

    if packet[2] == CRSF_COMMAND_SET and len(packet) >= 8:
        power = packet[3] | (packet[4] << 8)
        frequency = packet[5] | (packet[6] << 8)
        print(f"Получены новые параметры: мощность {power} мВт, частота {frequency / 10.0} МГц")

        # Применение новых параметров
        global lora
        lora.set_frequency(frequency / 10.0)
        lora.set_tx_power(power)
        save_settings(frequency / 10.0, power)

    elif packet[2] == CRSF_COMMAND_BIND:
        print("Получена команда биндинга")
        # Реализация логики биндинга (например, сохранение ID)
        bind_response = bytearray([CRSF_DEVICE_ADDRESS, 0x02, CRSF_COMMAND_BIND, 0x01])
        send_crsf_packet(bind_response)

# Главная функция TX-режима
def tx_mode():
    print("Режим передачи...")
    bind_packet = bytearray([CRSF_DEVICE_ADDRESS, 0x02, CRSF_COMMAND_BIND, 0x00])
    send_crsf_packet(bind_packet)
    print("Команда биндинга отправлена")

# Основной цикл
while True:
    print("Ожидание CRSF пакета...")
    packet = receive_crsf_packet()
    if packet:
        process_crsf_packet(packet)
    time.sleep(0.1)
