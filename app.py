import streamlit as st
import pandas as pd
import os
import plotly.express as px
from io import BytesIO
import numpy as np

# Set page configuration
st.set_page_config(page_title="🚀 Data Sweeper", layout='wide')

# Custom styling with dark mode
st.markdown("""
    <style>
        body { background-color: black; color: white; }
        .stTextInput, .stFileUploader, .stButton, .stSelectbox, .stMultiselect, .stRadio, .stCheckbox { color: black !important; }
        .stDataFrame { background-color: #222 !important; color: white !important; }
        .stAlert { background-color: #333; color: white; }
    </style>
""", unsafe_allow_html=True)

# Sidebar for user input and file upload
st.sidebar.title("⚙️ User Input")
user_name = st.sidebar.text_input("Enter Your Name")

uploaded_files = st.sidebar.file_uploader(
    "📤 Upload your files (CSV or Excel):", 
    type=["csv", "xlsx"], 
    accept_multiple_files=True
)

if user_name:
    st.sidebar.success(f"Welcome, {user_name}!")

st.title("🚀 Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning, analysis, and visualization.")

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
    st.subheader(f"🧹 Data Cleaning for {file_name}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"Remove Duplicates from {file_name}"):
            df.drop_duplicates(inplace=True)
            st.success("✅ Duplicates Removed!")
    
    with col2:
        if st.button(f"Fill Missing Values for {file_name}"):
            numeric_cols = df.select_dtypes(include=['number']).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
            st.success("✅ Missing Values Filled!")
    
    with col3:
        if st.button(f"Remove Rows with Missing Values for {file_name}"):
            df.dropna(inplace=True)
            st.success("✅ Rows with Missing Values Removed!")
    
    return df

# Function for data visualization
def visualize_data(df, file_name):
    st.subheader(f"📈 Data Visualization for {file_name}")
    numeric_cols = df.select_dtypes(include=['number']).columns
    
    if len(numeric_cols) == 0:
        st.warning("⚠ No numeric columns found for visualization. Try selecting appropriate columns.")
    else:
        chart_type = st.radio("Select chart type:", ["Bar Chart", "Line Chart", "Histogram", "Scatter Plot"], key=f"chart_{file_name}")
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
        
        st.plotly_chart(fig)

# Function for file conversion
def convert_file(df, file_name, file_ext):
    st.subheader(f"🔄 File Conversion for {file_name}")
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

# Main logic
if uploaded_files:
    st.subheader(f"📂 Uploaded Files by {user_name}")
    
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()
        df = load_data(file)
        
        if df is not None:
            st.write(f"📁 **File Name:** {file.name}")
            st.write(f"📏 **File Size:** {file.size / 1024:.2f} KB")

            # Show dataframe preview
            st.write("🔍 **Preview of the Data**")
            st.dataframe(df, height=300)

            # Data Cleaning
            df = clean_data(df, file.name)

            # Select columns
            st.subheader(f"📌 Select Columns for {file.name}")
            columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
            df = df[columns]

            # Data Visualization
            visualize_data(df, file.name)

            # File Conversion
            convert_file(df, file.name, file_ext)

st.success("✅ All files processed successfully!")