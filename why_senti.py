import pandas as pd

senti_df = pd.read_csv('./data/senti_df.csv',sep="\t")
test = senti_df.head(20)
test.to_csv('./test.csv',index=False, sep='\t')
