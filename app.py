import streamlit as st
import pandas as pd

st.title("Instamojo → Meta Converter")

uploaded_file = st.file_uploader("Upload Instamojo CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # --- FIND STATUS COLUMN SAFELY ---
    status_col = None
    for col in df.columns:
        if "status" in col.lower():
            status_col = col
            break

    if status_col:
        df = df[df[status_col].astype(str).str.lower().isin(["credit", "successful", "success"])]

    # --- NAME SPLIT ---
    df["fn"] = df["Buyer Name"].fillna("").apply(lambda x: str(x).split(" ")[0])
    df["ln"] = df["Buyer Name"].fillna("").apply(lambda x: " ".join(str(x).split(" ")[1:]))

    # --- DATE FORMAT ---
    df["event_time"] = pd.to_datetime(df["Created At"], errors="coerce") \
                        .dt.strftime("%Y-%m-%dT%H:%M:%S")

    # --- EMAIL CLEAN ---
    df["email"] = df["Buyer Email"].fillna("").str.strip().str.lower()

    # --- PHONE CLEAN ---
    df["phone"] = df["Buyer Phone Number"].astype(str).str.replace(r"\D", "", regex=True)
    df["phone"] = df["phone"].apply(lambda x: "+91" + x[-10:] if len(x) >= 10 else "")

    # --- FINAL OUTPUT ---
    meta_df = pd.DataFrame({
        "event_name": "Purchase",
        "event_time": df["event_time"],
        "email": df["email"],
        "phone": df["phone"],
        "fn": df["fn"],
        "ln": df["ln"],
        "value": df["Amount"],
        "currency": "INR",
        "order_id": df["Payment ID"]
    })

    st.subheader("Preview")
    st.dataframe(meta_df.head())

    csv = meta_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Meta CSV",
        csv,
        "meta_offline.csv",
        "text/csv"
    )
