import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np

# -------------------------------
# 1. CONNECT TO FIREBASE
# -------------------------------

cred = credentials.Certificate("retailpulseai-e2a4a-firebase-adminsdk-fbsvc-a29aa4fe45.json")

firebase_admin.initialize_app(cred, {
    "databaseURL": "https://retailpulseai-e2a4a-default-rtdb.firebaseio.com/"
})

ref = db.reference("billing_records")
data = ref.get()

records = []

# -------------------------------
# 2. CONVERT FIREBASE DATA → DATAFRAME
# -------------------------------

if data:

    for key, value in data.items():

        for item in value["items"]:

            records.append({
                "date": value["date"],
                "time": value["time"],
                "product": item["productName"],
                "quantity": item["quantity"],
                "total": item["total"],
                "customer": value["customerID"]
            })

else:
    print("No data found in Firebase")
    exit()

df = pd.DataFrame(records)

print("Data Loaded Successfully")
print(df.head())

# -------------------------------
# 3. DAILY SALES REPORT
# -------------------------------

daily_sales = df.groupby("date")["total"].sum().reset_index()

print("\nDaily Sales")
print(daily_sales)

fig1 = px.line(
    daily_sales,
    x="date",
    y="total",
    title="Daily Revenue",
    template="plotly_dark",
    markers=True
)

fig1.update_traces(line=dict(color="cyan", width=4), name="Revenue")
fig1.show()

# -------------------------------
# 4. MONTHLY REVENUE GRAPH
# -------------------------------

df["date"] = pd.to_datetime(df["date"])

df["month"] = df["date"].dt.month_name()

monthly_sales = df.groupby("month")["total"].sum().reset_index()

fig2 = px.bar(
    monthly_sales,
    x="month",
    y="total",
    title="Monthly Revenue",
    template="plotly_dark"
)

fig2.update_traces(marker_color="dodgerblue", name="Revenue")
fig2.show()

# -------------------------------
# 5. BEST SELLING PRODUCTS
# -------------------------------

best_products = df.groupby("product")["quantity"].sum().reset_index()

fig3 = px.bar(
    best_products,
    x="product",
    y="quantity",
    title="Best Selling Products",
    template="plotly_dark"
)

fig3.update_traces(marker_color="deepskyblue", name="Sales Volume")
fig3.show()

# -------------------------------
# 6. LOW PERFORMING PRODUCTS
# -------------------------------

low_products = best_products.sort_values(by="quantity").head(5)

fig4 = px.bar(
    low_products,
    x="product",
    y="quantity",
    title="Low Performing Products",
    template="plotly_dark"
)

fig4.update_traces(marker_color="red", name="Low Sales")
fig4.show()

# -------------------------------
# 7. CUSTOMER BUYING TREND
# -------------------------------

customer_trend = df.groupby("customer")["total"].sum().reset_index()

fig5 = px.bar(
    customer_trend,
    x="customer",
    y="total",
    title="Customer Spending",
    template="plotly_dark"
)

fig5.update_traces(marker_color="cyan", name="Total Spend")
fig5.show()

# -------------------------------
# 8. BUSIEST HOUR ANALYSIS
# -------------------------------

df["hour"] = pd.to_datetime(df["time"], format="%H:%M:%S").dt.hour

hourly_customers = df.groupby("hour")["customer"].count().reset_index()

fig6 = px.line(
    hourly_customers,
    x="hour",
    y="customer",
    title="Customers Per Hour",
    template="plotly_dark",
    markers=True
)

fig6.update_traces(line=dict(color="yellow", width=4), name="Customers")
fig6.show()

# -------------------------------
# 9. AI SALES PREDICTION
# -------------------------------

daily_sales["day_index"] = np.arange(len(daily_sales))

X = daily_sales[["day_index"]]
y = daily_sales["total"]

model = LinearRegression()
model.fit(X, y)

future_days = np.arange(len(daily_sales), len(daily_sales) + 7).reshape(-1, 1)

prediction = model.predict(future_days)

pred_df = pd.DataFrame({
    "day": range(len(daily_sales), len(daily_sales) + 7),
    "predicted_sales": prediction
})

fig7 = px.line(
    pred_df,
    x="day",
    y="predicted_sales",
    title="AI Future Sales Prediction",
    template="plotly_dark",
    markers=True
)

fig7.update_traces(line=dict(color="lime", width=4), name="Prediction")
fig7.show()

print("\nAI Sales Prediction Completed")