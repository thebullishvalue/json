import streamlit as st
import pandas as pd
import json
import io
import time

# --- CSS Styling (Matched to app.py) ---
def apply_styling():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        :root {
            --primary-color: #FFC300;
            --primary-rgb: 255, 195, 0;
            --background-color: #0F0F0F;
            --secondary-background-color: #1A1A1A;
            --bg-card: #1A1A1A;
            --bg-elevated: #2A2A2A;
            --text-primary: #EAEAEA;
            --text-secondary: #EAEAEA;
            --text-muted: #888888;
            --border-color: #2A2A2A;
            --border-light: #3A3A3A;
            
            --success-green: #10b981;
            --danger-red: #ef4444;
            --warning-amber: #f59e0b;
            --info-cyan: #06b6d4;
            --neutral: #888888;
        }
        
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Main background */
        .main {
            background-color: var(--background-color);
            color: var(--text-primary);
        }
        
        /* Hide sidebar elements */
        [data-testid="stSidebar"] {
            display: none;
        }

        .stApp > header {
            background-color: transparent;
        }
        
        .block-container {
            padding-top: 1rem;
            max-width: 1400px;
        }
        
        .premium-header {
            background: var(--secondary-background-color);
            padding: 1.25rem 2rem;
            border-radius: 16px;
            margin-bottom: 1.5rem;
            box-shadow: 0 0 20px rgba(var(--primary-rgb), 0.1);
            border: 1px solid var(--border-color);
            position: relative;
            overflow: hidden;
            margin-top: 2.5rem;
        }
        
        .premium-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 20% 50%, rgba(var(--primary-rgb),0.08) 0%, transparent 50%);
            pointer-events: none;
        }
        
        .premium-header h1 {
            margin: 0;
            font-size: 2.50rem;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.50px;
            position: relative;
        }
        
        .premium-header .tagline {
            color: var(--text-muted);
            font-size: 1rem;
            margin-top: 0.25rem;
            font-weight: 400;
            position: relative;
        }
        
        .info-box {
            background: var(--secondary-background-color);
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--primary-color);
            padding: 1.25rem;
            border-radius: 12px;
            margin: 0.5rem 0;
            box-shadow: 0 0 15px rgba(var(--primary-rgb), 0.08);
        }
        
        .info-box h4 {
            color: var(--primary-color);
            margin: 0 0 0.5rem 0;
            font-size: 1rem;
            font-weight: 700;
        }

        /* Buttons & Uploaders */
        .stButton>button {
            border: 2px solid var(--primary-color);
            background: transparent;
            color: var(--primary-color);
            font-weight: 700;
            border-radius: 12px;
            padding: 0.75rem 2rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            width: 100%;
        }
        
        .stButton>button:hover {
            box-shadow: 0 0 25px rgba(var(--primary-rgb), 0.6);
            background: var(--primary-color);
            color: #1A1A1A;
            transform: translateY(-2px);
        }

        [data-testid="stFileUploader"] {
            background-color: var(--secondary-background-color);
            padding: 20px;
            border-radius: 12px;
            border: 1px dashed var(--border-light);
        }

        /* Result Cards */
        .result-card {
            background-color: var(--bg-card);
            padding: 1.25rem;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            box-shadow: 0 0 15px rgba(var(--primary-rgb), 0.08);
            margin-bottom: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .section-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent 0%, var(--border-color) 50%, transparent 100%);
            margin: 2rem 0;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Logic Functions ---
def process_json_update(json_data, quantity_map):
    """
    Updates the quantity in the JSON structure based on the symbol map.
    """
    updated_count = 0
    # Iterate through the list of instruments in the JSON
    for item in json_data:
        try:
            symbol = item.get('instrument', {}).get('tradingsymbol')
            # If this symbol exists in our CSV data
            if symbol and symbol in quantity_map:
                new_quantity = int(quantity_map[symbol])
                # Update the quantity in 'params'
                if 'params' in item:
                    item['params']['quantity'] = new_quantity
                    updated_count += 1
        except Exception as e:
            st.warning(f"Error processing an item: {e}")
            continue
    return json_data, updated_count

