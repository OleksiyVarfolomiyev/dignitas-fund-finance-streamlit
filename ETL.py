import pandas as pd
#import import_ipynb
import data_aggregation_tools as da

def format_money(value):
    if abs(value) >= 1e6:
        return '{:.2f}M'.format(value / 1e6)
    elif abs(value) >= 1e3:
        return '{:.2f}K'.format(value / 1e3)
    else:
        return '{:.2f}'.format(value)

def read_txs():
    dtypes = { 'UAH': 'float', 'Category': 'str' }

    large_donations_by_category = pd.read_csv('data/large_donations_by_category.csv', dtype=dtypes, parse_dates=['Date'])
    large_spending_by_category = pd.read_csv('data/large_spending_by_category.csv', dtype=dtypes, parse_dates=['Date'])

    donations_below_large_by_category = pd.read_csv('data/donations_below_large_by_category.csv', dtype=dtypes, parse_dates=['Date'])
    spending_below_large_by_category = pd.read_csv('data/spending_below_large_by_category.csv', dtype=dtypes, parse_dates=['Date'])

    donations_total = pd.read_csv('data/donations_total.csv', dtype=dtypes, parse_dates=['Date'])
    spending_total =  pd.read_csv('data/spending_total.csv', dtype=dtypes, parse_dates=['Date'])

    donations_total_by_category = pd.read_csv('data/donations_total_by_category.csv', dtype=dtypes, parse_dates=['Date'])
    spending_total_by_category = pd.read_csv('data/spending_total_by_category.csv', dtype=dtypes, parse_dates=['Date'])

    donations_total_by_category = pd.read_csv('data/donations_total_by_category.csv', dtype=dtypes, parse_dates=['Date'])
    spending_total_by_category = pd.read_csv('data/spending_total_by_category.csv', dtype=dtypes, parse_dates=['Date'])

    return large_donations_by_category, large_spending_by_category, donations_below_large_by_category, spending_below_large_by_category, \
        donations_total, spending_total, donations_total_by_category, spending_total_by_category


def read_data(nrows = None):
    dtypes = { 'UAH': 'float', 'To Account': 'str', 'From Account': 'str', 'Category': 'str', 'Subcategory': 'str', 'Commentary': 'str'}

    if nrows:
            df = pd.read_csv('./data/ExportEN.csv', dtype=dtypes, nrows=nrows, index_col=None, parse_dates=['Date'])
    else:
            df = pd.read_csv('./data/ExportEN.csv', dtype=dtypes, index_col=None, parse_dates=['Date'])

    df['Subcategory'] = df['Subcategory'].fillna('')
    df['Category'] = df['Category'].fillna('')

    return df

def convert_to_USD(df, UA_USD_exchange_rate):
    df['UAH'] = df['UAH']/UA_USD_exchange_rate
    return df

def replace_category(data, column, value):
    """Replace Category with Subcategory"""
    df_copy = data.copy()  # Create a copy of the DataFrame to avoid modifying the original
    df_copy.loc[df_copy[column] == value, 'Category'] = df_copy['Subcategory']
    return df_copy

def replace_category_values(data, category_column, val1, val2):
    """Mapping of Category values"""
    df_copy = data.copy()
    df_copy[category_column] = df_copy[category_column].replace(val1, val2)
    return df_copy

