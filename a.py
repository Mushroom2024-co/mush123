import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Set the title of the app
st.set_page_config(page_title="Mushroom Farm Monitoring System", layout="wide")

# Add custom CSS for background and styling
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(to right, #f0f4f8, #d9e4ef);
        color: #333;
        font-family: 'Arial', sans-serif;
    }
    .reportview-container .main {
        padding: 2rem;
        border-radius: 8px;
        background-color: rgba(255, 255, 255, 0.9);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    h1 {
        color: #3F51B5;
        text-align: center;
    }
    h2, h3 {
        color: #3F51B5;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Set the header of the app
st.title("Mushroom Farm Monitoring System")

# Google Sheets data URL
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1S5rbM_i_k_mmWcaT5HfD53hGuAjesUjd7J5TfD8qKT8/gviz/tq?tqx=out:csv"

# Load the data from Google Sheets (CSV format)
@st.cache_data(ttl=5)  # Cache data for 5 seconds
def load_data():
    try:
        data = pd.read_csv(spreadsheet_url)
        # Check required columns
        required_columns = [
            'Timestamp', 'Fan State', 'Humidifier State', 
            'LED Brightness', 'Temperature', 'Humidity', 
            'Soil Moisture', 'Light Intensity'
        ]
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            st.error(f"Missing columns in the data: {', '.join(missing_columns)}")
            return pd.DataFrame()  # Return an empty DataFrame if columns are missing
        
        # Convert 'Timestamp' to datetime
        data['Timestamp'] = pd.to_datetime(data['Timestamp'], errors='coerce')
        data = data.dropna(subset=['Timestamp'])  # Drop rows with invalid timestamps
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error

# Function to display the filtered data by date range
def show_filtered_data(data):
    st.subheader("Filter Data by Date Range")

    if data.empty:
        st.error("No data loaded. Please check your Google Sheets link or data format.")
        return

    # Initialize session state for dates
    if 'start_date' not in st.session_state:
        st.session_state.start_date = data['Timestamp'].min().date()
    if 'end_date' not in st.session_state:
        st.session_state.end_date = data['Timestamp'].max().date()

    start_date = st.date_input("Start Date", value=st.session_state.start_date, key="start_date_input")
    end_date = st.date_input("End Date", value=st.session_state.end_date, key="end_date_input")

    st.session_state.start_date = start_date
    st.session_state.end_date = end_date

    filtered_data = data[(data['Timestamp'].dt.date >= start_date) & (data['Timestamp'].dt.date <= end_date)]
    
    if filtered_data.empty:
        st.warning("No data available for the selected date range.")
        return

    st.write(filtered_data)

    # Plot Fan and Humidifier States
    st.subheader("Fan and Humidifier States Over Time")
    try:
        fan_humidifier_data = filtered_data[['Timestamp', 'Fan State', 'Humidifier State']].melt(
            id_vars=['Timestamp'], value_vars=['Fan State', 'Humidifier State'], var_name='State', value_name='Status'
        )
        fig_fan_humidifier = px.bar(
            fan_humidifier_data,
            x="Timestamp",
            y="Status",
            color="State",
            title="Fan and Humidifier States Over Time",
            barmode="group",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig_fan_humidifier.update_layout(xaxis_title="Timestamp", yaxis_title="State", xaxis=dict(tickformat='%Y-%m-%d %H:%M'))
        st.plotly_chart(fig_fan_humidifier, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating Fan and Humidifier plot: {e}")

    # Display LED state distribution
    st.subheader("LED State Distribution")
    try:
        if 'LED Brightness' in filtered_data.columns:
            led_count = filtered_data['LED Brightness'].value_counts()
            fig_led = px.pie(
                values=led_count.values,
                names=led_count.index,
                title="LED State Distribution",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Plotly,
                labels={'values': 'Count', 'names': 'LED Brightness'},
            )
            fig_led.update_traces(textinfo='percent+label')
            fig_led.update_layout(showlegend=True)
            st.plotly_chart(fig_led, use_container_width=True)
        else:
            st.warning("The column 'LED Brightness' is missing from the data.")
    except Exception as e:
        st.error(f"Error creating LED distribution chart: {e}")

# Function to display temperature and humidity over time
def show_temp_humidity(data):
    st.subheader("Temperature and Humidity Over Time")
    try:
        fig_temp_humidity = plt.figure(figsize=(12, 6))
        plt.plot(data['Timestamp'], data['Temperature'], label='Temperature (°C)', color='tab:red', linewidth=2)
        plt.plot(data['Timestamp'], data['Humidity'], label='Humidity (%)', color='tab:blue', linewidth=2)
        plt.xlabel('Timestamp')
        plt.ylabel('Value')
        plt.title('Temperature and Humidity Over Time', fontsize=16)
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid()
        st.pyplot(fig_temp_humidity)
    except Exception as e:
        st.error(f"Error plotting Temperature and Humidity: {e}")

# Function to display soil moisture and light intensity over time
def show_soil_light(data):
    st.subheader("Soil Moisture and Light Intensity Over Time")
    try:
        fig_soil_light = plt.figure(figsize=(12, 6))
        plt.plot(data['Timestamp'], data['Soil Moisture'], label='Soil Moisture (raw)', color='tab:green', linewidth=2)
        plt.plot(data['Timestamp'], data['Light Intensity'], label='Light Intensity (lux)', color='tab:orange', linewidth=2)
        plt.xlabel('Timestamp')
        plt.ylabel('Value')
        plt.title('Soil Moisture and Light Intensity Over Time', fontsize=16)
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid()
        st.pyplot(fig_soil_light)
    except Exception as e:
        st.error(f"Error plotting Soil Moisture and Light Intensity: {e}")

# Main app content
def main():
    data = load_data()
    show_filtered_data(data)
    show_temp_humidity(data)
    show_soil_light(data)

# Button to refresh data
if st.button('Refresh Data'):
    main()
else:
    main()
