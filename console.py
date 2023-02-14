#!/usr/bin/env python3
# coding: utf-8
'''
Простой класс для более комфортной разработки терминальных приложений
на Python. Позволяет использовать ASCII последовательности для отобра-
жения цвета в терминале на Linux/Windows. Также реализованы функции
очисти вывода, диалога выбора элемента из списка, проверки ввода и
преобразования данных.

(c) Vitalii Vovk, 2022
'''
import os
from datetime import datetime


if os.name == 'nt':
    os.system('color')


class Console(object):

    # константы цвета текста
    TXT_BLACK      = '\033[30;22m'
    TXT_RED        = '\033[31;22m'
    TXT_GREEN      = '\033[32;22m'
    TXT_YELLOW     = '\033[33;22m'
    TXT_BLUE       = '\033[34;22m'
    TXT_MAGENTA    = '\033[35;22m'
    TXT_CYAN       = '\033[36;22m'
    TXT_WHITE      = '\033[37;22m'
    TXT_BR_RED     = '\033[31;1m'
    TXT_BR_GREEN   = '\033[32;1m'
    TXT_BR_YELLOW  = '\033[33;1m'
    TXT_BR_BLUE    = '\033[34;1m'
    TXT_BR_MAGENTA = '\033[35;1m'
    TXT_BR_CYAN    = '\033[36;1m'
    TXT_BR_WHITE   = '\033[37;1m'
    TXT_RESET      = '\033[39;22m'

    # константы цвета фона
    BG_BLACK       = '\033[40;22m'
    BG_RED         = '\033[41;22m'
    BG_GREEN       = '\033[42;22m'
    BG_YELLOW      = '\033[43;22m'
    BG_BLUE        = '\033[44;22m'
    BG_MAGENTA     = '\033[45;22m'
    BG_CYAN        = '\033[46;22m'
    BG_WHITE       = '\033[47;22m'
    BG_RESET       = '\033[49;22m'

    # константа сброса цвета текста и фона
    RESET_ALL      = f'\033[0m'

    # константы информационных сообщений
    MSG_OK         = f'[+] {TXT_BR_GREEN}OK:{RESET_ALL}'
    MSG_WARN       = f'[!] {TXT_BR_YELLOW}WARNING:{RESET_ALL}'
    MSG_FAIL       = f'[-] {TXT_BR_RED}ERROR:{RESET_ALL}'
    MSG_INFO       = f'[i] {TXT_BR_CYAN}INFO:{RESET_ALL}'
    MSG_STATUS     = f'[ ]'
    MSG_TIME       = f'{MSG_STATUS} {TXT_BR_MAGENTA}{datetime.now().strftime("%H:%M:%S")}:{RESET_ALL}'


    @classmethod
    def println(cls, text:str = '', txt_color:str = None, bg_color:str = None, end='\n'):
        '''
        Печатает строку с заданными цветами текста и фона.

        :param:
            text      (str) : текст вывода
            txt_color (str) : цвет текста
            bg_color  (str) : цвет фона
            end       (str) : последовательность.строка для замены
                              символа переноса строки

        :return:
            str : форматированная строка
        '''
        txt_color = cls.TXT_RESET if txt_color is None else txt_color
        bg_color = cls.BG_RESET if bg_color is None else bg_color
        print(f'{bg_color}{txt_color}{text}{cls.RESET_ALL}',end=end)

    @classmethod
    def print_head(cls, text = None, sym:str = '*', length:int = 48, txt_color:str = None, bg_color:str = None) -> str:
        '''
        Печатает "шапку" сообщения/диалога с заданными шириной и цветом.

        :param:
            text      (str) : текст заголовка
            sym       (str) : символ для формирования рамки заголовка
            length    (int) : ширина рамки заголовка
            txt_color (str) : цвет текста
            bg_color  (str) : цвет фона

        :return:
            str : форматированная строка заголовка
        '''
        txt_color = cls.TXT_RESET if txt_color is None else txt_color
        bg_color = cls.BG_RESET if bg_color is None else bg_color
        text = str(text).center(length - len(sym) -1)
        delim = ''.ljust(length, sym)
        print(f'{bg_color}{txt_color}{delim}\n{sym}{text}{sym}\n{delim}\n{cls.RESET_ALL}')

    @classmethod
    def clear(cls, new_text = None):
        '''
        Очищает ранее выведенный в терминал текст и печатает заданную строку.

        :param:
            new_text (str) : текст который будет выведен после очистки
        '''
        os.system('cls||clear')
        print(cls.RESET_ALL, end='')
        if new_text is not None:
            print(new_text)

    @classmethod
    def input_to_int(cls, title:str = 'Выберите номер:') -> int:
        '''
        Запрашивает у пользователя ввод и преобразует его в целое число

        :param:
            title (str) : текст диалога ввода

        :return:
            int : целое число на основе введенных данных
        '''
        while True:
            input_str = input(f'\n{title}').strip()
            if input_str.isnumeric():
                return int(input_str)
            elif input_str in ('', None):
                return 0
            else:
                print(f'{cls.MSG_FAIL} {input_str} - не является допустимым значением.')

    @classmethod
    def select(cls, items:list, header:str = 'Список элементов') -> tuple:
        '''
        Выводит диалог выбора элемента из списка

        :param:
            items  (list) : список элементов
            header (str)  : заголовок диалога выбора

        :return:
            tuple(int, item) : возвращает кортеж содержащий номер
                               элемента списка и сам элемент.
        '''
        cls.print_head(header)
        itms_length = len(items)
        for i,v in enumerate(items):
            pos = str(i).center(len(str(itms_length))+2)
            print(f'[{cls.TXT_MAGENTA}{pos}{cls.RESET_ALL}] {v}')
        while True:
            num = cls.input_to_int()
            if num >= itms_length:
                cls.print_err(f'Число не может быть быть больше {itms_length-1}.')
            elif num < 0:
                cls.print_err(f'Число не может отрицательным.')
            else:
                return num, items[num]
