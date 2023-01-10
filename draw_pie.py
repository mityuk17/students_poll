
from matplotlib import pyplot
import os
def get_value(a):
    return f'{round(a,2)}%'
def draw(data: list, chat_id:int):
    high, medium, low = 0, 0, 0
    for row in data:
        if 'Высокая удовлетворённость' in row:
            high += 1
        elif 'Средняя удовлетворённость' in row:
            medium += 1
        elif 'Низкая удовлетворённсть' in row:
            low += 1
    a = [[high,'Высокая\nудовлетворённость'],[medium, 'Средняя\nудовлетворённость'],[low,'Низкая\nудовлетворённсть']]
    pyplot.pie([i[0] for i in a if i[0]], labels=[i[1] for i in a if i[0]],
               autopct=get_value)
    if not os.path.exists('plots'):
        os.mkdir('plots')
    pyplot.savefig(f'plots/{chat_id}.png')