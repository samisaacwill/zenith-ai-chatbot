"""
ShopStream - Billing Engine Testbed
A Streamlit application for testing multi-tenant billing workflows with Supabase
"""

import streamlit as st
import time
import uuid
from datetime import datetime
from typing import Optional
from supabase import create_client, Client


# ============================================================================
# CONFIGURATION
# ============================================================================

def init_supabase() -> Client:
    """Initialize Supabase client using secrets"""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


# ============================================================================
# FINANCIAL GUARD CONTEXT MANAGER
# ============================================================================

class monitor_guard:
    """
    Context manager for tracking billable operations.
    Acts as a placeholder for future Revgate SDK integration.
    
    Tracks operation status and logs transactions to Supabase:
    - PROVISIONAL: Operation completed successfully
    - VOIDED: Operation failed or was interrupted
    """
    
    def __init__(self, entity_id: str, product_key: str, revenue_potential: float):
        self.entity_id = entity_id
        self.product_key = product_key
        self.revenue_potential = revenue_potential
        self.transaction_id = str(uuid.uuid4())
        self.exception_occurred = False
        self.supabase = init_supabase()
        
    def __enter__(self):
        """Start tracking the billable operation"""
        st.toast(f"🔍 Tracking started: {self.product_key} (${self.revenue_potential:.2f})")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Complete tracking and log transaction status.
        
        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        if exc_type is not None:
            # Exception occurred - mark as VOIDED
            status = "VOIDED"
            print(f"❌ VOIDED: {self.product_key} for {self.entity_id} - Exception: {exc_val}")
        else:
            # Success - mark as PROVISIONAL
            status = "PROVISIONAL"
            
        # Log transaction to Supabase
        self._log_transaction(status)
        
        # Don't suppress exceptions
        return False
    
    def _log_transaction(self, status: str):
        """Log transaction to Supabase database"""
        try:
            transaction = {
                "id": self.transaction_id,
                "entity_id": self.entity_id,
                "product_key": self.product_key,
                "status": status,
                "revenue": self.revenue_potential,
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.supabase.table("transactions").insert(transaction).execute()
            
        except Exception as e:
            st.error(f"Failed to log transaction: {e}")


# ============================================================================
# BUSINESS LOGIC FUNCTIONS
# ============================================================================

def add_product_listing(entity_id: str, force_failure: bool = False):
    """
    Add a product listing (non-AI operation).
    
    Args:
        entity_id: Client identifier
        force_failure: If True, raises exception for testing
    """
    with monitor_guard(entity_id, "listing", 0.10):
        # Simulate processing
        time.sleep(0.5)
        
        if force_failure:
            raise Exception("Forced failure during product listing creation")
        
        st.success("✅ Product listing added successfully!")


def generate_smart_copy(entity_id: str, force_failure: bool = False):
    """
    Generate AI-powered product copy using Llama 3.
    
    Args:
        entity_id: Client identifier
        force_failure: If True, raises exception for testing
    """
    with monitor_guard(entity_id, "smart_copy", 1.00):
        # Simulate AI call
        with st.spinner("🤖 Llama 3 generating copy..."):
            time.sleep(1.5)
        
        if force_failure:
            raise Exception("Forced failure during smart copy generation")
        
        st.success("✅ Smart copy generated with Llama 3!")
        st.info("📝 Sample: 'Transform your space with this premium, eco-friendly solution...'")


def brand_safety_check(entity_id: str, force_failure: bool = False):
    """
    Run AI-powered brand safety analysis using GPT-4o.
    
    Args:
        entity_id: Client identifier
        force_failure: If True, raises exception for testing
    """
    with monitor_guard(entity_id, "brand_guard", 5.00):
        # Simulate AI call
        with st.spinner("🛡️ GPT-4o analyzing brand safety..."):
            time.sleep(2.0)
        
        if force_failure:
            raise Exception("Forced failure during brand safety check")
        
        st.success("✅ Brand safety check passed!")
        st.info("🛡️ Analysis: Content meets brand guidelines. Safety score: 98/100")


# ============================================================================
# QA UTILITY FUNCTIONS
# ============================================================================

def run_batch_operations(operation_func, entity_id: str, count: int, force_failure: bool):
    """
    Execute batch operations for stress testing.
    
    Args:
        operation_func: Function to execute
        entity_id: Client identifier
        count: Number of operations to run
        force_failure: Whether to force failures
    """
    success_count = 0
    failure_count = 0
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(count):
        try:
            operation_func(entity_id, force_failure)
            success_count += 1
        except Exception as e:
            failure_count += 1
            st.warning(f"⚠️ Batch {i+1} failed: {str(e)}")
        
        progress = (i + 1) / count
        progress_bar.progress(progress)
        status_text.text(f"Processing: {i+1}/{count} operations")
    
    progress_bar.empty()
    status_text.empty()
    
    st.success(f"🎯 Batch complete: {success_count} succeeded, {failure_count} failed")


def fetch_recent_transactions(limit: int = 5):
    """
    Fetch recent transactions from Supabase.
    
    Args:
        limit: Maximum number of transactions to fetch
        
    Returns:
        List of transaction records
    """
    try:
        supabase = init_supabase()
        response = supabase.table("transactions").select("*").order("created_at", desc=True).limit(limit).execute()
        return response.data
    except Exception as e:
        st.error(f"Failed to fetch transactions: {e}")
        return []


def void_transaction(transaction_id: str):
    """
    Update transaction status to VOIDED.
    
    Args:
        transaction_id: UUID of the transaction to void
    """
    try:
        supabase = init_supabase()
        supabase.table("transactions").update({"status": "VOIDED"}).eq("id", transaction_id).execute()
        st.success(f"✅ Transaction {transaction_id[:8]}... voided successfully!")
    except Exception as e:
        st.error(f"Failed to void transaction: {e}")


# ============================================================================
# STREAMLIT UI
# ============================================================================

def main():
    """Main application entry point"""
    
    # Page configuration
    st.set_page_config(
        page_title="ShopStream - Billing Testbed",
        page_icon="🛒",
        layout="wide"
    )
    
    # Header
    st.title("🛒 ShopStream")
    st.subheader("Billing Engine Testbed")
    st.markdown("---")
    
    # ========================================================================
    # SIDEBAR: CONFIGURATION
    # ========================================================================
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Multi-tenant selector
        entity_id = st.selectbox(
            "🏢 Client Selector",
            options=["Test Shop A", "Test Shop B", "Test Shop C"],
            index=0
        )
        
        st.markdown("---")
        
        # QA Controls
        st.header("🧪 QA Controls")
        
        force_failure = st.toggle(
            "⚡ Force Code Failure",
            value=False,
            help="If enabled, operations will raise an exception after simulated AI call"
        )
        
        stress_test_count = st.slider(
            "🔥 Stress Test Batch Size",
            min_value=1,
            max_value=20,
            value=5,
            help="Number of operations to run in batch mode"
        )
        
        st.markdown("---")
        st.caption("💡 Toggle 'Force Failure' to test VOIDED transaction logging")
    
    # ========================================================================
    # MAIN CONTENT: PRODUCT FEATURES
    # ========================================================================
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📦 Product Listing")
        st.caption("Non-AI • $0.10")
        
        if st.button("➕ Add Product Listing", use_container_width=True, type="primary"):
            try:
                add_product_listing(entity_id, force_failure)
            except Exception as e:
                st.error(f"❌ Operation failed: {e}")
        
        if st.button("🔥 Batch Add Listings", use_container_width=True):
            run_batch_operations(add_product_listing, entity_id, stress_test_count, force_failure)
    
    with col2:
        st.markdown("### ✨ Smart Copy")
        st.caption("AI (Llama 3) • $1.00")
        
        if st.button("🤖 Generate Smart Copy", use_container_width=True, type="primary"):
            try:
                generate_smart_copy(entity_id, force_failure)
            except Exception as e:
                st.error(f"❌ Operation failed: {e}")
        
        if st.button("🔥 Batch Generate Copy", use_container_width=True):
            run_batch_operations(generate_smart_copy, entity_id, stress_test_count, force_failure)
    
    with col3:
        st.markdown("### 🛡️ Brand Safety")
        st.caption("AI (GPT-4o) • $5.00")
        
        if st.button("🔍 Run Safety Check", use_container_width=True, type="primary"):
            try:
                brand_safety_check(entity_id, force_failure)
            except Exception as e:
                st.error(f"❌ Operation failed: {e}")
        
        if st.button("🔥 Batch Safety Checks", use_container_width=True):
            run_batch_operations(brand_safety_check, entity_id, stress_test_count, force_failure)
    
    st.markdown("---")
    
    # ========================================================================
    # MANUAL VOID SECTION
    # ========================================================================
    
    st.header("🗂️ Transaction Management")
    
    if st.button("🔄 Refresh Transactions"):
        st.rerun()
    
    transactions = fetch_recent_transactions(5)
    
    if transactions:
        st.markdown("### Last 5 Transactions")
        
        for txn in transactions:
            col_info, col_action = st.columns([4, 1])
            
            with col_info:
                status_emoji = "✅" if txn["status"] == "PROVISIONAL" else "❌"
                timestamp = datetime.fromisoformat(txn["created_at"].replace("Z", "+00:00"))
                
                st.markdown(f"""
                **{status_emoji} {txn['product_key'].upper()}** • ${txn['revenue']:.2f}  
                Entity: `{txn['entity_id']}` | Status: `{txn['status']}`  
                ID: `{txn['id'][:13]}...` | Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
                """)
            
            with col_action:
                if txn["status"] != "VOIDED":
                    if st.button("🚫 Void", key=f"void_{txn['id']}", use_container_width=True):
                        void_transaction(txn['id'])
                        st.rerun()
                else:
                    st.button("✓ Voided", key=f"voided_{txn['id']}", disabled=True, use_container_width=True)
            
            st.markdown("---")
    else:
        st.info("📭 No transactions found. Start using the features above to create transactions!")
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    
    st.markdown("---")
    st.caption("🔧 ShopStream v1.0 | Built for billing engine testing and QA stress testing")


if __name__ == "__main__":
    main()
