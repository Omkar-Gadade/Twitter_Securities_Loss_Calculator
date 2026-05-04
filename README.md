# 📊 Securities Litigation Loss Calculator (Twitter Settlement)

## 🚀 Overview

This project implements a **loss calculation engine** for the Twitter Securities Litigation Settlement.
It computes **recognized losses** for investors based on:

* FIFO (First-In-First-Out) transaction matching
* Settlement-specific inflation decline (Table 1)
* Average price constraint (Table 2)
* Market loss cap

The solution is built using **Python and Streamlit**, providing a simple web interface to upload transaction data and compute losses.

---

## 🧠 Key Concepts Implemented

### 1. FIFO Matching

Transactions are matched using First-In-First-Out logic:

* Earliest purchases are matched with earliest sales
* Ensures correct mapping of buy-sell pairs

---

### 2. Inflation Decline (Table 1)

Loss depends on:

* Purchase date bucket
* Sale date bucket

The settlement provides a **matrix-based lookup table** (Table 1), implemented as:

```
(purchase_bucket, sale_bucket) → inflation value
```

---

### 3. Average Price (Table 2)

* Settlement defines a fixed average price: **28.06**
* Used to cap losses in certain scenarios

---

### 4. Loss Calculation Rules

Loss per share is calculated as:

```
min(
    inflation decline,
    purchase price - sale price,
    purchase price - average price (if applicable)
)
```

Different rules apply based on sale date:

| Case | Date Range           | Rule                   |
| ---- | -------------------- | ---------------------- |
| A    | Before Apr 28, 2015  | Loss = 0               |
| B    | Apr 28 – Aug 2, 2015 | Basic min rule         |
| C    | Aug 3 – Oct 30, 2015 | Includes avg price cap |
| D    | After Oct 30, 2015   | Uses avg price only    |

---

### 5. Market Loss Cap

Final loss is capped by actual economic loss:

```
Market Loss = Total Purchase - (Total Sales + Holding Value)

Final Loss = min(Recognized Loss, Market Loss)
```

---

## 📂 Input Format

The input Excel file must contain the following columns:

* `Entity`
* `Fund Name`
* `Transaction Type` (Purchase / Sale)
* `Purchases`
* `Sales`
* `Price per share`
* `Trade Date`

---

## ⚙️ Installation

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the App

```bash
streamlit run app.py
```

---

## 🌐 Features

* Upload Excel transaction file
* Automatic FIFO matching
* Accurate loss calculation using settlement rules
* Fund-level and client-level aggregation
* Download results as CSV

---

## 📊 Output

The app provides:

* **Fund-wise Loss**
* **Client-wise Total Loss**

---

## 🧪 Example Use Case

Upload a dataset with buy/sell transactions →
App computes →
✔ Recognized Loss
✔ Applies settlement constraints
✔ Outputs final claimable loss

---

## ⚠️ Notes

* Only common stock transactions are considered
* Option-related calculations are excluded (not present in dataset)
* Average price (28.06) is fixed as per settlement notice

---

## 💡 Tech Stack

* Python
* Pandas
* Streamlit

---

## 🎯 Conclusion

This project demonstrates how a **legal settlement document** can be translated into a **structured computational model**, combining finance concepts with data engineering and web deployment.

---

## 📎 Author

Omkar Gadade
