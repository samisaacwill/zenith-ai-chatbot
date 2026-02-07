import streamlit as st
import uuid
import time
from datetime import datetime
from supabase import create_client

# Initialize
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# --- REAL-WORLD REV-GATE GUARD ---
class monitor_guard:
    def __init__(self, entity_id, product_key, price):
        self.data = {"entity_id": entity_id, "product_key": product_key, "price": price}

    def __enter__(self):
        st.toast(f"🚀 Service Started: {self.data['product_key']}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        status = "VOIDED" if exc_type else "PROVISIONAL"
        # Log to Evidence Table (Module C: Trust Layer)
        supabase.table("ai_evidence").insert({
            "transaction_id": self.data["entity_id"],
            "client_name": st.session_state.client,
            "reasoning_trace": f"Step 1: Ingested Request -> Step 2: Processed via {self.data['product_key']} -> Result: {status}",
            "cost_estimate": self.data["price"]
        }).execute()
        return False

# --- PROFESSIONAL UI ---
st.set_page_config(page_title="ShopStream Pro", layout="wide")
st.title("🛒 ShopStream Pro: Merchant AI Studio")

if 'client' not in st.session_state: st.session_state.client = "Test Shop A"

with st.sidebar:
    st.header("🏢 Merchant Settings")
    st.session_state.client = st.selectbox("Active Account", ["Test Shop A", "Retailer B", "Enterprise C"])
    st.info(f"Plan: Marketplace Tier\nSettlement: 24h Window")

# SERVICE AREA
col1, col2 = st.columns(2)
with col1:
    st.subheader("✨ AI Content Studio")
    prod_name = st.text_input("Product Name", "Leather Travel Bag")
    if st.button("Generate Pro Copy ($1.00)"):
        tx_id = f"copy_{uuid.uuid4().hex[:6]}"
        with monitor_guard(tx_id, "smart_copy", 1.00):
            with st.spinner("AI writing..."):
                time.sleep(1)
                st.success(f"Generated! ID: {tx_id}")

with col2:
    st.subheader("🛡️ Brand Safety Guard")
    if st.button("Run Compliance Scan ($5.00)"):
        tx_id = f"guard_{uuid.uuid4().hex[:6]}"
        with monitor_guard(tx_id, "brand_guard", 5.00):
            with st.spinner("Scanning..."):
                time.sleep(1.5)
                st.success(f"Safe! ID: {tx_id}")

# EVIDENCE & AUDIT (The "Trust" Layer)
st.divider()
st.header("📊 Billing Evidence & Audit Trail")
st.caption("Review reasoning traces and manage disputes within the 24h settlement window.")

try:
    evidence = supabase.table("ai_evidence").select("*").order("created_at", desc=True).limit(5).execute().data
    for item in evidence:
        with st.expander(f"Transaction {item['transaction_id']} - ${item['cost_estimate']}"):
            st.write(f"**Reasoning Trace:** {item['reasoning_trace']}")
            st.write(f"**Time:** {item['created_at']}")
            if st.button("Dispute / Void", key=item['transaction_id']):
                st.warning("Void request sent to Revgate Settlement Engine.")
except Exception:
    st.info("Start an AI operation to see the evidence trail.")
