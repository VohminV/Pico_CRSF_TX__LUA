-- LUA-скрипт для RadioMaster TX12MKII
-- Изменение мощности и частоты через CRSF

local options = {
    { "power", VALUE, 100, 10, 500 }, -- Мощность в милливаттах (10-500 мВт)
    { "frequency", VALUE, 868, 240, 960 } -- Частота в МГц (240-960 МГц)
}

-- CRSF-адреса и команды
local CRSF_DEVICE_ADDRESS = 0xEE -- Адрес устройства для передачи (примерный)
local CRSF_COMMAND_SET = 0x10   -- Команда настройки

-- Генерация CRSF-пакета
local function createCrsfPacket(power, frequency)
    local packet = { CRSF_DEVICE_ADDRESS, 0x06, CRSF_COMMAND_SET } -- Адрес, длина, команда

    -- Преобразование мощности (мВт) и частоты (МГц) в байты
    local power_low = bit32.band(power, 0xFF)
    local power_high = bit32.rshift(power, 8)
    local freq_low = bit32.band(frequency, 0xFF)
    local freq_high = bit32.rshift(frequency, 8)

    -- Добавление данных в пакет
    packet[#packet + 1] = power_low
    packet[#packet + 1] = power_high
    packet[#packet + 1] = freq_low
    packet[#packet + 1] = freq_high

    -- Вычисление CRC
    local crc = 0
    for _, byte in ipairs(packet) do
        crc = bit32.bxor(crc, byte)
    end
    packet[#packet + 1] = crc

    return packet
end

-- Отправка CRSF-пакета через передатчик
local function sendCrsfPacket(packet)
    local crsf = serial.openCRSF()
    if crsf then
        serial.writeCRSF(crsf, packet)
        serial.closeCRSF(crsf)
        return true
    else
        return false
    end
end

-- Главная функция скрипта
local function run(event)
    -- Получение текущих настроек
    local power = model.getGlobalVariable(1, 0) or 100 -- Глобальная переменная для мощности
    local frequency = model.getGlobalVariable(2, 0) or 868 -- Глобальная переменная для частоты

    -- Рисуем интерфейс
    lcd.clear()
    lcd.drawText(10, 10, "CRSF Настройки", MIDSIZE)
    lcd.drawText(10, 30, "Мощность (мВт):", 0)
    lcd.drawNumber(150, 30, power, 0)
    lcd.drawText(10, 50, "Частота (МГц):", 0)
    lcd.drawNumber(150, 50, frequency, 0)

    -- Управление настройками с помощью энкодера
    if event == EVT_ROT_LEFT then
        power = math.max(power - 10, 10)
    elseif event == EVT_ROT_RIGHT then
        power = math.min(power + 10, 500)
    elseif event == EVT_ENTER_BREAK then
        frequency = frequency + 1
    elseif event == EVT_EXIT_BREAK then
        frequency = frequency - 1
    end

    -- Сохранение настроек в глобальные переменные
    model.setGlobalVariable(1, 0, power)
    model.setGlobalVariable(2, 0, frequency)

    -- Формирование и отправка CRSF-пакета
    local packet = createCrsfPacket(power, frequency)
    if sendCrsfPacket(packet) then
        lcd.drawText(10, 70, "Пакет отправлен!", 0)
    else
        lcd.drawText(10, 70, "Ошибка отправки!", 0)
    end

    return 0
end

return { run=run, init=nil, background=nil, options=options }
