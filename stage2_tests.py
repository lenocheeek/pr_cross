#!/usr/bin/env python3
"""Тесты для этапа 2"""
from assembler import Assembler

def test_stage2():
    assembler = Assembler()
    
    # Простая проверка
    source = "const 125\nload 558\nstore\nbitrev"
    program = assembler.assemble(source)
    binary = assembler.to_binary(program)
    
    print(f"Компилировано команд: {len(program)}")
    print(f"Размер бинарного файла: {len(binary)} байт")
    
    # Проверка первых 4 команд
    expected = bytes([0x6A, 0x1F, 0x00, 0x00, 0x97, 0x8B, 0x00, 0x00, 
                      0x01, 0x00, 0x00, 0x00, 0x3C, 0x00, 0x00, 0x00])
    
    if binary[:16] == expected:
        print("✓ Машинный код соответствует спецификации")
    else:
        print("✗ Ошибка в машинном коде")

if __name__ == '__main__':
    test_stage2()
