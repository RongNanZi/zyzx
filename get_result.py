import pandas as pd
import re
from collections import Counter

def get_list_kv(re_path, sentence):
    wanted = {}
    re_expressions = pd.read_csv(re_path)['re'].values
    k = 1
    for re_expression in re_expressions:
        finds = re.findall(re_expression, sentence)
        if finds:
            if len(finds[0]) == 2:
                for v in finds:
                    name1 = '套餐{}名称'.format(k)
                    name3 = '套餐{}还剩余'.format(k)
                    k+=1
                    wanted.update({name1:v[0],name3:v[1]})
            elif len(finds[0]) == 3:
                for v in finds:
                    name1 = '套餐{}名称'.format(k)
                    name2 = '套餐{}已使用'.format(k)
                    name3 = '套餐{}还剩余'.format(k)
                    k+=1
                    wanted.update({name1:v[0], name2:v[1],name3:v[2]})
    return wanted


def get_kv(re_path, sentence):
    wanted = []
    re_csv = pd.read_csv(re_path)
    for i in re_csv.index:
        re_expression = re_csv.loc[i]['re']
        find = re.search(re_expression, sentence)
        if find:
            key = re_csv.loc[i]['key']
            cn_key = re_csv.loc[i]['cn_key']
            #shengjian's regular expression's group name is cn_key
            if key.startswith('jsheng'):
                value = find.group(cn_key)
            else:
                value = find.group(key)
                
            wanted.append({'find': find, \
                           'key': key, \
                           'cn_key': cn_key, \
                           'value': value, \
                          'level': re_csv.loc[i]['level']})
    return wanted

def get_result(sentence,kre_path, kre_list_path = None):

    #the output is dict object
    if kre_list_path is not None:
        list_kv = get_list_kv(kre_list_path, sentence)
    else:
        list_kv ={}
    #the output is a dict list
    kv = get_kv(kre_path, sentence)
    
    if len(kv) == 0:
        return list_kv
    kv_df = pd.DataFrame(kv)
    #selected level higher values
    def get_level(df):
        if df.shape[0]< 2:
            return df
        level_values = df.sort_values("level",ascending=False)['level'].values
        return df[df.level == level_values[0]]
    kv_df = kv_df.groupby(['cn_key']).apply(get_level)
    
    #vote same (cn_key, value) ,drop other cn_key but not same values
    def vote(df):
        if df.shape[0]< 3:
            return df
        all_values = df['value'].values
        if len(all_values) == len(set(all_values)):
            return df
        v_c = Counter(all_values)
        most_v = v_c.most_common(1)
        return df[df.value==most_v[0][0]]
    kv_df = kv_df.groupby('cn_key').apply(vote)
    
    # drop the same (cn_key, value) item 
    kv_df = kv_df.drop_duplicates(['cn_key', 'value'])
    
    cn_key_list = kv_df['cn_key'].values
    
    #if all (cn_key, value) is unique, return result
    if len(cn_key_list) == len(set(cn_key_list)):
        re_r =  dict(zip(kv_df['cn_key'].values, kv_df['value'].values))
        re_r.update(list_kv)
        return re_r
    
    #choose  min length find when cn_key is same
    def get_minlen_find(df):
        find_length = [len(str(item)) for item in df['find'].values]
        df['find_length'] = find_length
        min_len = min(find_length)
        return df[df.find_length == min_len]
    kv_df= kv_df.groupby('cn_key').apply(get_minlen_find)
    
    #if all (cn_key, value) is unique, return result
    cn_key_list = kv_df['cn_key'].values
    if len(cn_key_list) == len(set(cn_key_list)):
        re_r =  dict(zip(kv_df['cn_key'].values, kv_df['value'].values))
        re_r.update(list_kv)
        return re_r
   
    #choose  min length value when cn_key is same
    def get_minlen_value(df):
        find_length = [len(str(item)) for item in df['value'].values]
        df['value_length'] = find_length
        min_len = min(find_length)
        return df[df.value_length == min_len]
    kv_df= kv_df.groupby(['cn_key']).apply(get_minlen_value)
    
    re_r =dict(zip(kv_df['cn_key'].values, kv_df['value'].values))
    re_r.update(list_kv)
    return re_r