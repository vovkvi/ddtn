#!/usr/bin/env python3
# coding: utf-8

import os
import xml.etree.ElementTree as ET

from console import Console


output = []


def read_config(xml_path:str = None) -> dict:
    '''
    Функция для загрузки данных конфигурации из XML файла

    :param:
        xml_path - путь к XML файлу конфигурации

    :return:
        возращает данные из XML файла в виде словаря:

            dict(
                'cos' : float,
                'dU'  : int,
                'tk'  : list(
                    '+5' : float
                    ),
                'vl'  : list(
                            dict(
                                'descr'    : str,
                                'sechenie' : str
                            )
                        )
            )
    '''
    if xml_path == None:
        from  pkgutil import get_data
        lines = get_data('res','config.xml').decode('utf-8')
        root = ET.fromstring(lines)
    elif not os.path.exists(xml_path):
        print(Console.MSG_FAIL,'Конфигурационный файл не найден!')
        return
    else:
        root = ET.parse(xml_path).getroot()

    result = {
        'cos' : float(root.get('COS')),
        'dU'  : int(root.get('dU'))
    }
    for e in root:
        if e.tag == 'TK':
            result.setdefault('tk',{})
            for ch in e:
                t = ch.attrib['T']
                result['tk'][f'+{t}' if t[0] != '-' else t] = float(ch.attrib['K'])
        if e.tag == 'VL':
            result.setdefault('vl',[]).append({
                'descr'    : e.attrib.get('M'),
                'sechenie' : [(x.attrib.get('S'), x.attrib.get('I')) for x in e]
            })
    return result


def calculate(tk:dict, I:int, pr:int, cos:float, dU:float) -> dict:
    '''
    Функция для расчетов ДДТН, АДТН и мощности.

    :param:
        tk  (dict)  : словарь температурных коэффициентов
        I   (int)   : номинальный ток линии
        pr  (int)   : число проводов в фазе
        cos (float) : коэффициент мощности
        dU  (float) : отклонение напряжения от номинального

    :return:
        возвращает словарь с данными расчетов

        dict(
            'U'    : list(int),
            'rows' : dict(
                '-5' : list(int)
            )
        )
    '''
    U = (35, 110, 220, 330, 500)
    result = {
        'U'    : [round(i + ((i / 100) * dU)) for i in U],
        'rows' : {}
    }
    for key,kt in tk.items():
        result['rows'][key] = [
            round(I * kt * pr),      # ДДТН
            round(I * 1.2 * kt * pr) # АДТН
        ]
        result['rows'][key].extend([
            round((I * kt * x * 1.73 * cos)/1000) for x in result['U'] # P к U
        ])
    return result


def memo(*values):
    '''
    Функция для хранения и печати вывода других функций

    :param:
        values - строки переданные сюда будут добавлены в список
                 объедененной строкой с разделителем "пробел".
    '''
    output.append(' '.join([*values]))
    Console.clear()
    print('\n'.join(output))


def main():
    # читаем конфигурационный файл
    cfg = read_config()
    if cfg is None:
        return
    COS = cfg.get('cos')
    otkl_U = cfg.get('dU')

    # запрашиваем марку провода
    sel_m = Console.select([x['descr'] for x in cfg['vl']],'Доступные марки провода')
    memo(Console.MSG_OK, f'Марка провода: {sel_m[1]}')

    # запрашиваем сечение провода
    sel_v = Console.select([x[0] for x in cfg['vl'][sel_m[0]]['sechenie']], 'Доступные сечения провода')
    memo(Console.MSG_OK, f"Сечение провода: {sel_v[1]}")

    # получаем номинальный ток провода
    vl_I = cfg['vl'][sel_m[0]]['sechenie'][sel_v[0]][1]
    memo(Console.MSG_OK, f"Номинальный ток: {vl_I} А")

    # запрашиваем число проводов в фазе
    pr = 1
    sel = input(f"\nПроводов в фазе: {pr}. Это утверждение верно(Y/n): ")
    if not sel.upper() in ['', 'Y', 'YES']:
        pr = Console.input_to_int('Введите число проводов в фазе: ')
    memo(Console.MSG_OK, f"Проводов в фазе: {pr}")

    # запрашиваем отклонение напряжения
    strU = f'+{otkl_U}' if otkl_U >= 0 else str(otkl_U)
    sel = input(f"\nОтклонение U от Uном: {strU} %. Это утверждение верно(Y/n): ")
    if not sel.upper() in ['', 'Y', 'YES']:
        otkl_U = Console.input_to_int('Введите отклонение U (%): ')
    memo(Console.MSG_OK, f"Отклонение от Uном: {f'+{otkl_U} %' if otkl_U >= 0 else otkl_U}")

    # запрашиваем коэффициент мощности (cos φ)
    sel = input(f"\nКоэффициент мощности: {COS}. Это утверждение верно(Y/n): ")
    if not sel.upper() in ['', 'Y', 'YES']:
        COS = None
        while not isinstance(COS, float):
            input_str = input('Введите коэффициент мощности: ')
            try:
                COS = abs(float(input_str))
                COS = 0.99 if COS >= 1 else COS
            except:
                print(f'{Console.MSG_FAIL} {input_str} - не является допустимым значением.')
    memo(Console.MSG_OK, f"cos φ: {COS}")

    # проводим расчеты и печатаем результат
    calc = calculate(cfg['tk'], int(vl_I), pr, COS, otkl_U)
    print()
    print('+------+------+------+----------------------------------+\n' +
          '|      |      |      |    Мощность P, МВт при U, кВ     |\n' +
          '| T,°C | ДДТН | АДТН +------+------+------+------+------+\n' +
          '|      |      |      |' +
           str.join('', [f'{i:^6}|' for i in calc['U']]) + '\n' +
          '+------+------+------+------+------+------+------+------+'
        )
    color_rows = {
                '+5'  : Console.BG_CYAN,
                '+25' : Console.BG_YELLOW,
                '+35' : Console.BG_GREEN
                }
    for k,v in calc['rows'].items():
        tmp = f'|{k:^6}|' + ''.join([f'{e:^6}|' for e in v])
        print(f"{color_rows.get(k,'')}{tmp}{Console.RESET_ALL}")
    print(f'+------+------+------+------+------+------+------+------+\n')
    Console.println('\t  ', bg_color=color_rows['+5'] ,end=' - Зима')
    Console.println('\t  ', bg_color=color_rows['+25'],end=' - Номинал')
    Console.println('\t  ', bg_color=color_rows['+35'],end=' - Лето')
    print('\n')


if __name__ == '__main__':
    main()