def extract_relevant_txs(df, start_date, end_date):
    """Main category mapping module"""
    # spending
    ds = df[df['From Account'].notna()]; ds = ds.drop(['To Account'], axis=1)

    # donations
    df = df[df['To Account'].notna()]; df = df.drop(['From Account'], axis=1)

    #if (start_date != None) | (end_date != None):
    #    df = df[df['Date'] >= start_date]
    #    ds = ds[ds['Date'] >= start_date]
        #df = df[df['Date'] <= end_date]
        #ds = ds[ds['Date'] <= end_date]

    df['Commentary'] = df['Commentary'].astype(str)
    ds['Commentary'] = ds['Commentary'].astype(str)
    df = df[~df['Commentary'].str.contains('Переказ між рахунками організації')]
    ds = ds[~ds['Commentary'].str.contains('Переказ між рахунками організації')]
    df = df[~df['Commentary'].str.contains('Гривнi вiд продажу')]
    ds = ds[~ds['Commentary'].str.contains('Списання коштiв на здiйснення валютно-обмiнних операцiй')]
    #df = df[df['Category'] != 'Transfer']
    #ds = ds[ds['Category'] != 'Transfer']
    ds = ds[ds['Category'] != 'Продаж валюти']

    ds = replace_category(ds, 'Category', 'Закупівлі')
    df = replace_category(df, 'Category', 'Донати')
    df = replace_category(df, 'Category', 'Гранти')
    df = replace_category(df, 'Category', 'Income categories')
    #df = replace_category(df, 'Category', 'Загальні донати')

    old_values = ['Taxes', 'ремонт Авто', 'Юридичні послуги', 'Salary']
    ds = replace_category_values(ds, 'Category', old_values, 'Адмін')

    df = df.drop(['Subcategory'], axis=1)
    ds = ds.drop(['Subcategory'], axis=1)

    df['Category'] = df['Category'].str.replace('Адмін Донати', 'Адмін')
    df['Category'] = df['Category'].str.replace('Донати ', '')

    #mask = (df['To Account'] == 'ПриватБанк Люті пташки')
    #df.loc[mask, 'Category'] = 'Люті пташки'
    mask = (df['To Account'] == 'Приват 1000 дронів для України')
    df.loc[mask, 'Category'] = '1000 дронів для України'

    mask = (df['To Account'] == 'Вікторі Дронс')
    df.loc[mask, 'Category'] = 'Victory Drones'
    mask = (df['To Account'] == 'ПриватБанк Загальний рахунок зборів')
    df.loc[mask, 'Category'] = 'Загальні донати'
    mask = df['To Account'] == 'Приват Загальний рахунок зборів'
    df.loc[mask, 'Category'] = 'Загальні донати'

    mask = (df['To Account'] == 'ПриватБанк PLN')
    df.loc[mask, 'Category'] = 'Загальні донати'

    mask = df['To Account'] == 'ПриватБанк Адмін рахунок'
    df.loc[mask, 'Category'] = 'Адмін'
    mask = ds['From Account'] == 'ПриватБанк Адмін рахунок'
    ds.loc[mask, 'Category'] = 'Адмін'

    mask = df['To Account'] == 'Приват Літай'
    df.loc[mask, 'Category'] = 'Літай'

    mask = df['To Account'] == 'Приват На захисті краси України'
    df.loc[mask, 'Category'] = 'На захисті краси України'

    ds['Category'] = ds['Category'].str.replace('техніки Літай', 'Літай')
    ds['Category'] = ds['Category'].str.replace('Закупівлі на захисті краси', 'На захисті краси України')
    ds['Category'] = ds['Category'].str.replace('Закупівля ', '')
    ds['Category'] = ds['Category'].str.replace('Дрони Люті пташки', 'Люті пташки')
    ds['Category'] = ds['Category'].str.replace('Адміністративні витрати', 'Адмін')
    df['Category'] = df['Category'].str.replace('Грант МЛПК', 'МЛПК')
    # ds['Category'] = ds['Category'].str.replace('Канцелярія', 'Адмін')
    # ds['Category'] = ds['Category'].str.replace('Комісія банку', 'Адмін')
    # ds['Category'] = ds['Category'].str.replace('обладнання', 'Обладнання')

    mask = ds['From Account'] == 'Приват Банк Адмін рахунок'
    ds.loc[mask, 'Category'] = 'Адмін'
    mask = ds['From Account'] == 'Вікторі Дронс'
    ds.loc[mask, 'Category'] = 'Victory Drones'
    mask = ds['From Account'] == 'Приват Літай'
    ds.loc[mask, 'Category'] = 'Літай'
    mask = ds['From Account'] == 'Приват На захисті краси України'
    ds.loc[mask, 'Category'] = 'На захисті краси України'

    ds = ds.drop(['From Account'], axis=1)
    df = df.drop(['To Account'], axis=1)

    condition = ds['Category'].str.contains('|'.join(['Лопати', 'Антени', 'Піротехніка', 'Планшети']), case=False)
    ds.loc[condition, 'Category'] = 'Лопати + Антени + Піротехніка + Планшети'

    ds['Category'] = ds['Category'].str.replace('Suppliers and Contractors', 'Адмін')

    mask = df['Commentary'].str.contains('люті пташки', case=False, na=False)
    df.loc[mask, 'Category'] = 'Люті пташки'
    mask = df['Commentary'].str.contains('MOBILE LAUNDRY SHOWER UNITS', case=False, na=False)
    df.loc[mask, 'Category'] = 'МЛПК'
    mask = df['Commentary'].str.contains('From UK ONLINE GIVING FOUNDATION', case=False, na=False)
    df.loc[mask, 'Category'] = 'Загальні донати'
    mask = ds['Category'].str.contains('Канцелярія', case=False, na=False)
    ds.loc[mask, 'Category'] = 'Адмін'
    mask = ds['Category'].str.contains('обладнання', case=False, na=False)
    ds.loc[mask, 'Category'] = 'Обладнання'
    mask = ds['Category'].str.contains('Комісія банку', case=False, na=False)
    ds.loc[mask, 'Category'] = 'Адмін'

    # save preppped data to csv
    #df.to_csv('data/donations.csv', index=False)
    #ds.to_csv('data/spending.csv', index=False)
    df = df.drop(['Commentary'], axis=1)
    ds = ds.drop(['Commentary'], axis=1)

    donations_total_by_category = df.groupby(['Date', 'Category']).sum().reset_index()
    donations_total_by_category.to_csv('data/donations_total_by_category.csv', index=False)

    spending_total_by_category = ds.groupby(['Date', 'Category']).sum().reset_index()
    spending_total_by_category.to_csv('data/spending_total_by_category.csv', index=False)

    donations_total = df.drop('Category', axis=1).groupby('Date').sum().reset_index()

    donations_total.to_csv('data/donations_total.csv', index=False)

    spending_total = ds.drop('Category', axis=1).groupby('Date').sum().reset_index()
    spending_total.to_csv('data/spending_total.csv', index=False)

    # above 100k UAH
    amount = 100000
    large_donations = df[df['UAH'] >= amount].fillna('')
    large_donations_by_category = large_donations.groupby(['Date', 'Category']).sum().reset_index()
    large_donations_by_category.to_csv('data/large_donations_by_category.csv', index=False)

    large_spending = ds[ds['UAH'] >= amount].fillna('')
    large_spending_by_category = large_spending.groupby(['Date', 'Category']).sum().reset_index()
    large_spending_by_category.to_csv('data/large_spending_by_category.csv', index=False)

    # below 100k UAH
    donations_below_large_by_category = df[df.UAH < amount]
    spending_below_large_by_category = ds[ds.UAH < amount]

    donations_below_large_by_category = donations_below_large_by_category.groupby(['Date', 'Category']).sum().reset_index()
    spending_below_large_by_category = spending_below_large_by_category.groupby(['Date', 'Category']).sum().reset_index()

    donations_below_large_by_category.to_csv('data/donations_below_large_by_category.csv', index=False)
    spending_below_large_by_category.to_csv('data/spending_below_large_by_category.csv', index=False)