# --- Main App ---
# Configure layout and collapse sidebar
st.set_page_config(page_title="Pragyam : JSON Utility", page_icon="📂", layout="wide", initial_sidebar_state="collapsed")
apply_styling()

# Header
st.markdown("""
<div class="premium-header">
    <h1>Pragyam : Broker JSON Sync</h1>
    <div class="tagline">Automated Portfolio File Updater Utility</div>
</div>
""", unsafe_allow_html=True)

# Instructions (Moved from Sidebar)
with st.expander("ℹ️  Utility Instructions & Guide", expanded=False):
    st.info("""
    **How to use:**
    1. Upload your curated portfolio CSV (generated from the main app).
    2. Upload the raw JSON order files (ETF.json) from your broker.
    3. The system maps quantities by symbol and generates clean import files.
    """)

# Main Content
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.markdown("### 1. Data Sources")
    
    st.markdown("#### Portfolio Input")
    csv_file = st.file_uploader("Upload 'curated_portfolio.csv'", type=['csv'], help="The output file from the Pragyam Curation Engine.")

    st.markdown("#### JSON Templates")
    json_files = st.file_uploader("Upload Broker JSONs", type=['json'], accept_multiple_files=True, help="Your original ETF.json or ETF 2.0.json files.")

    if csv_file and json_files:
        st.success(f"ready to process {len(json_files)} templates.")

with col2:
    st.markdown("### 2. Processing Engine")
    
    if csv_file is None:
        st.markdown("""
        <div class='info-box'>
            <h4>Waiting for Input</h4>
            <p>Please upload the generated CSV file to begin the synchronization process.</p>
        </div>
        """, unsafe_allow_html=True)
        
    elif not json_files:
        st.markdown("""
        <div class='info-box'>
            <h4>Waiting for Templates</h4>
            <p>Please upload the JSON templates you wish to update.</p>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        try:
            # 1. Read the CSV
            df = pd.read_csv(csv_file)
            df.columns = df.columns.str.strip() # Normalize headers
            
            if 'symbol' in df.columns and 'units' in df.columns:
                qty_map = dict(zip(df['symbol'], df['units'].fillna(0).astype(int)))
                
                st.markdown(f"""
                <div class='info-box'>
                    <h4>Map Loaded Successfully</h4>
                    <p>Found <strong>{len(qty_map)}</strong> symbols in the portfolio CSV.</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("View Source Map Data"):
                    st.dataframe(df[['symbol', 'units', 'weightage_pct']].head(), use_container_width=True)

                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                st.subheader("Generated Output Files")

                # 2. Process Files
                for j_file in json_files:
                    j_file.seek(0)
                    file_name = j_file.name
                    
                    try:
                        json_content = json.load(j_file)
                        updated_json, count = process_json_update(json_content, qty_map)
                        json_output = json.dumps(updated_json, indent=4)
                        
                        # Styled Result Card
                        st.markdown(f"""
                        <div class="result-card">
                            <div>
                                <h4 style="margin:0; color: var(--primary-color);">{file_name}</h4>
                                <small style="color: var(--text-muted);">Updated {count} instruments</small>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.download_button(
                            label=f"⬇️ Download Updated {file_name}",
                            data=json_output,
                            file_name=f"updated_{file_name}",
                            mime="application/json",
                            key=file_name
                        )
                            
                    except Exception as e:
                        st.error(f"Error reading {file_name}: {str(e)}")
            else:
                st.error("CSV format incorrect. Columns 'symbol' and 'units' are required.")
                st.dataframe(df.head())
                
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Footer (Moved from Sidebar to Main Page Bottom)
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.caption(f"© {pd.Timestamp.now().year} Pragyam Utility")
