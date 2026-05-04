import streamlit as st
import pandas as pd
from collections import deque

# ---------------- UI ----------------
st.set_page_config(page_title="Twitter Settlement Loss Calculator", layout="wide")

st.title("🐦 Twitter Securities Loss Calculator")
st.markdown("Upload an Excel file to compute recognized losses")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file is None:
    st.info("Please upload a file to begin.")
    st.stop()

# ---------------- LOAD ----------------
try:
    df = pd.read_excel(uploaded_file, engine="openpyxl")
except Exception as e:
    st.error(f"Error reading file: {e}")
    st.stop()

# ---------------- PREPROCESS ----------------
try:
    df["Trade Date"] = pd.to_datetime(df["Trade Date"], dayfirst=True)
    df["Purchases"] = df["Purchases"].fillna(0)
    df["Sales"] = df["Sales"].fillna(0)
    df["Qty"] = df["Purchases"] - df["Sales"]

    df = df[df["Transaction Type"].isin(["Purchase", "Sale"])]
    df = df.sort_values(["Entity", "Fund Name", "Trade Date"])
except Exception as e:
    st.error(f"Preprocessing error: {e}")
    st.stop()

st.subheader("📄 Data Preview")
st.dataframe(df.head())

# ---------------- TABLE 1 LOGIC ----------------

def get_purchase_bucket(date):
    if date < pd.Timestamp("2015-04-28"):
        return "early"
    elif date == pd.Timestamp("2015-04-28"):
        return "mid"
    elif date <= pd.Timestamp("2015-07-28"):
        return "late"
    else:
        return "post"


def get_sale_bucket(date):
    if date < pd.Timestamp("2015-04-28"):
        return "pre"
    elif date == pd.Timestamp("2015-04-28"):
        return "same_day"
    elif date <= pd.Timestamp("2015-07-28"):
        return "period1"
    elif date <= pd.Timestamp("2015-07-30"):
        return "period2"
    elif date == pd.Timestamp("2015-07-31"):
        return "period3"
    else:
        return "post_aug1"


inflation_table = {
    "early": {
        "pre": 0.00,
        "same_day": 8.97,
        "period1": 12.93,
        "period2": 18.27,
        "period3": 18.69,
        "post_aug1": 20.34
    },
    "mid": {
        "same_day": 0.00,
        "period1": 3.96,
        "period2": 9.30,
        "period3": 9.72,
        "post_aug1": 11.37
    },
    "late": {
        "period1": 0.00,
        "period2": 5.34,
        "period3": 5.76,
        "post_aug1": 7.41
    },
    "post": {
        "period2": 0.00,
        "period3": 0.00,
        "post_aug1": 0.00
    }
}


def get_inflation_decline(purchase_date, sale_date):
    p_bucket = get_purchase_bucket(purchase_date)
    s_bucket = get_sale_bucket(sale_date)
    return inflation_table.get(p_bucket, {}).get(s_bucket, 0.0)

# ---------------- CONSTANT ----------------
AVG_PRICE = 28.06

# ---------------- LOSS FUNCTION ----------------

def calculate_loss(buy, sell, qty):

    buy_price = buy["price"]
    sell_price = sell["Price per share"]

    buy_date = buy["date"]
    sell_date = sell["Trade Date"]

    inflation = get_inflation_decline(buy_date, sell_date)

    # Case A
    if sell_date < pd.Timestamp("2015-04-28"):
        return 0

    # Case B
    elif sell_date <= pd.Timestamp("2015-08-02"):
        loss = min(inflation, buy_price - sell_price)

    # Case C
    elif sell_date <= pd.Timestamp("2015-10-30"):
        loss = min(inflation, buy_price - sell_price, buy_price - AVG_PRICE)

    # Case D
    else:
        loss = min(inflation, buy_price - AVG_PRICE)

    return max(loss, 0) * qty

# ---------------- FIFO + MARKET CAP ----------------

def compute_loss_for_fund(df_fund):

    inventory = deque()
    total_loss = 0
    total_purchase = 0
    total_sales = 0

    for _, row in df_fund.iterrows():

        qty = row["Qty"]
        price = row["Price per share"]
        date = row["Trade Date"]

        if qty > 0:
            inventory.append({
                "qty": qty,
                "price": price,
                "date": date
            })
            total_purchase += qty * price

        elif qty < 0:
            sell_qty = abs(qty)
            total_sales += sell_qty * price

            while sell_qty > 0 and inventory:

                buy = inventory[0]
                matched_qty = min(sell_qty, buy["qty"])

                loss = calculate_loss(buy, row, matched_qty)
                total_loss += loss

                buy["qty"] -= matched_qty
                sell_qty -= matched_qty

                if buy["qty"] == 0:
                    inventory.popleft()

    # Remaining holdings
    holding_value = sum(item["qty"] * AVG_PRICE for item in inventory)

    # Market loss cap
    market_loss = total_purchase - (total_sales + holding_value)

    if market_loss <= 0:
        return 0

    return min(total_loss, market_loss)

# ---------------- RUN ----------------

results = []

for (client, fund), group in df.groupby(["Entity", "Fund Name"]):

    loss = compute_loss_for_fund(group)

    results.append({
        "Client": client,
        "Fund": fund,
        "Loss": round(loss, 2)
    })

result_df = pd.DataFrame(results)
client_loss = result_df.groupby("Client")["Loss"].sum().reset_index()

# ---------------- OUTPUT ----------------

st.subheader("📊 Fund-wise Loss")
st.dataframe(result_df)

st.download_button(
    "⬇️ Download Results",
    result_df.to_csv(index=False),
    file_name="fund_loss_results.csv"
)

st.subheader("📊 Client-wise Loss")
st.dataframe(client_loss)


st.download_button(
    "⬇️ Download Results",
    client_loss.to_csv(index=False),
    file_name="client_loss_results.csv"
)