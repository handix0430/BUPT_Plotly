import pandas as pd

df = pd.read_excel('CUP_SNAP_HISTORYRECORD.xlsx')

for i in range(0,7,2):
    print(df.columns[i])