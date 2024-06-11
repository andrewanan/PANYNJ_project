import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate


#can't use db call since db is 24hrs behind.
#uncomment 
#file_path= input("Please enter file path for CSV: ")
#file_path = file_path[1:-1]

print("Press ENTER to continue.\n")
input("Please ensure flush converted only is named 'TRN-201 Transaction Research (1).csv'. ")

file_path= 'TRN-201 Transaction Research.csv'
file_path_degraded = 'TRN-001 Transaction Details.csv'
file_path_spurious = 'TRN-201 Transaction Research (1).csv'

df = pd.read_csv(file_path, skiprows=8, on_bad_lines='skip', low_memory=False)



df['Trx Tmst'] = pd.to_datetime(df['Trx Tmst'], errors='coerce')

#df['Hour'] = df['Trx Tmst'].dt.hour

df['Time'] = df['Trx Tmst'].dt.floor('15T')
df['Plaza'] = df['Plaza'].astype(str)
df['Resl'] = df['Resl'].astype(str)

#print(df.head())


total_images = df.pivot_table(index='Time', columns='Total Image', values='Plaza', aggfunc='count', fill_value=0)

total_images.loc['Total'] = total_images.sum()





#print(total_images)
first_trx = df['Trx Tmst'].min()
last_trx = df['Trx Tmst'].max()

print(f"\nTotal Images per Trx from {first_trx} to {last_trx}\n")
print(tabulate(total_images, headers = 'keys', tablefmt='github'))


df['Trx Tmst'] = pd.to_datetime(df['Trx Tmst'], errors='coerce')
df['HalfHour'] = df['Trx Tmst'].dt.floor('30T')

df['Plaza'].fillna('Unknown', inplace=True)
df['Resl'].fillna('Unknown', inplace=True)

#reverse flush
df_simplified = df[['Plaza', 'Resl', 'Trx Tmst']].copy()
filtered_reverse_flush = df_simplified[df_simplified['Plaza'].isin(['LT', 'GWBU'])]
filtered_reverse_flush = filtered_reverse_flush[filtered_reverse_flush['Resl'].isin(['FLUSH'])]

reverse_flush = filtered_reverse_flush.pivot_table(index='Plaza', columns='Resl', values='Plaza', aggfunc='count', fill_value=0)

print(f"\nReverse Flush from {first_trx} to {last_trx}\n")
print(tabulate(reverse_flush, headers='keys', tablefmt='github'))

#degraded
df1 = pd.read_csv(file_path_degraded, skiprows=8, on_bad_lines='skip', low_memory=False)

df1_simple = df1[['Plaza', 'Trx Tmst', 'Degraded']].copy()

degraded_transactions_filtered = df1_simple[df1_simple['Degraded'].isin(['Y', 'N'])]

degraded_transactions = degraded_transactions_filtered.pivot_table(index='Plaza', columns='Degraded', values='Plaza', aggfunc='count', fill_value=0)

print(f"\nDegraded Transactions (Y Value)\n")
print(tabulate(degraded_transactions, headers = 'keys', tablefmt='github'))


#spurious
df2 = pd.read_csv(file_path_spurious, skiprows=8, on_bad_lines='skip', low_memory=False)
df2_simple = df2[['Plaza', 'Trx Tmst', 'Md']].copy()

spurious_transactions = df2_simple.pivot_table(index='Plaza', columns='Md', values='Plaza', aggfunc='count', fill_value=0)

first_trx_s = df2_simple['Trx Tmst'].min()
last_trx_s = df2_simple['Trx Tmst'].max()

print(f"\nSpurious Values from {first_trx_s} to {last_trx_s} (E Values) \n")
print(tabulate(spurious_transactions, headers = 'keys', tablefmt='github'))