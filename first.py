import pandas as pd

import re

pattern = re.compile(r'(?P<title>.*)\s+\((?P<section>.*)\)')
pattern2 = re.compile(r'.*for\s+(?P<teams>.*)')



def process(row):
    if match := pattern.match(row):
        result = match.groupdict()
        result['title_with_section'] = row
    elif match := pattern2.match(row):
        result = match.groupdict()
    else:
        result =  {'comment': row}

    return {**result, 'row': row}


goods = []
with open('crap.txt', 'rb') as f:
    for line in f:
        row = line.decode('utf-8').strip()
        if len(row) > 1:
            print(row)
            x = process(row)
            print(x)
            if 'title' in x.keys():
                goods.append(x)
            else:
                if len(goods) > 0:
                    goods[-1].update(x)



df = pd.DataFrame(goods)
print(df)
df.to_excel('sessions.xlsx')
