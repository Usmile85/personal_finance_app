
import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="💸 Personal Finance Tracker", layout="centered")
st.markdown("<h1 style='text-align: center;'>📱 Personal Finance Dashboard</h1>", unsafe_allow_html=True)

csv_file = "personal_finance_log.csv"

if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)
    df = df.dropna(subset=["Date"])
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df["Subcategory"] = df["Subcategory"].astype(str)
    df["Notes"] = df["Notes"].astype(str)
else:
    df = pd.DataFrame(columns=["Date", "Category", "Subcategory", "Amount", "Notes"])

with st.sidebar:
    st.markdown("### ➕ Add Expense")
    date = st.date_input("Date", value=datetime.today())
    category = st.selectbox("Category", [
        "Food & Groceries", "Transportation", "Rent & Utilities", "Airtime & Data",
        "Debt Repayment", "Charity or Zakat", "Shopping", "Entertainment",
        "Business Expenses", "Savings"
    ])
    subcategory = st.selectbox("Subcategory", [
        "Groceries", "Laundry", "Kiddies Food", "School Fee", "Electricity", "Parent",
        "Detergent", "Subscription", "Miscellaneous", "Water"
    ])
    amount = st.number_input("Amount (₦)", min_value=0.0, step=0.01)
    notes = st.text_area("Notes")
    st.markdown("---")
    budget = st.number_input("🎯 Monthly Budget (₦)", value=50000.0, step=1000.0)

    if st.button("💾 Save"):
        new_row = {
            "Date": pd.to_datetime(date),
            "Category": category,
            "Subcategory": subcategory,
            "Amount": amount,
            "Notes": notes
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(csv_file, index=False)
        st.success("✅ Expense saved! Please refresh.")

df["DateOnly"] = df["Date"].dt.normalize()
today = pd.Timestamp.now().normalize()
this_month = df[df["Date"].dt.month == pd.Timestamp.now().month]
this_week = df[df["Date"].dt.isocalendar().week == pd.Timestamp.now().isocalendar().week]
today_expense = df[df["DateOnly"] == today]

if not df.empty:
    st.markdown("## 📊 Summary")
    st.metric("📅 Today", f"₦{today_expense['Amount'].sum():,.2f}")
    st.metric("🗓️ This Week", f"₦{this_week['Amount'].sum():,.2f}")
    st.metric("🗓️ This Month", f"₦{this_month['Amount'].sum():,.2f}")
    st.metric("📁 Total", f"₦{df['Amount'].sum():,.2f}")

    monthly_spent = this_month['Amount'].sum()
    if monthly_spent > budget:
        st.error(f"🚨 Over budget by ₦{monthly_spent - budget:,.2f}")
    else:
        st.success(f"✅ Under budget! Remaining: ₦{budget - monthly_spent:,.2f}")

    st.markdown("### 📋 All Records")
    st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)

    st.markdown("### 📌 By Category")
    st.bar_chart(df.groupby("Category")["Amount"].sum().sort_values())

    st.markdown("### 🧾 By Subcategory")
    st.bar_chart(df.groupby("Subcategory")["Amount"].sum().sort_values())

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", data=csv, file_name="finance_log.csv")

    def to_excel(dataframe):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            dataframe.to_excel(writer, index=False, sheet_name="Sheet1")
        return output.getvalue()

    excel = to_excel(df)
    st.download_button("⬇️ Download Excel", data=excel, file_name="finance_log.xlsx")
else:
    st.info("Add expenses from the sidebar to begin tracking.")
