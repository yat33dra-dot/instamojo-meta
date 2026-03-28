import streamlit as st
import pandas as pd

st.title("Instamojo → Meta Converter")

uploaded_file = st.file_uploader("Upload Instamojo CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.write("Columns detected:", list(df.columns))  # 👈 DEBUG

    # --- STATUS FILTER ---
    status_col = None
    for col in df.columns:
        if "status" in col.lower():
            status_col = col
            break

    if status_col:
        df = df[df[status_col].astype(str).str.lower().isin(["credit", "successful", "success"])]

    # --- NAME ---
    name_col = next((c for c in df.columns if "name" in c.lower()), None)
    df["fn"] = df[name_col].fillna("").apply(lambda x: str(x).split(" ")[0]) if name_col else ""
    df["ln"] = df[name_col].fillna("").apply(lambda x: " ".join(str(x).split(" ")[1:])) if name_col else ""

    # --- DATE ---
    date_col = next((c for c in df.columns if "date" in c.lower() or "time" in c.lower()), None)
    if date_col:
        df["event_time"] = pd.to_datetime(df[date_col], errors="coerce") \
                            .dt.strftime("%Y-%m-%dT%H:%M:%S")
    else:
        df["event_time"] = ""

    # --- EMAIL ---
    email_col = next((c for c in df.columns if "email" in c.lower()), None)
    df["email"] = df[email_col].fillna("").str.lower().str.strip() if email_col else ""

    # --- PHONE ---
    phone_col = next((c for c in df.columns if "phone" in c.lower()), None)
    if phone_col:
        df["phone"] = df[phone_col].astype(str).str.replace(r"\D", "", regex=True)
        df["phone"] = df["phone"].apply(lambda x: "+91" + x[-10:] if len(x) >= 10 else "")
    else:
        df["phone"] = ""

    # --- AMOUNT ---
    amount_col = next((c for c in df.columns if "amount" in c.lower()), None)
    df["value"] = df[amount_col] if amount_col else ""

    # --- ORDER ID ---
    id_col = next((c for c in df.columns if "id" in c.lower()), None)
    df["order_id"] = df[id_col] if id_col else ""

    # --- FINAL ---
    meta_df = pd.DataFrame({
        "event_name": "Purchase",
        "event_time": df["event_time"],
        "email": df["email"],
        "phone": df["phone"],
        "fn": df["fn"],
        "ln": df["ln"],
        "value": df["value"],
        "currency": "INR",
        "order_id": df["order_id"]
    })

    st.subheader("Preview")
    st.dataframe(meta_df.head(20))

    csv = meta_df.to_csv(index=False).encode("utf-8")

    st.download_button("Download Meta CSV", csv, "meta_offline.csv")
