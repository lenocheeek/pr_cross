#!/usr/bin/env python3
"""
Ассемблер для учебной виртуальной машины (УВМ)
Вариант №23
Этап 1: Перевод программы в промежуточное представление
"""

import sys
import struct
from enum import IntEnum
from typing import List, Tuple, Optional, Dict, Any


class Opcode(IntEnum):
    """Коды операций УВМ"""
    STORE = 1      # Запись значения в память
    LOAD = 23      # Чтение значения из памяти
    CONST = 42     # Загрузка константы
    BITREV = 60    # Унарная операция bitreverse()


class Assembler:
    """Ассемблер УВМ"""
    
    # Словарь мнемоник
    MNEMONICS = {
        'store': Opcode.STORE,
        'load': Opcode.LOAD,
        'const': Opcode.CONST,
        'bitrev': Opcode.BITREV,
    }
    
    def __init__(self):
        self.program: List[Dict[str, Any]] = []
        self.labels: Dict[str, int] = {}
        self.current_address = 0
        
    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Разбор строки ассемблера"""
        # Удаляем комментарии
        if ';' in line:
            line = line.split(';')[0]
        
        line = line.strip()
        if not line:
            return None
            
        # Проверяем метку
        if line.endswith(':'):
            label = line[:-1].strip()
            if label in self.labels:
                raise ValueError(f"Повторное объявление метки '{label}'")
            self.labels[label] = self.current_address
            return None
            
        # Разделяем мнемонику и аргументы
        parts = line.split()
        if not parts:
            return None
            
        mnemonic = parts[0].lower()
        
        if mnemonic not in self.MNEMONICS:
            raise ValueError(f"Неизвестная мнемоника '{mnemonic}'")
            
        opcode = self.MNEMONICS[mnemonic]
        args = parts[1:] if len(parts) > 1 else []
        
        # Формируем промежуточное представление команды
        cmd = {
            'address': self.current_address,
            'opcode': opcode,
            'mnemonic': mnemonic,
            'args': args,
            'raw_line': line
        }
        
        # Валидация аргументов
        if opcode == Opcode.CONST:
            if len(args) != 1:
                raise ValueError(f"CONST требует 1 аргумент: {line}")
            try:
                value = self.parse_number(args[0])
                if not (0 <= value <= 0xFFFF):  # 16-битное значение
                    raise ValueError(f"Константа вне диапазона: {value}")
                cmd['value'] = value
            except ValueError:
                # Возможно, это метка - обработаем позже
                cmd['label'] = args[0]
                
        elif opcode == Opcode.LOAD:
            if len(args) != 1:
                raise ValueError(f"LOAD требует 1 аргумент: {line}")
            try:
                addr = self.parse_number(args[0])
                if not (0 <= addr <= 0xFFFFFF):  # 24-битный адрес
                    raise ValueError(f"Адрес вне диапазона: {addr}")
                cmd['address_arg'] = addr
            except ValueError:
                cmd['label'] = args[0]
                
        elif opcode == Opcode.STORE:
            if len(args) != 0:
                raise ValueError(f"STORE не принимает аргументов: {line}")
                
        elif opcode == Opcode.BITREV:
            if len(args) != 0:
                raise ValueError(f"BITREV не принимает аргументов: {line}")
                
        self.current_address += 1  # Каждая команда = 1 слово (4 байта)
        return cmd
    
    def parse_number(self, s: str) -> int:
        """Парсинг чисел в различных форматах"""
        s = s.strip().lower()
        
        if s.startswith('0x'):  # Шестнадцатеричное
            return int(s[2:], 16)
        elif s.startswith('0b'):  # Двоичное
            return int(s[2:], 2)
        elif s.startswith('0o'):  # Восьмеричное
            return int(s[2:], 8)
        else:  # Десятичное
            return int(s)
    
    def assemble(self, source: str) -> List[Dict[str, Any]]:
        """Ассемблирование исходного кода"""
        self.program = []
        self.labels = {}
        self.current_address = 0
        
        lines = source.split('\n')
        
        # Первый проход: сбор меток и промежуточное представление
        for line_num, line in enumerate(lines, 1):
            try:
                cmd = self.parse_line(line)
                if cmd:
                    self.program.append(cmd)
            except ValueError as e:
                raise ValueError(f"Строка {line_num}: {e}")
        
        # Второй проход: разрешение меток
        for cmd in self.program:
            if 'label' in cmd:
                label = cmd['label']
                if label not in self.labels:
                    raise ValueError(f"Неизвестная метка '{label}'")
                
                if cmd['opcode'] == Opcode.CONST:
                    cmd['value'] = self.labels[label]
                    del cmd['label']
                elif cmd['opcode'] == Opcode.LOAD:
                    cmd['address_arg'] = self.labels[label]
                    del cmd['label']
        
        return self.program
    
    def encode_instruction(self, cmd: Dict[str, Any]) -> bytes:
        """Кодирование команды в бинарное представление"""
        opcode = cmd['opcode']
        
        if opcode == Opcode.CONST:
            value = cmd.get('value', 0)
            # A=42 в битах 0-5, константа в битах 6-21
            encoded = (value << 6) | opcode
            return struct.pack('<I', encoded)
            
        elif opcode == Opcode.LOAD:
            addr = cmd.get('address_arg', 0)
            # A=23 в битах 0-5, адрес в битах 6-29
            encoded = (addr << 6) | opcode
            return struct.pack('<I', encoded)
            
        elif opcode == Opcode.STORE:
            # A=1 в битах 0-5
            return struct.pack('<I', opcode)
            
        elif opcode == Opcode.BITREV:
            # A=60 в битах 0-5
            return struct.pack('<I', opcode)
            
        else:
            raise ValueError(f"Неизвестный opcode: {opcode}")
    
    def to_binary(self, program: List[Dict[str, Any]]) -> bytes:
        """Преобразование программы в бинарный формат"""
        binary = b''
        for cmd in program:
            binary += self.encode_instruction(cmd)
        return binary
    
    def format_intermediate(self, program: List[Dict[str, Any]]) -> str:
        """Форматирование промежуточного представления для отладки"""
        result = []
        for cmd in program:
            addr = cmd['address']
            mnemonic = cmd['mnemonic'].upper()
            args = cmd.get('args', [])
            
            if mnemonic == 'CONST':
                value = cmd.get('value', 0)
                result.append(f"[{addr:04d}] {mnemonic} {value} (0x{value:X})")
                # Показываем битовое представление как в спецификации
                a_bits = f"{Opcode.CONST:06b}"
                b_bits = f"{value:016b}"
                result.append(f"  A биты 0-5: {a_bits} = {Opcode.CONST}")
                result.append(f"  B биты 6-21: {b_bits} = {value}")
                
            elif mnemonic == 'LOAD':
                addr_arg = cmd.get('address_arg', 0)
                result.append(f"[{addr:04d}] {mnemonic} {addr_arg} (0x{addr_arg:X})")
                a_bits = f"{Opcode.LOAD:06b}"
                b_bits = f"{addr_arg:024b}"
                result.append(f"  A биты 0-5: {a_bits} = {Opcode.LOAD}")
                result.append(f"  B биты 6-29: {b_bits} = {addr_arg}")
                
            elif mnemonic == 'STORE':
                result.append(f"[{addr:04d}] {mnemonic}")
                a_bits = f"{Opcode.STORE:06b}"
                result.append(f"  A биты 0-5: {a_bits} = {Opcode.STORE}")
                
            elif mnemonic == 'BITREV':
                result.append(f"[{addr:04d}] {mnemonic}")
                a_bits = f"{Opcode.BITREV:06b}"
                result.append(f"  A биты 0-5: {a_bits} = {Opcode.BITREV}")
            
            result.append("")
        
        return '\n'.join(result)


def main():
    """Точка входа CLI"""
    if len(sys.argv) < 3:
        print("Использование: python assembler.py <input.asm> <output.bin> [--test]")
        print("  --test  Режим тестирования (вывод промежуточного представления)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    test_mode = '--test' in sys.argv
    
    try:
        # Чтение исходного файла
        with open(input_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Ассемблирование
        assembler = Assembler()
        program = assembler.assemble(source)
        
        if test_mode:
            # Вывод промежуточного представления
            print("=== ПРОМЕЖУТОЧНОЕ ПРЕДСТАВЛЕНИЕ ===")
            print(assembler.format_intermediate(program))
            print("\n=== БИНАРНОЕ ПРЕДСТАВЛЕНИЕ (hex) ===")
            
        # Генерация бинарного файла
        binary = assembler.to_binary(program)
        
        # Вывод бинарного представления в тестовом режиме
        if test_mode:
            for i in range(0, len(binary), 4):
                chunk = binary[i:i+4]
                hex_str = ', '.join(f'0x{b:02X}' for b in chunk)
                print(f"Слово {i//4}: [{hex_str}]")
        
        # Запись в файл
        with open(output_file, 'wb') as f:
            f.write(binary)
            
        print(f"Успешно! Скомпилировано {len(program)} команд в {output_file}")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()