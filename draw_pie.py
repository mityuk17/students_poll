import matplotlib
import numpy as np
import pandas as pd
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
    pyplot.savefig(f'plots/pie_{chat_id}.png')
def draw2(data : list, chat_id : int):
    month = {1:'Янв.',2:'Февр.', 3: "Март", 4: "Апр.", 5:"Май", 6: "Июнь", 7: "Июль", 8: "Авг.", 9 : "Сент.", 10 : "Окт.", 11 : "Нояб.", 12: "Дек."}

    line_low = [i[1] for i in data]
    line_medium = [i[2] for i in data]
    line_high = [i[3] for i in data]
    x_values = [month[i[0]] for i in data]
    x_axis = np.arange(0,len(data),1)
    massiv = {
        'Низкая удовлетворённость' : line_low,
        'Средняя удовлетворённость' : line_medium,
        'Высокая удовлетворённоть' : line_high
    }
    df = pd.DataFrame(massiv)
    df.plot(kind = 'bar')
    pyplot.xticks(x_axis, x_values)
    pyplot.savefig(f'plots/bar_{chat_id}.png')