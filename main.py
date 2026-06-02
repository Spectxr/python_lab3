# 65% кода сгенерировано ИИ

from PIL import Image
import ast
import random
import os


def load_keys(filename):
    """Загрузка координат пикселей из файла ключей"""

    keys = []

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()

            if line:
                keys.append(ast.literal_eval(line))

    return keys


def text_to_bits(text):
    """Преобразование текста в битовую строку"""

    data = text.encode("utf-8")

    # Кодируем длину в 32-битную строку
    length_bits = format(len(data), "032b")

    message_bits = ""

    # Каждый байт преобразуется в 8 бит
    for byte in data:
        message_bits += format(byte, "08b")

    return length_bits + message_bits


def decode_text_from_image(image_path, keys_file):
    """1.1 Декодирование текста из закодированного сообщения"""

    img = Image.open(image_path).convert("RGB")
    pixels = img.load()

    keys = load_keys(keys_file)

    text = ""

    for x, y in keys:
        r, g, b = pixels[x, y]

        # Значение синего канала интерпретируем как ASCII-код символа
        text += chr(b)

    return text


def generate_keys(width, height, pixels_needed):
    """Генерация случайных неповторяющихся координат пикселей"""

    # Создаём список всех возможных координат и выбираем случайные
    keys = random.sample([(x, y) for x in range(width) for y in range(height)], pixels_needed)

    # Сохраняем ключи в текстовый файл
    with open("keys.txt", "w") as f:
        for x, y in keys:
            f.write(f"({x}, {y})\n")

    return keys


def encode_text_to_image(image_path, message):
    """1.2 Кодирование текста методом: b1-B, b0-B"""

    if not os.path.exists(image_path):
        print(f"\nОшибка: файл '{image_path}' не найден.")
        return

    img = Image.open(image_path).convert("RGB")
    pixels = img.load()

    # Получаем битовое представление сообщения
    bits = text_to_bits(message)

    width, height = img.size

    # Каждый пиксель хранит 2 бита, поэтому делим пополам и округляем вверх для нечётного количества бит
    pixels_needed = (len(bits) + 1) // 2

    keys = generate_keys(width, height, pixels_needed)

    with open("keys.txt", "w") as f:
        for x, y in keys:
            f.write(f"({x}, {y})\n")

    print("Первый символ:", message[0])
    print("Биты первого символа:", format(ord(message[0]), "08b"))

    print("\nИсходные значения пикселей:")
    pixel_index = 0
    for i in range(0, len(bits), 2):
        pair = bits[i:i + 2]

        # Если на последней итерации остался один бит, дополняем нулём справа
        if len(pair) < 2:
            pair += "0"
        x, y = keys[pixel_index]
        r, g, b = pixels[x, y]
        print(
            f"({x},{y}) -> "
            f"R={r} G={g} B={b}"
        )
        pixel_index += 1

    print("\nИзмененные значения пикселей:")
    pixel_index = 0
    for i in range(0, len(bits), 2):
        pair = bits[i:i + 2]
        if len(pair) < 2:
            pair += "0"
        x, y = keys[pixel_index]
        r, g, b = pixels[x, y]
        old_b = b

        # очищаем b1 и b0, 0b11111100 (252) сохраняет старшие 6 бит
        b = b & 0b11111100

        # записываем новые 2 бита в младшие позиции
        b = b | int(pair, 2)

        pixels[x, y] = (r, g, b)
        print(
            f"({x},{y}) -> "
            f"R={r} G={g} B={old_b}"
            f"  ==>  "
            f"R={r} G={g} B={b}"
        )
        pixel_index += 1

    img.save(image_path)
    print("\nСообщение успешно записано!")
    print("Файл сохранен как:", image_path)


def decode_hidden_text(image_path, keys_file):
    """1.2 Извлекает скрытое сообщение из изображения, читая по 2 бита из синего канала пикселей"""

    if not os.path.exists(image_path):
        print(f"\nОшибка: файл '{image_path}' не найден.")
        return ""

    if not os.path.exists(keys_file):
        print(f"\nОшибка: файл '{keys_file}' не найден.")
        return ""

    img = Image.open(image_path).convert("RGB")
    pixels = img.load()
    keys = load_keys(keys_file)

    # Собираем все биты из младших 2-х битов синего канала
    bits = ""

    for x, y in keys:
        _, _, b = pixels[x, y]

        # 0b11 (3) извлекает два младших бита, format(..., "02b") даёт 2-битное представление
        bits += format(b & 0b11, "02b")

    # первые 32 бита = длина сообщения
    message_length = int(bits[:32], 2)

    # Вычисляем границы битов собственно текста
    start = 32
    end = start + message_length * 8
    message_bits = bits[start:end]

    # Группируем биты по 8 и преобразуем в байты
    data = []
    for i in range(0, len(message_bits), 8):
        byte = message_bits[i:i + 8]
        data.append(int(byte, 2))

    # Декодируем байты в строку UTF-8
    return bytes(data).decode("utf-8")


def main():

    while True:
        print("\nМЕНЮ:")
        print("1 - Декодировать текст из изображения (п. 1.1)")
        print("2 - Закодировать текст в изображение (п. 1.2)")
        print("3 - Проверить декодирование (п. 1.2)")
        print("0 - Выход")
        choice = input("Выберите пункт: ")

        if choice == "1":
            image_path = "D:/учёба/python/lab3/new16.png"
            keys_file = "D:/учёба/python/lab3/keys16.txt"
            text = decode_text_from_image(image_path, keys_file)
            print("\nРезультат:")
            print(text)

        elif choice == "2":
            image_path = input("Исходное изображение: ")
            message = input("Введите сообщение: ")
            encode_text_to_image(image_path, message)

        elif choice == "3":
            image_path = input("Изображение: ")
            keys_file = "keys.txt"
            text = decode_hidden_text(image_path, keys_file)
            if text != "":
                print("\nИзвлеченное сообщение:")
                print(text)

        elif choice == "0":
            print("Работа завершена.")
            break

        else:
            print("Неверный пункт меню")


if __name__ == "__main__":
    main()
