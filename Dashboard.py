import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Menggunakan raw string (r"") atau mengganti backslash (\) dengan double backslash (\\) pada path file CSV
day_df = pd.read_csv("day_data.csv")
hour_df = pd.read_csv("hour_data.csv")

def get_total_count_by_hour_df(hour_df):
    # Mengelompokkan DataFrame berdasarkan kolom "hours" dan menghitung total sum untuk kolom "total user"
    hour_count_df = hour_df.groupby(by="hour").agg({"total_users": ["sum"]})
    # Mengembalikan DataFrame yang berisi total count untuk setiap jam
    return hour_count_df

def count_by_day_df(day_df):
    day_df_count_2011 = day_df.query(str('date >= "2011-01-01" and date < "2012-12-31"'))
    return day_df_count_2011

def total_registered_df(day_df):
   reg_df =  day_df.groupby(by="date").agg({
      "registered": "sum"
    })
   reg_df = reg_df.reset_index()
   reg_df.rename(columns={
        "registered": "register_sum"
    }, inplace=True)
   return reg_df

def total_casual_df(day_df):
   cas_df =  day_df.groupby(by="date").agg({
      "casual": ["sum"]
    })
   cas_df = cas_df.reset_index()
   cas_df.rename(columns={
        "casual": "casual_sum"
    }, inplace=True)
   return cas_df

def create_seasonly_users_df(df):
    seasonly_users_df = df.groupby(["season", "year"]).agg({
        "total_users": "sum"
    })
    seasonly_users_df = seasonly_users_df.reset_index()
    seasonly_users_df['season'] = pd.Categorical(seasonly_users_df['season'],
                                             categories=['Spring', 'Summer', 'Fall', 'Winter'])
    seasonly_users_df = seasonly_users_df.sort_values('season')
    return seasonly_users_df

def sum_order (hour_df):
    sum_order_items_df = hour_df.groupby("hour").total_users.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

datetime_columns = ["date"]
day_df.sort_values(by="date", inplace=True)
day_df.reset_index(inplace=True)   

hour_df.sort_values(by="date", inplace=True)
hour_df.reset_index(inplace=True)

for column in datetime_columns:
    day_df[column] = pd.to_datetime(day_df[column])
    hour_df[column] = pd.to_datetime(hour_df[column])

min_date_days = day_df["date"].min()
max_date_days = day_df["date"].max()

min_date_hour = hour_df["date"].min()
max_date_hour = hour_df["date"].max()

with st.sidebar:
    st.title('Data Penyewaan Sepeda')
    st.image("https://thumbs.dreamstime.com/z/bike-sharing-services-icon-vector-outline-illustration-sign-color-symbol-184331518.jpg")
start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date_days,
        max_value=max_date_days,
        value=[min_date_days, max_date_days])

main_df_day = day_df[(day_df["date"] >= str(start_date)) & 
                       (day_df["date"] <= str(end_date))]

main_df_hour = hour_df[(hour_df["date"] >= str(start_date)) & 
                        (hour_df["date"] <= str(end_date))]

hour_count_df = get_total_count_by_hour_df(main_df_hour)
day_df_count_2011 = count_by_day_df(main_df_day)
reg_df = total_registered_df(main_df_day)
cas_df = total_casual_df(main_df_day)
sum_order_items_df = sum_order(main_df_hour)
season_df = create_seasonly_users_df(main_df_day)

st.header('Bike Sharing Data')

st.subheader('Daily Sharing')
col1, col2, col3 = st.columns(3)
 
with col1:
    total_orders = day_df_count_2011.total_users.sum()
    st.metric("Total Sharing Bike", value=total_orders)

with col2:
    total_sum = reg_df.register_sum.sum()
    st.metric("Total Registered", value=total_sum)

with col3:
    total_sum = cas_df.casual_sum.sum()
    st.metric("Total Casual", value=total_sum)

st.subheader("Performa penjualan perusahaan dalam beberapa tahun terakhir")

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    day_df["date"],
    day_df["total_users"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

st.subheader("pada jam berapa yang paling banyak dan paling sedikit disewa?")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
sns.barplot(x="hour", y="total_users", data=sum_order_items_df.head(5), palette=["#90CAF9","#D3D3D3", "#D3D3D3",  "#D3D3D3", "#D3D3D3"], ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Hours (PM)", fontsize=30)
ax[0].set_title("Jam dengan banyak penyewa sepeda", loc="center", fontsize=30)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x="hour", y="total_users", data=sum_order_items_df.sort_values(by="hour", ascending=True).head(5), palette=["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3","#90CAF9"], ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Hours (AM)",  fontsize=30)
ax[1].set_title("Jam dengan sedikit penyewa sepeda", loc="center", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)
st.subheader("musim apa yang paling banyak disewa?")

colors = ["#D3D3D3", "#D3D3D3","#90CAF9", "#D3D3D3", ]
fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(
        y="total_users", 
        x="season",
        data=season_df.sort_values(by="season", ascending=False),
        palette=colors,
        ax=ax
    )
ax.set_title("Grafik Antar Musim", loc="center", fontsize=50)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=35)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)

st.subheader("Perbandingan Customer yang Registered dengan casual")

labels = 'casual', 'registered'
sizes = [18.8, 81.2]
explode = (0, 0.1) 

fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',colors=["#D3D3D3", "#90CAF9"],
        shadow=True, startangle=90)
ax1.axis('equal')  

st.pyplot(fig1)
