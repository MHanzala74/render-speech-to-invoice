from product_matching import find_product_semantic_match
from store_product import store_products_in_chromedb
from Invoice_generation import generate_invoice
import streamlit as st
import json
from audio_recorder_streamlit import audio_recorder
import tempfile
import speech_recognition as sr
import io

# Initialize session state
if 'products' not in st.session_state:
    st.session_state.products = []
if 'invoice_history' not in st.session_state:
    st.session_state.invoice_history = []
if 'spoken_text' not in st.session_state:
    st.session_state.spoken_text = ""
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None

# Load products
def load_products():
    try:
        with open("mock_products_mixed_shuffled.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Data file not found")
        return []

# Convert audio bytes to text
def convert_audio_to_text(audio_bytes):
    """
    Converts audio bytes into text
    """
    try:
        # Save audio bytes into a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file.flush()
            
            # Speech recognition
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(tmp_file.name) as source:
                audio_data = recognizer.record(source)
                
                # Use Google Web Speech API
                text = recognizer.recognize_google(audio_data)
                return text
                
    except sr.UnknownValueError:
        st.error("Could not understand the speech. Please try again.")
        return None
    except sr.RequestError as e:
        st.error(f"Could not connect to the service: {e}")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

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
            st.subheader("Record your voice")
            
            # Audio recorder component
            audio_bytes = audio_recorder()
            
            if audio_bytes:
                # Audio playback
                st.audio(audio_bytes, format='audio/wav')
                
                if st.button("Convert speech to text", type="primary"):
                    with st.spinner("Converting speech to text..."):
                        try:
                            # Convert audio to text
                            recognized_text = convert_audio_to_text(audio_bytes)
                            
                            if recognized_text:
                                st.session_state.spoken_text = recognized_text
                                st.success(f"Recognized text: **{recognized_text}**")
                            else:
                                st.error("Could not understand the speech")
                                
                        except Exception as e:
                            st.error(f"Error: {e}")
            
            # If spoken text exists, match with product
            if st.session_state.spoken_text:
                st.write(f"**Recognized text:** {st.session_state.spoken_text}")
                
                product = find_product_semantic_match(st.session_state.spoken_text, st.session_state.products)
                if product:
                    st.session_state.selected_product = product
                    st.success(f"Selected product: **{product['name']}**")
                else:
                    st.error("No matching product found")

        with col2:
            if st.session_state.selected_product:
                product = st.session_state.selected_product
                st.subheader("Selected Product")
                st.write(f"**Name:** {product['name']}")
                st.write(f"**Price:** Rs. {product.get('price', 'N/A')}")
                st.write(f"**Unit:** {product.get('uoM', 'N/A')}")
                st.write(f"**Tax Rate:** {product.get('taxRate', 'N/A')}%")
                
                quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
                
                if st.button("Generate Invoice", type="primary"):
                    invoice = generate_invoice(product, quantity)
                    if invoice:
                        st.session_state.invoice_history.append(invoice)
                        st.success("Invoice generated successfully!")
                        
                        # Show invoice details
                        st.subheader("Invoice Details")
                        st.write(f"**Invoice ID:** {invoice['invoiceId']}")
                        st.write(f"**Product:** {invoice['productName']}")
                        st.write(f"**Quantity:** {invoice['quantity']}")
                        st.write(f"**Unit Price:** Rs. {invoice['unitPrice']:,.2f}")
                        st.write(f"**Total Price:** Rs. {invoice['grandTotal']:,.2f}")
                        st.write(f"**Tax:** Rs. {invoice['salesTaxApplicable']:,.2f}")

    elif option == "View all products":
        st.header("All Products")
        
        search_term = st.text_input("Search product")
        
        filtered_products = st.session_state.products
        if search_term:
            filtered_products = [p for p in st.session_state.products 
                               if search_term.lower() in p['name'].lower()]
        
        if not filtered_products:
            st.warning("No products found")
        else:
            for product in filtered_products[:20]:
                with st.expander(f"{product['name']} - Rs. {product.get('price', 'N/A')}"):
                    st.write(f"**ID:** {product['id']}")
                    st.write(f"**Price:** Rs. {product.get('price', 'N/A')}")
                    st.write(f"**Unit:** {product.get('uoM', 'N/A')}")
                    st.write(f"**Tax Rate:** {product.get('taxRate', 'N/A')}%")

    elif option == "Invoice history":
        st.header("Invoice History")
        
        if not st.session_state.invoice_history:
            st.info("No invoices generated yet")
        else:
            for i, invoice in enumerate(reversed(st.session_state.invoice_history[-10:])):
                with st.expander(f"Invoice {invoice['invoiceId']} - Rs. {invoice['grandTotal']:,.2f}"):
                    st.write(f"**Product:** {invoice['productName']}")
                    st.write(f"**Quantity:** {invoice['quantity']}")
                    st.write(f"**Unit Price:** Rs. {invoice['unitPrice']:,.2f}")
                    st.write(f"**Total Price:** Rs. {invoice['grandTotal']:,.2f}")
                    st.write(f"**Tax:** Rs. {invoice['salesTaxApplicable']:,.2f}")

if __name__ == "__main__":
    main()