def extract_top_donors(large_donations, amount):
    """Top donors by amount"""
    # remove numbers from the Commentary
    large_donations['Commentary'] = large_donations['Commentary'].str.replace(r'\d+', '', regex=True)
    large_donations = large_donations[~large_donations.apply(lambda row: row.astype(str).str.contains('продажу валюти').any(), axis=1)]
    large_donations = large_donations[~large_donations.apply(lambda row: row.astype(str).str.contains('Луценко Ігор Вікторович').any(), axis=1)]
    # extract donor names from the Commentary
    mask = large_donations['Commentary'].str.contains('РУШ', na=False)
    large_donations.loc[mask, 'Commentary'] = 'eva.ua'
    mask = large_donations['Commentary'].str.contains('КОНСАЛТИНГОВА ГРУПА', na=False)
    large_donations.loc[mask, 'Commentary'] = 'КОНСАЛТИНГОВА ГРУПА \"A-95\"'
    mask = large_donations['Commentary'].str.contains('UNITED HELP UKRAINE', na=False)
    large_donations.loc[mask, 'Commentary'] = 'UNITED HELP UKRAINE'
    mask = large_donations['Commentary'].str.contains('АМІК УКРАЇНА', na=False)
    large_donations.loc[mask, 'Commentary'] = 'АМІК УКРАЇНА'
    mask = large_donations['Commentary'].str.contains('Торгович Оксана Станіславівна', na=False)
    large_donations.loc[mask, 'Commentary'] = 'Приват Банк'
    mask = large_donations['Commentary'].str.contains('РО \"УКУ УГКЦ\"', na=False)
    large_donations.loc[mask, 'Commentary'] = 'РО \"УКУ УГКЦ\"'
    mask = large_donations['Commentary'].str.contains('ФОНД \"ДЯКУЮ ТОБІ\"', na=False)
    large_donations.loc[mask, 'Commentary'] = 'БФ \"ДЯКУЮ ТОБІ\"'
    mask = large_donations['Commentary'].str.contains('ТОВ "ФК \"ЕВО\"', na=False)
    large_donations.loc[mask, 'Commentary'] = 'ТОВ "ФК \"ЕВО\"'

    # sum donations by donor
    top_donors = pd.DataFrame(large_donations.groupby('Commentary')['UAH'].sum())
    # filter over 1M UAH donors
    top_donors = top_donors[top_donors['UAH'] >= amount]
    top_donors = top_donors.sort_values('UAH', ascending = False)
    top_donors = pd.DataFrame(top_donors['UAH'].apply(format_money))
    top_donors = top_donors.reset_index().rename(columns={'Commentary': 'Top Donors'})

    return top_donors
