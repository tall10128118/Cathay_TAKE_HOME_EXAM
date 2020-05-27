import pandas as pd 
import numpy as np 

CN_NUM  = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}

CN_UNIT = {
    '十' : 10,
    '拾' : 10,
    '百' : 100,
    '佰' : 100,
}
 
def chinese_to_arabic(cn:str) -> int:    
    unit = 0   # current
    ldig = []  # digest
    for cndig in reversed(cn):
        if cndig in CN_UNIT:
            unit = CN_UNIT.get(cndig)
            if unit == 10000 or unit == 100000000:
                ldig.append(unit)
                unit = 1
        else:
            dig = CN_NUM.get(cndig)
            if unit:
                dig *= unit
                unit = 0
            ldig.append(dig)
    if unit == 10:
        ldig.append(10)
    val, tmp = 0, 0
    for x in reversed(ldig):
        if x == 10000 or x == 100000000:
            val += tmp * x
            tmp = 0
        else:
            tmp += x
    val += tmp
    return val
 

df_a = pd.read_csv('C:/Users/DogHuang/Desktop/履歷/公司/國泰/csv/a_lvr_land_a.csv', encoding='utf8')
df_b = pd.read_csv('C:/Users/DogHuang/Desktop/履歷/公司/國泰/csv/b_lvr_land_a.csv', encoding='utf8')
df_e = pd.read_csv('C:/Users/DogHuang/Desktop/履歷/公司/國泰/csv/e_lvr_land_a.csv', encoding='utf8')
df_f = pd.read_csv('C:/Users/DogHuang/Desktop/履歷/公司/國泰/csv/f_lvr_land_a.csv', encoding='utf8')
df_h = pd.read_csv('C:/Users/DogHuang/Desktop/履歷/公司/國泰/csv/h_lvr_land_a.csv', encoding='utf8')

df_all = pd.concat( [df_a, df_b[1:], df_e[1:], df_f[1:], df_h[1:]], axis=0 )
df_all.drop(0,inplace=True)
df_all.to_csv( 'D:/Cathay_bank_HW/df_all.csv', index=False, encoding='utf_8_sig')

# ----------------------------------------------------------------------------------------------------------
total_floor_num = []
for i in df_all["總樓層數"]:
    try:
        total_floor_num.append(chinese_to_arabic( i.strip("層")))
    except:
        total_floor_num.append(0)

df_all["總樓層數"] = total_floor_num

# filter_a
mask1 = df_all["主要用途"]=="住家用"
mask2 = df_all["建物型態"]=="住宅大樓(11層含以上有電梯)"
mask3 = df_all["總樓層數"]  >= 13

filter_a = df_all.loc[ (mask1&mask2&mask3 ) ,:]
filter_a.to_csv( 'D:/Cathay_bank_HW/filter_a.csv', index=False, encoding='utf_8_sig')

# ----------------------------------------------------------------------------------------------------------
# filter_b
transaction_pen_number = []

for i in df_all["交易筆棟數"]:
    try:
       transaction_pen_number.append( int(i[-1]) ) 
    except:
        pass
  
df_all["車位總價元"] = df_all["車位總價元"].astype(int)
df_all["總價元"] = df_all["總價元"].astype(int)

filter_b = pd.DataFrame(  { '總件數':df_all.shape[1], '總車位數':sum(transaction_pen_number), '平均總價元':df_all["總價元"].mean(), '平均車位總價數':df_all["車位總價元"].mean() }, index = ['filter_b'])
filter_b.to_csv( 'D:/Cathay_bank_HW/filter_b.csv', index=False, encoding='utf_8_sig')
