#!/usr/bin/env python3
"""
Тесты для ассемблера УВМ
Проверка соответствия тестам из спецификации
"""

import struct
from assembler import Assembler


def test_specification_examples():
    """Тесты из спецификации УВМ"""
    assembler = Assembler()
    
    print("ТЕСТЫ ИЗ СПЕЦИФИКАЦИИ УВМ\n")
    
    # Тест 1: CONST (A=42, B=125)
    print("1. Тест CONST (A=42, B=125):")
    print("   Ожидается: 0x6A, 0x1F, 0x00, 0x00")
    
    program = assembler.assemble("const 125")
    binary = assembler.to_binary(program)
    hex_bytes = ', '.join(f'0x{b:02X}' for b in binary)
    print(f"   Получено:  {hex_bytes}")
    print(f"   Совпадение: {hex_bytes == '0x6A, 0x1F, 0x00, 0x00'}\n")
    
    # Тест 2: LOAD (A=23, B=558)
    print("2. Тест LOAD (A=23, B=558):")
    print("   Ожидается: 0x97, 0x8B, 0x00, 0x00")
    
    program = assembler.assemble("load 558")
    binary = assembler.to_binary(program)
    hex_bytes = ', '.join(f'0x{b:02X}' for b in binary)
    print(f"   Получено:  {hex_bytes}")
    print(f"   Совпадение: {hex_bytes == '0x97, 0x8B, 0x00, 0x00'}\n")
    
    # Тест 3: STORE (A=1)
    print("3. Тест STORE (A=1):")
    print("   Ожидается: 0x01, 0x00, 0x00, 0x00")
    
    program = assembler.assemble("store")
    binary = assembler.to_binary(program)
    hex_bytes = ', '.join(f'0x{b:02X}' for b in binary)
    print(f"   Получено:  {hex_bytes}")
    print(f"   Совпадение: {hex_bytes == '0x01, 0x00, 0x00, 0x00'}\n")
    
    # Тест 4: BITREV (A=60)
    print("4. Тест BITREV (A=60):")
    print("   Ожидается: 0x3C, 0x00, 0x00, 0x00")
    
    program = assembler.assemble("bitrev")
    binary = assembler.to_binary(program)
    hex_bytes = ', '.join(f'0x{b:02X}' for b in binary)
    print(f"   Получено:  {hex_bytes}")
    print(f"   Совпадение: {hex_bytes == '0x3C, 0x00, 0x00, 0x00'}\n")


def test_bit_representation():
    """Проверка битового представления"""
    print("ПРОВЕРКА БИТОВОГО ПРЕДСТАВЛЕНИЯ\n")
    
    assembler = Assembler()
    
    # CONST 125
    program = assembler.assemble("const 125")
    binary = assembler.to_binary(program)
    value = struct.unpack('<I', binary)[0]
    
    print("CONST 125:")
    print(f"  Двоичное: {value:032b}")
    print(f"  A (биты 0-5):  {value & 0x3F:06b} = {value & 0x3F}")
    print(f"  B (биты 6-21): {(value >> 6) & 0xFFFF:016b} = {(value >> 6) & 0xFFFF}")
    print()


def test_assembler_features():
    """Тестирование возможностей ассемблера"""
    print("ТЕСТИРОВАНИЕ ВОЗМОЖНОСТЕЙ АССЕМБЛЕРА\n")
    
    assembler = Assembler()
    
    test_program = """
    ; Программа с разными форматами чисел
    const 100        ; Десятичное
    const 0x64       ; Шестнадцатеричное
    const 0b1100100  ; Двоичное
    const 0144       ; Восьмеричное
    
    ; Программа с метками
    start:
    const 42
    load start       ; Использование метки
    
    ; Все команды
    store
    bitrev
    """
    
    print("Исходный код:")
    print(test_program)
    print("\nПромежуточное представление:")
    
    program = assembler.assemble(test_program)
    print(assembler.format_intermediate(program))


if __name__ == '__main__':
    test_specification_examples()
    test_bit_representation()
    test_assembler_features()