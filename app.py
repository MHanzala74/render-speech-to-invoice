from product_matching import find_product_semantic_match
from store_product import store_products_in_chromedb
from speech_to_text import speech_to_text
from Invoice_generation import generate_invoice
import streamlit as st
import json

# Initialize session state
if 'products' not in st.session_state:
    st.session_state.products = []
if 'invoice_history' not in st.session_state:
    st.session_state.invoice_history = []

# Load products
def load_products():
    try:
        with open("mock_products_mixed_shuffled.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Data file not found")
        return []


# Main Streamlit app
def main():
    st.set_page_config(
        page_title="AI Urdu Speech-to-Invoice System",
        page_icon="🎤",
        layout="wide"
    )

    st.title("AI Urdu Speech-to-Invoice System")
    st.markdown("---")

    # Load products
    if not st.session_state.products:
        st.session_state.products = load_products()
        if st.session_state.products:
            store_products_in_chromedb(st.session_state.products)

    # Sidebar
    with st.sidebar:
        st.header("Options")
        option = st.radio(
            "Select:",
            ["Select product by voice", "View all products", "Invoice history"]
        )

    # Main content
    if option == "Select product by voice":
        st.header("Select product by voice")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("Record voice", type="primary"):
                spoken_text = speech_to_text()
                if spoken_text:
                    st.success(f"You said: **{spoken_text}**")
                    
                    product = find_product_semantic_match(spoken_text, st.session_state.products)
                    if product:
                        st.session_state.selected_product = product
                        st.success(f"Selected product: **{product['name']}**")
                    else:
                        st.error("No product found")

        with col2:
            if 'selected_product' in st.session_state:
                product = st.session_state.selected_product
                st.subheader("Selected Product")
                st.write(f"**Name:** {product['name']}")
                st.write(f"**Price:** Rs. {product.get('price', 'N/A')}")
                st.write(f"**Unit:** {product.get('uoM', 'N/A')}")
                
                quantity = st.number_input("Quantity", min_value=1, value=1)
                
                if st.button("Generate Invoice"):
                    invoice = generate_invoice(product, quantity)
                    if invoice:
                        st.success("Invoice created!")
                        st.json(invoice)

    elif option == "View all products":
        st.header("All Products")
        
        search_term = st.text_input("Search for product")
        
        filtered_products = st.session_state.products
        if search_term:
            filtered_products = [p for p in st.session_state.products 
                               if search_term.lower() in p['name'].lower()]
        
        for product in filtered_products[:20]:  # Show first 20 products
            with st.expander(f"{product['name']} - Rs. {product.get('price', 'N/A')}"):
                st.write(f"**ID:** {product['id']}")
                st.write(f"**Price:** Rs. {product.get('price', 'N/A')}")
                st.write(f"**Unit:** {product.get('uoM', 'N/A')}")
                st.write(f"**Tax Rate:** {product.get('taxRate', 'N/A')}")

    elif option == "Invoice History":
        st.header("Invoice History")
        
        if not st.session_state.invoice_history:
            st.info("No invoice created yet")
        else:
            for invoice in reversed(st.session_state.invoice_history[-10:]):  # Show last 10
                with st.expander(f"انوائس {invoice['invoiceId']}"):
                    st.write(f"**Product:** {invoice['productName']}")
                    st.write(f"**Quantity:** {invoice['quantity']}")
                    st.write(f"**Total price:** Rs. {invoice['grandTotal']:,.2f}")
                    st.write(f"**Tax:** Rs. {invoice['salesTaxApplicable']:,.2f}")

if __name__ == "__main__":
    main()