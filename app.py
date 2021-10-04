import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import plotly.graph_objects as go


@st.cache
# Function to read in CSV files and create dataframes
def get_data(fname='National_Register_of_Historic_Places.csv'):
    return pd.read_csv(fname)


# Function to display map
def map_plot(df):
    st.map(df)


# Function to display map with filter by county
def map_plot2(df, column1, column2):
    # Create dataframe with unique column names for the selectbox
    choices = df[column1].unique()
    # Allow the user to select which county to look at on the map
    choice = st.sidebar.selectbox('Select a county:', choices)

    # Create new dataframe with historic places only from the county the user selects
    new_df = df.loc[df[column1] == choice]

    # Ask if the user would like to see a list of the historic places in their county of choice
    display = st.checkbox(f'Do you want to see a list of the historic places in {choice} county?')
    # If they check the box:
    if display:
        # Display portion of dataframe with name
        new_df_display = new_df[column2]
        st.write(new_df_display)

    # Return a map with coordinates of each historic place in the county selected
    st.map(new_df)


# Function to display pie chart
def pie_plot(dictionary):
    # Assign keys (county names) to variable counties
    counties = dictionary.keys()
    # Assign values (frequencies) to variable freq
    freq = dictionary.values()

    pie = px.pie(values=freq,
                 names=counties,
                 color=counties,
                 title='Percent of Registered Historic Places by County')

    # Display pie chart
    st.plotly_chart(pie)


# Function to display cumulative histogram
def cum_hist(df, column):
    # Use plotly.graph_objects to create cumulative histogram
    fig = go.Figure(data=[go.Histogram(x=df[column], cumulative_enabled=True)])
    fig.update_layout(
        title='Total Number of Registered Historic Places Each Year',
        xaxis_title='Year',
        yaxis_title='Number of Historic Places Registered')

    # Display histogram
    st.plotly_chart(fig)


# Function to return descriptive statistics
def describe(df):
    return df.describe()


# Function to display bar plot
def bar_plot(df, column1, column2):
    # Set x equal to place names
    x = df[column2]
    bar_width = 0.75

    fig, ax = plt.subplots()
    # x-axis is place names, y-axis is attendance
    ax.bar(x, df[column1], width=bar_width, color='pink', edgecolor='blue')

    # Set x-ticks to be place names
    ax.set_xticks(x)
    ax.set_xticks(df[column2])
    plt.xticks(rotation=90)
    # Set y-ticks to be more uniform
    plt.yticks(np.arange(1000000, 8500000, step=1000000))
    # Add a grid
    ax.grid(axis='y', linestyle='--')

    # Add a title
    plt.title('Most Visited Historic Places in 2020')
    # Add x label and y label
    plt.xlabel('Historic Place')
    plt.ylabel('Attendance')

    # Display bar plot
    st.pyplot(fig)


def main():
    # Load in Historic Places Data
    df_place = get_data()

    # Load in Attendance Data
    df_attendance = get_data(fname="Attendance.csv")
    # Only include entries in the dataframe from 2020
    df_attendance = df_attendance.loc[df_attendance['Year'] == 2020]
    # Extract facility, county, and attendance columns from the dataframe
    df_attendance = df_attendance[['Facility', 'County', 'Attendance']]
    # Rename 'Facility' column to match Historic Places column names
    df_attendance.columns = ['Resource Name', 'County', 'Attendance']

    # Add title and introduction to the application
    st.title('National Register of Historic Places in New York')
    st.markdown('Welcome to this application! Here you will find '
                'information about historic locations in New York.')

    # Dataframe Section
    st.header('Table of Historic Places')
    st.markdown('Here you can see a list of all historic places in '
                'New York! Filter by Name, County, and more by '
                'clicking on the column header of your choice.')
    # Display dataframe
    st.dataframe(df_place)

    # Make a title for the sidebar
    st.sidebar.title('Filter Data')

    # Map Section
    st.markdown('#')
    st.header('Map of New York')
    # Extract portion of dataframe used to make the map
    df_map = df_place[['Resource Name', 'County', 'Latitude', 'Longitude']]
    # Rename columns
    df_map.columns = ['Resource Name', 'County', 'lat', 'lon']
    # Call map_plot() function to display map
    st.subheader('All Historic Places')
    map_plot(df_map)
    # Call map_plot2() function to display filter map
    st.subheader('Examine One County at a Time Using Sidebar')
    map_plot2(df_map, 'County', 'Resource Name')

    # Pie Chart Section
    st.markdown('#')
    st.header('Location by County')
    # Create empty dictionary
    dict_counties = {}
    for county in df_place['County']:
        # Initialize number of historic places in each county
        county_freq = 0
        # Create a dictionary of unique county names
        if county not in dict_counties:
            # Set the county name as the key and set the frequency as the value
            dict_counties[county] = county_freq
        # For each historic place in the dataframe, add 1 to the frequency of its respective county
        for place in df_place:
            if county in dict_counties:
                dict_counties[county] += 1
    # Call pie_plot() function to display pie chart
    pie_plot(dict_counties)

    # Cumulative Histogram Section
    st.markdown('#')
    st.header('Number of Historic Places Registered Over Time')
    st.write('Excludes some historic places that do not have a registration date.')
    # Create a copy of the place dataframe so that when NaN rows are removed, it will not affect the original dataframe
    df_place_copy = df_place.copy()
    # Drop NaN rows
    df_place_copy.dropna(subset=['National Register Date'], inplace=True)
    # Replace slashes with dashes in the National Register Date column
    for date in df_place_copy['National Register Date']:
        date.replace('/', '-')
    # Convert date strings to Date/Time format
    df_place_copy['National Register Date'] = pd.to_datetime(df_place_copy['National Register Date'])
    # Add column to the dataframe with just the register year
    df_place_copy['Register Year'] = pd.DatetimeIndex(df_place_copy['National Register Date']).year
    # Call cum_hist() function to display cumulative histogram
    cum_hist(df_place_copy, 'Register Year')

    # Attendance Section
    st.markdown('#')
    st.header('Attendance at National Historic Places in 2020')
    st.subheader('Descriptive Statistics')
    st.write('Attendance not collected for every historic place.')
    # Call describe() function to get descriptive statistics
    st.write(describe(df_attendance))
    st.subheader('Top 10 Most Visited Historic Places in 2020')
    # Find 10 largest values for attendance and create a new dataframe
    top10 = df_attendance.nlargest(10, 'Attendance')
    # Ask if the user would like to see a list of these historic places
    display = st.checkbox(f'Do you want to see a list of these places and their attendance?')
    # If they check the box:
    if display:
        # Display portion of dataframe with name, county, and attendance
        st.dataframe(top10)
    # Call bar_plot() function to display bar plot of attendance for 10 largest attendance values
    bar_plot(top10, 'Attendance', 'Resource Name')

    # Quote about New York for fun
    st.markdown('##')
    st.write('"Must I tell you that neither the Alps nor the '
             'Appenines, nor even Aetna itself, have dimmed, '
             'in my eyes, the beauty of our Catskills."   '
             '-Thomas Cole, Founder of Hudson River School of Art')


main()
