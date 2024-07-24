import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate
import os
import shutil
import re
import seaborn as sns

#made by Andrew Anantharajah
#this code can be refactored, was learning as I went.

print("Please ensure flush converted only file is named 'TRN-201 Transaction Research (1).csv' and all files are stored in the same folder as the .py script\n")
input("Press ENTER to continue.\n")


file_path= 'TRN-201 Transaction Research.csv'
file_path_degraded = 'TRN-001 Transaction Details.csv'
file_path_spurious = 'TRN-201 Transaction Research (1).csv'

df = pd.read_csv(file_path, skiprows=8, on_bad_lines='skip', low_memory=False)



df['Trx Tmst'] = pd.to_datetime(df['Trx Tmst'], errors='coerce')

#df['Hour'] = df['Trx Tmst'].dt.hour

df['Time'] = df['Trx Tmst'].dt.floor('15T')
df['Plaza'] = df['Plaza'].astype(str)
df['Resl'] = df['Resl'].astype(str)

image_count_total = df['Total Image'].astype

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

#image correct by lane
df3 = df = pd.read_csv(file_path, skiprows=8, on_bad_lines='skip', low_memory=False)

#number of expected images per trx
correct_values = {
    'BB': 4,
    'GB': 4,
    'GWTR': 4,
    'OBX': 4,
    'GWBL': 6,
    'GWBU': 6,
    'HT': 6,
    'LT': 6
}


df3_filtered = df3[['Plaza', 'Lane', 'Total Image', 'Trx Tmst']].copy()

df3_filtered.loc[:, 'Total Image'] = pd.to_numeric(df3_filtered['Total Image'], errors='coerce')

df3_filtered.loc[:, 'Matching Images'] = df3_filtered.apply(lambda row: row['Total Image'] == correct_values.get(row['Plaza'], None), axis=1)

lane_correct_data = df3_filtered.groupby(['Plaza', 'Lane']).agg(
    Total_images = ('Total Image', 'size'),
    Correct_Image_Count = ('Matching Images', 'sum')
).reset_index()

print(f"\nTotal Image Values Per Lane from {first_trx_s} to {last_trx_s}\n")

lane_correct_data['Correct Ratio (%)'] = lane_correct_data['Correct_Image_Count'] / lane_correct_data['Total_images'] * 100

table = tabulate(lane_correct_data, headers='keys', tablefmt='github', showindex=False)

print(table)

input("\nPress ENTER to view detailed Problem Plazas & Lanes Photos per Trx (<95% Correct Ratio)\n")

#tables for <95% correct ratio (Plaza + Lane hourly breakdown)
problem_lane = lane_correct_data[lane_correct_data['Correct Ratio (%)'] < 95]

df3['Total Image'] = pd.to_numeric(df3['Total Image'], errors='coerce')
df3['Trx Tmst'] = pd.to_datetime(df3['Trx Tmst'], errors='coerce')

def create_pivot_table(plaza,lane):
    problem_lane = df3[(df3['Plaza'] == plaza) & (df3['Lane'] == lane)].copy()
    problem_lane.loc[:,'Trx Tmst'] = problem_lane['Trx Tmst'].dt.floor('15T')

    problem_lane_final = problem_lane.pivot_table(index='Trx Tmst', columns='Total Image', values='Plaza', aggfunc='count', fill_value=0)
    problem_lane_final.loc['Total'] = problem_lane_final.sum()

    return problem_lane_final


pivot_tables = {}

for _, row in problem_lane.iterrows():
    plaza = row['Plaza']
    lane = row['Lane']
    pivot_table = create_pivot_table(plaza, lane)
    pivot_tables[(plaza, lane)] = pivot_table


for (plaza, lane), pivot_table in pivot_tables.items():
    print(f"\nTotal Images Per Trx for {plaza} Lane {lane}\n")
    print(tabulate(pivot_table, headers='keys', tablefmt='github', showindex=True))

    #Remove total row
    pivot_table = pivot_table[pivot_table.index != 'Total']

    #line graph
    pivot_table.reset_index(inplace=True)
    pivot_table_melted = pivot_table.melt(id_vars=['Trx Tmst'], var_name='Total Images', value_name='Count')
    custom_palette = sns.color_palette("husl", n_colors=len(pivot_table_melted['Total Images'].unique())) #custom pallete because default is hard to distinguish from one another
    sns.lineplot(data=pivot_table_melted, x='Trx Tmst', y='Count', hue='Total Images', palette=custom_palette)
    plt.title(f'Total Images Per Trx Over Time for {plaza} Lane {lane}')
    plt.xlabel('Transaction Time')
    plt.ylabel('Count')
    plt.legend(title='Total Images')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def move_files():
    while True:
        try: 
            date = input('Enter date for spotcheck (YYYYMMDD): ')
        except ValueError:
            print("Date Format Not Recognized\n")
            continue
        if re.match(r"^\d{8}$", date):
            break
        print("Invalid date format. Please use YYYYMMDD.\n")

    while True:
        try:
            spotcheck_number = input('Is this Spotcheck 1, 2, or 3?\n')
        except ValueError:
            print("Please enter 1, 2 or 3.\n")
        if spotcheck_number in [ '1', '2', '3\n']:
            break
        print("Please enter 1, 2, or 3.\n")

    folder_name = f"{date}_SC{spotcheck_number}"
    os.makedirs(folder_name, exist_ok=True)

    shutil.move(file_path, os.path.join(folder_name, os.path.basename(file_path)))
    shutil.move(file_path_spurious, os.path.join(folder_name, os.path.basename(file_path_spurious)))
    shutil.move(file_path_degraded, os.path.join(folder_name, os.path.basename(file_path_degraded)))

    print(f"Files have been moved to: {folder_name}")


response = (input("\nDo you want to move files to historical folder?\nPress ENTER for Yes."))


if response in ['Y', 'y', 'yes', 'YES', 'Yes', ""]:
    move_files()

else:
    print("Files not moved.")

