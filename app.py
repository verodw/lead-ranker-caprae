import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os
import sys
import base64
from PIL import Image
from io import BytesIO

def get_base64_favicon(img_path: str) -> str:
    """Convert image to base64 for favicon use"""
    try:
        img = Image.open(img_path)
        img = img.resize((32, 32), Image.Resampling.LANCZOS)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode()
        return img_base64
    except Exception as e:
        print(f"Error creating favicon: {e}")
        return None

def img_to_html(img_path: str, width: int = 60) -> str:
    """Convert image to HTML for display"""
    try:
        with open(img_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode()
            return f'<img src="data:image/png;base64,{img_base64}" width="{width}px">'
    except Exception as e:
        print(f"Error converting image to HTML: {e}")
        return ""

def column_mapping(df):
    mapping = {
        'Company': ['Company', 'Name', 'Organization Name'],
        'Industry': ['Industry', 'Sector'],
        'Website': ['Website', 'URL', 'Company Website'],
        'EmployeeCount': ['EmployeeCount', 'Number of employees', 'Employees']
    }

    for target_col, candidates in mapping.items():
        for col in candidates:
            if col in df.columns:
                df[target_col] = df[col]
                break

    return df

favicon_base64 = get_base64_favicon("lead_ranker.png")
if favicon_base64:
    st.set_page_config(
        page_title="Lead Ranker - Caprae Capital",
        page_icon=f"data:image/png;base64,{favicon_base64}",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    favicon_html = f"""
    <link rel="icon" type="image/png" href="data:image/png;base64,{favicon_base64}">
    <link rel="shortcut icon" type="image/png" href="data:image/png;base64,{favicon_base64}">
    <link rel="apple-touch-icon" href="data:image/png;base64,{favicon_base64}">
    """
    st.markdown(favicon_html, unsafe_allow_html=True)
else:
    st.set_page_config(
        page_title="Lead Ranker - Caprae Capital",
        page_icon="🚀",  # Emoji sebagai fallback
        layout="wide",
        initial_sidebar_state="expanded"
    )
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from scoring import score_leads
except ImportError as e:
    st.error(f"Error importing scoring module: {e}")
    st.error("Please make sure scoring.py is in the same directory as app.py")
    st.stop()

try:
    from dotenv import load_dotenv
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
except ImportError:
    openai_api_key = None

# Custom CSS dengan favicon tambahan
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .stMetric {
        background-color: #f0f2f6;
        border: 1px solid #e1e5e9;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .upload-section {
        border: 2px dashed #cccccc;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #fafafa;
        margin: 1rem 0;
    }
    
    .sidebar-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: bold;
    }
    
    .lead-card {
        border-left: 4px solid;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
        background-color: white;
        color: #333; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .lead-card a {
        color: #1a0dab;
        text-decoration: underline;
    }

    .lead-card h4 {
        color: #222;
    }

    .lead-card p {
        color: #444;
    }
    
    .high-score { border-left-color: #28a745; background-color: #f8fff9; }
    .medium-score { border-left-color: #ffc107; background-color: #fffdf5; }
    .low-score { border-left-color: #dc3545; background-color: #fff5f5; }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-header">🎯 Lead Ranker Controls</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    img_html = img_to_html("lead_ranker.png", width=80)

    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0;">
        {img_html}
        <h1 style="color: #667eea; font-size: 3rem; margin-bottom: 0;">Lead Ranker</h1>
        <h3 style="color: #764ba2; margin-top: 0;">AI-Powered Lead Scoring for Caprae Capital</h3>
        <p style="color: #666; font-size: 1.1rem;">Transform your lead generation with intelligent scoring and insights</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="upload-section">', unsafe_allow_html=True)
st.markdown("### 📁 Upload Your Lead Data")
st.markdown("*Support CSV files with columns: Company, Industry, Website, EmployeeCount*")
uploaded_file = st.file_uploader("", type=["csv"], help="Upload your leads CSV file")
st.markdown('</div>', unsafe_allow_html=True)

if 'df_scored' not in st.session_state:
    st.session_state.df_scored = None
if 'df_original' not in st.session_state:
    st.session_state.df_original = None

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df = column_mapping(df)
        st.session_state.df_original = df
        
        required_columns = ['Company']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Missing required columns: {missing_columns}")
            st.info("Your CSV should have at least a 'Company' column. Optional columns: Industry, Website, EmployeeCount, Revenue")
            st.stop()
        
        with st.spinner('🔄 Scoring leads with AI...'):
            df_scored = score_leads(df, openai_api_key=openai_api_key)
            st.session_state.df_scored = df_scored
        
        st.sidebar.markdown("### 🔍 Filter Controls")
        
        min_score = int(df_scored['Score'].min())
        max_score = int(df_scored['Score'].max())
        score_threshold = st.sidebar.slider(
            "Minimum Lead Score",
            min_value=min_score,
            max_value=max_score,
            value=int(max_score * 0.7),
            help="Filter leads by minimum score"
        )
        
        if 'Industry' in df_scored.columns and df_scored['Industry'].notna().any():
            industries = ['All'] + list(df_scored['Industry'].dropna().unique())
            selected_industry = st.sidebar.selectbox("Industry Filter", industries)
        else:
            selected_industry = 'All'
        
        if 'EmployeeCount' in df_scored.columns and df_scored['EmployeeCount'].notna().any():
            emp_min, emp_max = st.sidebar.slider(
                "Employee Count Range",
                min_value=int(df_scored['EmployeeCount'].min()) if df_scored['EmployeeCount'].notna().any() else 0,
                max_value=int(df_scored['EmployeeCount'].max()) if df_scored['EmployeeCount'].notna().any() else 1000,
                value=(0, 1000)
            )
        else:
            emp_min, emp_max = 0, 1000
        
        filtered_df = df_scored[df_scored['Score'] >= score_threshold].copy()
        if selected_industry != 'All' and 'Industry' in df_scored.columns:
            filtered_df = filtered_df[filtered_df['Industry'] == selected_industry]
        if 'EmployeeCount' in df_scored.columns and df_scored['EmployeeCount'].notna().any():
            filtered_df = filtered_df[
                (filtered_df['EmployeeCount'] >= emp_min) & 
                (filtered_df['EmployeeCount'] <= emp_max)
            ]    
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📊 Total Leads",
                value=len(df_scored),
                help="Total number of leads processed"
            )
        
        with col2:
            high_quality = len(df_scored[df_scored['Score'] >= 80])
            st.metric(
                label="⭐ High Quality",
                value=high_quality,
                delta=f"{high_quality/len(df_scored)*100:.1f}%",
                help="Leads with score ≥ 80"
            )
        
        with col3:
            avg_score = df_scored['Score'].mean()
            st.metric(
                label="📈 Avg Score",
                value=f"{avg_score:.1f}",
                help="Average lead score"
            )
        
        with col4:
            st.metric(
                label="🎯 Filtered Results",
                value=len(filtered_df),
                delta=f"{len(filtered_df)/len(df_scored)*100:.1f}% of total",
                help="Leads matching current filters"
            )
        
        st.markdown("### 📊 Lead Analytics Dashboard")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            fig_hist = px.histogram(
                df_scored, 
                x='Score', 
                nbins=20,
                title="📈 Lead Score Distribution",
                color_discrete_sequence=['#667eea']
            )
            fig_hist.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12)
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with chart_col2:
            if 'Industry' in df_scored.columns and df_scored['Industry'].notna().any():
                industry_counts = df_scored.groupby('Industry')['Score'].agg(['count', 'mean']).reset_index()
                fig_bar = px.bar(
                    industry_counts,
                    x='Industry',
                    y='count',
                    title="🏢 Leads by Industry",
                    color='mean',
                    color_continuous_scale='Viridis'
                )
                fig_bar.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                score_categories = pd.cut(df_scored['Score'], 
                                        bins=[0, 60, 80, 100], 
                                        labels=['Low (0-60)', 'Medium (60-80)', 'High (80-100)'])
                cat_counts = score_categories.value_counts()
                
                fig_pie = px.pie(
                    values=cat_counts.values,
                    names=cat_counts.index,
                    title="🎯 Lead Quality Distribution",
                    color_discrete_sequence=['#ff7f7f', '#ffbf7f', '#7fbf7f']
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        st.markdown("### 🏆 Top Scoring Leads")
        
        display_col1, display_col2, display_col3 = st.columns([2, 1, 1])
        with display_col1:
            view_mode = st.radio("View Mode", ["Table", "Cards"], horizontal=True)
        with display_col2:
            rows_to_show = st.selectbox("Rows to Display", [10, 25, 50, 100], index=1)
        with display_col3:
            available_cols = [col for col in df_scored.columns if col not in ['scoring_rationale']]
            sort_by = st.selectbox("Sort By", ["Score"] + [col for col in available_cols if col != "Score"])
        
        display_df = filtered_df.sort_values(by=sort_by, ascending=False).head(rows_to_show)
        
        if view_mode == "Table":
            display_columns = ['Company', 'Score']
            if 'Industry' in df_scored.columns:
                display_columns.append('Industry')
            if 'Website' in df_scored.columns:
                display_columns.append('Website')
            if 'EmployeeCount' in df_scored.columns:
                display_columns.append('EmployeeCount')
            if 'scoring_rationale' in df_scored.columns:
                display_columns.append('scoring_rationale')
            
            display_columns = [col for col in display_columns if col in display_df.columns]
            
            st.dataframe(
                display_df[display_columns],
                use_container_width=True,
                height=400,
                column_config={
                    "Score": st.column_config.ProgressColumn(
                        "Lead Score",
                        help="AI-generated lead score",
                        min_value=0,
                        max_value=100,
                        format="%.1f"
                    ),
                    "Website": st.column_config.LinkColumn("Website") if "Website" in display_df.columns else None,
                }
            )
        else:
            for idx, row in display_df.iterrows():
                score = row['Score']
                if score >= 80:
                    card_class = "high-score"
                    score_emoji = "🟢 High"
                elif score >= 60:
                    card_class = "medium-score"
                    score_emoji = "🟡 Medium"
                else:
                    card_class = "low-score"
                    score_emoji = "🔴 Low"
                
                html_card = f"""
                    <div class="lead-card {card_class}">
                        <h4>
                            <span style="color: #555; font-weight: bold;">{score_emoji}</span><br>
                            {row.get('Company', 'Unknown Company')} - Score: {score:.1f}
                        </h4>
                        <p><strong>Industry:</strong> {row.get('Industry', 'N/A')} | <strong>Employees:</strong> {row.get('EmployeeCount', 'N/A')}</p>
                        <p><strong>Website:</strong> <a href="{row.get('Website', '#')}" target="_blank">{row.get('Website', 'N/A')}</a></p>
                        <p><strong>Rationale:</strong> {row.get('scoring_rationale', 'N/A')}</p>
                    </div>
                    """
                st.markdown(html_card, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.info("Please check your CSV file format and try again.")

if st.session_state.df_scored is not None:
    st.markdown("---")
    st.markdown("### 💾 Export Results")
    
    col1, col2 = st.columns(2)
    with col1:
        csv_data = st.session_state.df_scored.to_csv(index=False)
        st.download_button(
            label="📥 Download Scored Leads CSV",
            data=csv_data,
            file_name="scored_leads.csv",
            mime="text/csv",
            help="Download all scored leads as CSV file"
        )
    
    with col2:
        if len(filtered_df) > 0:
            filtered_csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="🎯 Download Filtered Results",
                data=filtered_csv,
                file_name="filtered_leads.csv",
                mime="text/csv",
                help="Download currently filtered leads as CSV file"
            )

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>🚀 <strong>Lead Ranker</strong> - AI-Powered Lead Scoring for Caprae Capital</p>
    <p>Built with ❤️ using Streamlit & OpenAI</p>
</div>
""", unsafe_allow_html=True)
