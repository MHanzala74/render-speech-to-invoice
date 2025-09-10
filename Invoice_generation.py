from decimal import Decimal
import uuid
import streamlit as st

# Invoice generation
def generate_invoice(product, quantity=1):
    try:
        price = Decimal(product.get("price", 0))
        tax_rate_str = product.get("taxRate", "0%")
        tax_rate = Decimal(tax_rate_str.replace("%", "")) / 100 if tax_rate_str else Decimal(0)

        total_value = price * quantity
        sales_tax = total_value * tax_rate
        grand_total = total_value + sales_tax

        invoice = {
            "id": str(uuid.uuid4()),
            "invoiceId": "INV-" + str(uuid.uuid1().int)[:12],
            "productId": product["id"],
            "internalUomId": product.get("uoM", "pcs"),
            "quantity": int(quantity),
            "uomQuantity": int(quantity),
            "totalValues": float(total_value),
            "valueSalesExcludingST": float(total_value),
            "salesTaxApplicable": float(sales_tax),
            "grandTotal": float(grand_total),
            "productName": product["name"],
            "unitPrice": float(price),
            "taxRate": product.get("taxRate", "0%")
        }
        
        st.session_state.invoice_history.append(invoice)
        return invoice
    
    except Exception as e:
        st.error(f"Error creating invoice: {e}")
        return None
