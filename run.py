import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate
import os
import glob

#can't use db call since db is 24hrs behind.
#uncomment 
#file_path= input("Please enter file path for CSV: ")
#file_path = file_path[1:-1]

file_path='C:/Users/aanantharajah/Downloads/internProject/TRN-201 Transaction Research.csv'

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
print("Total Images per Trx\n")
print(tabulate(total_images, headers = 'keys', tablefmt='github'))



dtype_spec = {
    'Plaza': str,
    'Resl': str,
}

df['Trx Tmst'] = pd.to_datetime(df['Trx Tmst'], errors='coerce')
df['HalfHour'] = df['Trx Tmst'].dt.floor('30T')

df['Plaza'].fillna('Unknown', inplace=True)
df['Resl'].fillna('Unknown', inplace=True)

#simplified df for 1d
df_simplified = df[['Plaza', 'Resl', 'Trx Tmst']].copy()

reverse_flush = df_simplified.pivot_table(index='Plaza', columns='Resl', values='Plaza', aggfunc='count', fill_value=0)

print("\nReverse Flush\n")
print(tabulate(reverse_flush, headers='keys', tablefmt='github'))


