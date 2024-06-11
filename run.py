import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate

#can't use db call since db is 24hrs behind.
#uncomment 
#file_path= input("Please enter file path for CSV: ")
#file_path = file_path[1:-1]

file_path= 'TRN-201 Transaction Research.csv'
file_path_degraded = 'TRN-001 Transaction Details.csv'

df = pd.read_csv(file_path, skiprows=8, on_bad_lines='skip')



df['Trx Tmst'] = pd.to_datetime(df['Trx Tmst'], errors='coerce')

#df['Hour'] = df['Trx Tmst'].dt.hour

df['HalfHour'] = df['Trx Tmst'].dt.floor('30T')
df['Plaza'] = df['Plaza'].astype(str)
df['Resl'] = df['Resl'].astype(str)

#print(df.head())


total_images = df.pivot_table(index='HalfHour', columns='Total Image', values='Plaza', aggfunc='count', fill_value=0)

total_images.loc['Total'] = total_images.sum()

#print(total_images)
print("\nTotal Images per Trx\n")
print(tabulate(total_images, headers = 'keys', tablefmt='github'))


df['Trx Tmst'] = pd.to_datetime(df['Trx Tmst'], errors='coerce')
df['HalfHour'] = df['Trx Tmst'].dt.floor('30T')

df['Plaza'].fillna('Unknown', inplace=True)
df['Resl'].fillna('Unknown', inplace=True)

#simplified df for 1d
df_simplified = df[['Plaza', 'Resl', 'Trx Tmst']].copy()
filtered_reverse_flush = df_simplified[df_simplified['Plaza'].isin(['LT', 'GWBU'])]

reverse_flush = filtered_reverse_flush.pivot_table(index='Plaza', columns='Resl', values='Plaza', aggfunc='count', fill_value=0)

print("\nReverse Flush\n")
print(tabulate(reverse_flush, headers='keys', tablefmt='github'))

#degraded
df1 = pd.read_csv(file_path_degraded, skiprows=8, on_bad_lines='skip', low_memory=False)

df1_simple = df1[['Plaza', 'Trx Tmst', 'Degraded']].copy()

degraded_transactions_filtered = df1_simple[df1_simple['Degraded'].isin(['Y', 'N'])]

degraded_transactions = degraded_transactions_filtered.pivot_table(index='Plaza', columns='Degraded', values='Plaza', aggfunc='count', fill_value=0)

print("\nDegraded Transactions\n")
print(tabulate(degraded_transactions, headers = 'keys', tablefmt='github'))



