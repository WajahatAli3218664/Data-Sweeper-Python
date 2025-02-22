import streamlit as st
import pandas as pd
import os
import plotly.express as px
from io import BytesIO
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(page_title="✨ Data Sweeper", layout='wide')

# Custom styling with improvements
st.markdown("""
    <style>
        body { background-color: #1e1e2e; color: white; }
        .stTextInput, .stFileUploader, .stButton, .stSelectbox, .stMultiselect, .stRadio, .stCheckbox { color: black !important; }
        .stDataFrame { background-color: #2e2e3e !important; color: white !important; }
        .stAlert { background-color: #3e3e4e; color: white; }
        .success-msg { background-color: #28a745; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; }
        .welcome-msg { background-color: #007bff; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; }
        .cleaning-msg { background-color: #ffcc00; color: black; padding: 12px; border-radius: 5px; text-align: center; font-weight: bold; margin-bottom: 10px; }
        .stButton > button:hover { transform: scale(1.05); transition: 0.3s ease-in-out; }
        .custom-button { background-color: #6c757d; color: white; padding: 10px; border-radius: 5px; font-weight: bold; border: none; cursor: pointer; }
        .custom-button:hover { background-color: #5a6268; }
    </style>
""", unsafe_allow_html=True)

# Sidebar for user input and file upload
st.sidebar.title("⚙️ User Controls")
user_name = st.sidebar.text_input("📝 Enter Your Name")

uploaded_files = st.sidebar.file_uploader(
    "📤 Upload CSV or Excel Files:", 
    type=["csv", "xlsx"], 
    accept_multiple_files=True
)

if user_name:
    st.sidebar.markdown(f'<div class="welcome-msg">🚀 Welcome, {user_name}!</div>', unsafe_allow_html=True)

st.title("🧹✨ Data Sweeper – Smart Cleaning & Conversion 🔄")
st.write("📊 Unlock the true potential of your data—effortlessly clean, analyze, and visualize your information for smarter insights and better decisions!.")

# Function to load data
def load_data(file):
    file_ext = os.path.splitext(file.name)[-1].lower()
    if file_ext == ".csv":
        return pd.read_csv(file)
    elif file_ext == ".xlsx":
        return pd.read_excel(file)
    else:
        st.error(f"Unsupported File Type: {file_ext}")
        return None

# Function to clean data
def clean_data(df, file_name):
    st.markdown(f'<div class="cleaning-msg">🧹 Cleaning Data: {file_name}</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"🚫 Remove Duplicates", key=f"remove_duplicates_{file_name}"):
            df.drop_duplicates(inplace=True)
            st.success("✅ Duplicates Removed!")
    
    with col2:
        if st.button(f"🔄 Fill Missing Values", key=f"fill_missing_{file_name}"):
            numeric_cols = df.select_dtypes(include=['number']).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
            st.success("✅ Missing Values Filled!")
    
    with col3:
        if st.button(f"❌ Drop Missing Values", key=f"drop_missing_{file_name}"):
            df.dropna(inplace=True)
            st.success("✅ Empty Rows Removed!")
    
    return df

# Function for data visualization
def visualize_data(df, file_name):
    st.subheader(f"📊 Visualizing Data: {file_name}")
    numeric_cols = df.select_dtypes(include=['number']).columns
    
    if len(numeric_cols) == 0:
        st.warning("⚠ No numeric columns found for visualization.")
    else:
        chart_type = st.radio("Choose Chart Type:", ["Bar Chart", "Line Chart", "Histogram", "Scatter Plot", "Pie Chart", "Box Plot"], key=f"chart_{file_name}")
        x_axis = st.selectbox("Select X-axis:", numeric_cols, key=f"x_{file_name}")
        y_axis = st.selectbox("Select Y-axis:", numeric_cols, key=f"y_{file_name}") if len(numeric_cols) > 1 else x_axis
        
        if chart_type == "Bar Chart":
            fig = px.bar(df, x=x_axis, y=y_axis, color=x_axis)
        elif chart_type == "Line Chart":
            fig = px.line(df, x=x_axis, y=y_axis, color=x_axis)
        elif chart_type == "Histogram":
            fig = px.histogram(df, x=x_axis, color=x_axis)
        elif chart_type == "Scatter Plot":
            fig = px.scatter(df, x=x_axis, y=y_axis, color=x_axis)
        elif chart_type == "Pie Chart":
            fig = px.pie(df, names=x_axis, values=y_axis)
        elif chart_type == "Box Plot":
            fig = px.box(df, x=x_axis, y=y_axis, color=x_axis)
        
        st.plotly_chart(fig)

# Function for file conversion
def convert_file(df, file_name, file_ext):
    st.subheader(f"🔄 Convert File: {file_name}")
    conversion_type = st.radio(f"Convert {file_name} to:", ["CSV", "Excel"], key=f"conv_{file_name}")

    if st.button(f"Convert {file_name} to {conversion_type}"):
        buffer = BytesIO()
        
        if conversion_type == "CSV":
            df.to_csv(buffer, index=False)
            file_name = file_name.replace(file_ext, ".csv")
            mime_type = "text/csv"
        else:
            df.to_excel(buffer, index=False)
            file_name = file_name.replace(file_ext, ".xlsx")
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        buffer.seek(0)

        st.download_button(
            label=f"⬇ Download {file_name} as {conversion_type}",
            data=buffer.getvalue(),
            file_name=file_name,
            mime=mime_type
        )

# Function to display summary statistics
def show_summary_stats(df, file_name):
    st.subheader(f"📊 Summary Statistics: {file_name}")
    st.write(df.describe())

# Function to display correlation matrix
def show_correlation_matrix(df, file_name):
    st.subheader(f"📊 Correlation Matrix: {file_name}")
    numeric_cols = df.select_dtypes(include=['number']).columns
    
    if len(numeric_cols) > 1:
        corr = df[numeric_cols].corr()
        fig, ax = plt.subplots()
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)
    else:
        st.warning("⚠ Not enough numeric columns to generate a correlation matrix.")

# Main logic
if uploaded_files:
    st.subheader(f"📂 Uploaded Files by {user_name}")
    
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()
        df = load_data(file)
        
        if df is not None:
            df = clean_data(df, file.name)
            show_summary_stats(df, file.name)
            show_correlation_matrix(df, file.name)
            visualize_data(df, file.name)
            convert_file(df, file.name, file_ext)

st.markdown('<div class="success-msg">✅ Processing Complete!</div>', unsafe_allow_html=True)