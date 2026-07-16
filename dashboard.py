import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set_theme(style='dark')

# TOTAL ORDER & REVENUE
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_date').agg({
        'order_id': 'nunique',
        'total_price': 'sum'
    })
    daily_orders_df = daily_orders_df.reset_index();
    daily_orders_df.rename(columns={
        'order_id': 'order_count',
        'total_price': 'revenue'
    }, inplace=True)

    return daily_orders_df

# HIGHEST & LOWEST SALES
def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_name").quantity_x.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

# CUSTOMER DEMOGRAPHY

## By Gender
def create_by_gender_df(df):
    by_gender_df = df.groupby(by='gender').customer_id.nunique().sort_values(ascending=False).reset_index()
    by_gender_df.rename(columns={
        'customer_id': 'customer_count'
    }, inplace=True)

    return by_gender_df

## By Age Group
def create_by_age_df(df):
    by_age_df = df.groupby(by='age_group').customer_id.nunique().sort_values(ascending=False).reset_index()
    by_age_df.rename(columns={
        'customer_id': 'customer_count'
    }, inplace=True)

    return by_age_df

## By State Group
def create_by_state_df(df):
    by_state_df = df.groupby(by='state').customer_id.nunique().sort_values(ascending=False).reset_index()
    by_state_df.rename(columns={
        'customer_id': 'customer_count'
    }, inplace=True)

    return by_state_df

# RFM
def create_rfm_df(df):
    rfm_df = df.groupby('customer_id', as_index=False).agg({
        'order_date': 'max',
        'order_id': 'nunique',
        'total_price': 'sum'
    })

    rfm_df.columns = ['customer_id', 'max_order_timestamp', 'frequency', 'monetary']

    rfm_df['max_order_timestamp'] = rfm_df['max_order_timestamp'].dt.date
    recent_date = df['order_date'].dt.date.max()
    rfm_df['recency'] = rfm_df['max_order_timestamp'].apply(lambda x: (recent_date - x).days)
    rfm_df.drop('max_order_timestamp', axis=1, inplace=True)

    return rfm_df

# IMPORT LIBRARY
all_df = pd.read_csv('all_data.csv')

# DATETIME COLUMN
datetime_col = ['order_date', 'delivery_date']
all_df.sort_values(by='order_date', inplace=True)
all_df.reset_index(inplace=True)

for col in datetime_col:
    all_df[col] = pd.to_datetime(all_df[col])

# COMPONENT FILTER
min_date = all_df['order_date'].min()
max_date = all_df['order_date'].max()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df['order_date'] >= str(start_date)) & (all_df['order_date'] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
by_gender_df = create_by_gender_df(main_df)
by_age_df = create_by_age_df(main_df)
by_state_df = create_by_state_df(main_df)
rfm_df = create_rfm_df(main_df)

st.header('Dicoding Collection Dashboard :sparkles:')

# TOTAL ORER & REVENUE
st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), 'AUD', locale='es_CO')
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df['order_date'],
    daily_orders_df['order_count'],
    marker='o',
    linewidth=2,
    color='#90CAF9'
)

ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

# HIGHEST & LOWEST SALES
st.subheader("Best & Worst Performing Product")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x='quantity_x', y='product_name', data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of sales", fontsize=30)
ax[0].set_title('Best Performing Product', loc='center', fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x='quantity_x', y='product_name', data=sum_order_items_df.sort_values(by='quantity_x', ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position('right')
ax[1].yaxis.tick_right()
ax[1].set_title('Worst Performing Product', loc='center', fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

# CUSTOMER DEMOGRAPHY
st.subheader('Customer Demographics')
col1, col2 = st.columns(2)

## Gender
with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(
        y='customer_count',
        x='gender',
        data=by_gender_df.sort_values(by='customer_count', ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title('Number of customer by gender', loc='center', fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

## Age
with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(
        y='customer_count',
        x='age_group',
        data=by_age_df.sort_values(by='customer_count', ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title('Number of customer by age', loc='center', fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

## State
fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x='customer_count',
    y='state',
    data=by_state_df.sort_values(by='customer_count', ascending=False),
    palette=colors,
    ax=ax
)
ax.set_title('Number of customer by state', loc='center', fontsize=50)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=35)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)

st.subheader("Best Customer Based on RFM Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric('Average recency (days)', value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric('Average frequency', value=avg_frequency)

with col3:
    avg_monetary = round(rfm_df.monetary.mean(), 3)
    st.metric('Average monetary', value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(y='recency', x='customer_id', data=rfm_df.sort_values(by='recency', ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel('customer_id', fontsize=30)
ax[0].set_title('By Recency (days)', loc='center', fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(y='frequency', x='customer_id', data=rfm_df.sort_values(by='frequency', ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel('customer_id', fontsize=30)
ax[1].set_title('By frequency', loc='center', fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

sns.barplot(y='monetary', x='customer_id', data=rfm_df.sort_values(by='monetary', ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel('customer_id', fontsize=30)
ax[2].set_title('By monetary', loc='center', fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)

st.pyplot(fig)

st.caption('Copyright (c) Dicoding 2023')