from FindKey import FindKey
import pandas as pd
from collections import Counter
data = pd.read_excel('D:/CMOS/zyzx/data/test.xlsx', sheet_name='流量类')
sms = data['短信原文'].values
a = FindKey(sms)
print('='*100+'frequency'+'='*100)
print(a.freq.most_common(100))
b = a.get_inner()
print('='*100+'inner'+'='*100)
print(Counter(b).most_common(100))
c = a.get_free()
print('='*100+'free'+'='*100)
print(Counter(c).most_common(100))
df = pd.DataFrame()
df['token'] = b.keys()
df['inner'] = b.values()

df['free'] = [0]*df.shape[0]
for i in df.index:
    df.loc[i, 'free'] = c[df.loc[i, 'token']]

min_inner, max_inner = min(df['inner']), max(df['inner'])
min_free, max_free = min(df['free']), max(df['free'])
df['inner'] = (df['inner']-min_inner)/(max_inner - min_inner)
df['free'] = (df['free']-min_free)/(max_free - min_free)
df['score'] = df['inner'] * df['free']
print(df.sort_values(by=['score'], ascending= False)[:1000] )

df.to_csv('test.csv', index=False)
