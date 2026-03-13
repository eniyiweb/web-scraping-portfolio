"""
Streamlit Dashboard for Price Monitor
Visualize price history and manage tracked products
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from price_monitor import PriceMonitor, PriceDatabase

st.set_page_config(
    page_title="Price Monitor Dashboard",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Price Monitoring Dashboard")

# Initialize
monitor = PriceMonitor()
db = PriceDatabase()

# Sidebar
st.sidebar.header("⚙️ Actions")

if st.sidebar.button("🔄 Check All Prices"):
    with st.spinner("Checking prices..."):
        monitor.check_prices()
    st.success("Prices updated!")

st.sidebar.markdown("---")

# Add new product
st.sidebar.subheader("➕ Add Product")
new_name = st.sidebar.text_input("Product Name")
new_url = st.sidebar.text_input("Product URL")

if st.sidebar.button("Add to Monitor"):
    if new_name and new_url:
        monitor.add_product(new_name, new_url)
        st.sidebar.success(f"Added {new_name}")
    else:
        st.sidebar.error("Name and URL required")

# Main content
tab1, tab2 = st.tabs(["📊 Current Prices", "📈 Price History"])

with tab1:
    st.header("Tracked Products")
    
    products = db.get_all_products()
    
    if not products:
        st.info("No products being tracked. Add one from the sidebar!")
    else:
        # Create DataFrame
        data = []
        for p in products:
            price_change = ""
            if p.price_dropped():
                change = abs(p.price_change_percent())
                price_change = f"📉 -{change:.1f}%"
            elif p.current_price and p.previous_price:
                if p.current_price > p.previous_price:
                    change = p.price_change_percent()
                    price_change = f"📈 +{change:.1f}%"
            
            data.append({
                'Product': p.name,
                'Current Price': f"${p.current_price:.2f}" if p.current_price else "N/A",
                'Previous': f"${p.previous_price:.2f}" if p.previous_price else "N/A",
                'Change': price_change,
                'Last Checked': p.last_checked[:10] if p.last_checked else "Never"
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        # Price drops highlight
        drops = [p for p in products if p.price_dropped()]
        if drops:
            st.success(f"🎉 {len(drops)} price drop(s) detected!")
            for p in drops:
                st.markdown(f"**{p.name}**: ${p.previous_price:.2f} → ${p.current_price:.2f}")

with tab2:
    st.header("Price History")
    
    if products:
        selected = st.selectbox(
            "Select Product",
            options=[(p.id, p.name) for p in products],
            format_func=lambda x: x[1]
        )
        
        if selected:
            product_id, product_name = selected
            history = db.get_price_history(product_id)
            
            if history:
                df_hist = pd.DataFrame(history)
                df_hist['date'] = pd.to_datetime(df_hist['date'])
                
                fig = px.line(
                    df_hist, 
                    x='date', 
                    y='price',
                    title=f"Price History: {product_name}",
                    labels={'price': 'Price ($)', 'date': 'Date'}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Export
                csv = df_hist.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    f"{product_name.replace(' ', '_')}_history.csv",
                    "text/csv"
                )
            else:
                st.info("No price history yet. Check prices first!")

# Footer
st.markdown("---")
st.caption("💡 Tip: Set up EMAIL_SMTP and EMAIL_USER in .env for email alerts")
