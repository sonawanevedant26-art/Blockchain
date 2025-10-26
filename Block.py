import streamlit as st
import hashlib
import uuid
from datetime import datetime

# ---- Page Config ----
st.set_page_config(page_title="Simple Blockchain Ledger", layout="wide")

# ---- Helper Functions ----
def sha256_hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

def create_block(wallet_from, wallet_to, amount, note):
    chain = st.session_state.chain
    prev_hash = chain[-1]["hash"] if chain else "0"*64
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    raw_data = f"{wallet_from}{wallet_to}{amount}{note}{timestamp}{prev_hash}"
    block_hash = sha256_hash(raw_data)

    block = {
        "id": str(uuid.uuid4()),
        "index": len(chain) + 1,
        "from": wallet_from,
        "to": wallet_to,
        "amount": float(amount),
        "note": note,
        "timestamp": timestamp,
        "prev_hash": prev_hash,
        "hash": block_hash
    }

    chain.append(block)
    st.session_state.msg = f"✅ Block #{block['index']} added successfully!"

def verify_chain_integrity(chain):
    for i in range(1, len(chain)):
        if chain[i]["prev_hash"] != chain[i-1]["hash"]:
            return False
    return True

# ---- Session State ----
if "chain" not in st.session_state:
    st.session_state.chain = []
if "msg" not in st.session_state:
    st.session_state.msg = ""

# ---- Sidebar ----
st.sidebar.title("⚙️ Blockchain Controls")

if st.sidebar.button("Clear Blockchain"):
    st.session_state.chain = []
    st.session_state.msg = "🧹 Blockchain cleared."

if st.sidebar.button("Verify Integrity"):
    if verify_chain_integrity(st.session_state.chain):
        st.sidebar.success("✅ Blockchain integrity verified.")
    else:
        st.sidebar.error("⚠️ Blockchain is corrupted!")

st.sidebar.info("Transactions are stored only during the current session.")

# ---- UI ----
st.title("💎 Simple Blockchain Ledger")

# ---- Add Transaction ----
st.subheader("➕ Add New Transaction")

col1, col2, col3 = st.columns(3)
with col1:
    wallet_from = st.text_input("Sender Wallet ID")
with col2:
    wallet_to = st.text_input("Receiver Wallet ID")
with col3:
    amount = st.text_input("Amount (₹)")

note = st.text_area("Transaction Note (optional)")

if st.button("Add Transaction"):
    if not wallet_from or not wallet_to or not amount:
        st.warning("Please fill in all fields.")
    else:
        try:
            float(amount)
            create_block(wallet_from, wallet_to, amount, note)
        except ValueError:
            st.error("Amount must be numeric.")

if st.session_state.msg:
    st.info(st.session_state.msg)

# ---- Blockchain Display ----
st.markdown("---")
st.subheader("📜 Blockchain Transactions")

if not st.session_state.chain:
    st.info("No transactions yet. Add one above.")
else:
    for block in st.session_state.chain[::-1]:  # show latest first
        st.markdown(f"""
        <div style='background:#E0F2FE;padding:12px;border-radius:10px;margin-bottom:10px;border-left:5px solid #0284C7'>
            <strong>Block #{block['index']}</strong> — <span style='color:#0284C7'>{block['timestamp']}</span><br>
            <b>From:</b> {block['from']} → <b>To:</b> {block['to']}<br>
            <b>Amount:</b> ₹{block['amount']}<br>
            <b>Note:</b> {block['note'] if block['note'] else '(none)'}<br>
            <small><code>{block['hash'][:40]}...</code></small>
        </div>
        """, unsafe_allow_html=True)
