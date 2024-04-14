# Libraries

from streamlit_folium import folium_static
from datetime         import datetime
from PIL              import Image

import folium
import pandas         as pd
import plotly.express as px
import streamlit      as st

# Read the training CSV

df = pd.read_csv(
    'C:/Users/gabre/DS IN PROGRESS/DS_2023/Ciclo_Basico/FTC Analisando dados com Python/FTC_project/train_1.csv')

# Cleaning and Modeling the data

df1 = df.copy()

# Convert the column Delivery_person_Age from object to number

df1['Delivery_person_Age'] = df1['Delivery_person_Age'].str.strip()
df1 = df1.loc[df1['Delivery_person_Age'] != 'NaN', :]
df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

# Convert the Delivery_person_Ratings from an object to float

df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

# Convert the column Order_Date from an object to datetime

df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )

# Convert multiple_deliveries from an object to int

df1['multiple_deliveries'] = df1['multiple_deliveries'].str.strip()
df1 = df1.loc[df1['multiple_deliveries'] != 'NaN', :]
df1 = df1.dropna( subset=['multiple_deliveries'] )
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

# Taking out all the spaces inside the strings

df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

# Taking out the NaN at Road_traffic_density and City

df1 = df1.loc[df1['Road_traffic_density'] != 'NaN', :]
df1 = df1.loc[df1['City'] != 'NaN', :]
df1 = df1.loc[df1['Festival'] != 'NaN', :]

# Remove the string (min) from Time_taken(min), and convert to int

df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.replace('(min) ', '' ) )
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )

# Company's View

# =============================
# Sidebar
# =============================

st.header( "Marketplace - Client's View" )

image_path = 'environmental_data science.jpg'
image = Image.open( image_path )
st.sidebar.image( image, width=250, use_column_width=True )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """___""" )
st.sidebar.markdown( '## Choose a limit period date' )

date_slider = st.sidebar.slider( 'Limit Date',
                                 value=datetime( 2022, 4, 6 ),
                                 min_value=datetime( 2022, 2, 11 ),
                                 max_value=datetime( 2022, 4, 6 ),
                                 format='DD-MM-YYYY'
                                 )

st.sidebar.markdown( """___""" )

traffic_options = st.sidebar.multiselect( 'Traffic Conditions',
                                          ['Low', 'Medium', 'High', 'Jam'],
                                          default=['Low', 'Medium', 'High', 'Jam']
                                          )

st.sidebar.markdown( """___""" )

st.sidebar.markdown( '### Powered by CDS' )

# Date filter

selected_line = df1['Order_Date'] <= date_slider
df1 = df1.loc[selected_line, :]

# Traffic filter

selected_line = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[selected_line, :]

# =============================
# Layout Streamlit
# =============================

# Create tabs to insert pages inside the home page

tab1, tab2, tab3 = st.tabs( ['Management View', 'Tactic View', 'Geographic View'] )

with tab1:
    with st.container():

        # The Chart Headline
        st.markdown( '# Orders by Day' )

        # Filtering data
        aux = df1[['ID', 'Order_Date']].groupby( 'Order_Date' ).count().reset_index()

        # Plotting using Plotly Express
        fig1 = px.bar( aux, x='Order_Date', y='ID', title='Plotly Bar Plot' )
        fig2 = px.line( aux, x='Order_Date', y='ID', title='Plotly Line Plot' )
        st.plotly_chart( fig1 )
        st.plotly_chart( fig2 )

    with st.container():

        # Creating columns
        col1, col2 = st.columns( 2 )

        # Column 1
        with col1:

            # The Chart Headline
            st.markdown( '### The orders distribution by each kind of traffic type' )

            # Filtering data
            aux = df1[['ID', 'Road_traffic_density']].groupby( 'Road_traffic_density' ).count().reset_index()
            aux = aux[( aux['Road_traffic_density'] != 'NaN' )]
            aux['delivery_percentage'] = aux['ID'] / aux['ID'].sum()

            # Plotting using Plotly Express
            fig = px.pie( aux, values='delivery_percentage', names='Road_traffic_density' )
            st.plotly_chart( fig, use_container_width=True )

        # Column 2
        with col2:

            # The Chart Headline
            st.markdown( '### Order volume Comparison by city and traffic type' )

            # Filtering data
            aux = df1[['ID', 'City', 'Road_traffic_density']].groupby(
                ['City', 'Road_traffic_density'] ).count().reset_index()
            aux = aux[( aux['City'] != 'NaN' ) & ( aux['Road_traffic_density'] != 'NaN' )]

            # Plotting using Plotly Express
            fig = px.scatter( aux, x='City', y='Road_traffic_density', size='ID', color='City' )
            st.plotly_chart( fig, use_container_width=True )

with tab2:
    with st.container():

        # The Chart Headline
        st.markdown( '### The quantity of orders by Week' )

        # Filtering data
        df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
        aux = df1[['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()

        # Plotting using Plotly Express
        fig = px.line( aux, x='week_of_year', y='ID' )
        st.plotly_chart( fig, use_container_width=True )

    with st.container():

        # The Chart Headline
        st.markdown( '### The number of orders by Delivery Man by weeks' )

        # Filtering data
        aux1 = df1[['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
        aux2 = df1[['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year' ).nunique().reset_index()
        aux = pd.merge( aux1, aux2, how='inner' )
        aux['order_by_deliveryman'] = aux['ID'] / aux['Delivery_person_ID']

        # Plotting using Plotly Express
        fig = px.line( aux, x='week_of_year', y='order_by_deliveryman' )
        st.plotly_chart( fig, use_container_width=True )

with tab3:

    # The Chart Headline
    st.markdown( '### The central location of each city' )

    # Filtering data
    aux = df1[['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude'
               ]].groupby( ['City', 'Road_traffic_density'] ).median().reset_index()
    aux = aux[( aux['City'] != 'NaN' ) & ( aux['Road_traffic_density'] != 'NaN' )]

    # Plotting using Folium
    map = folium.Map()

    for index, i in aux.iterrows():
        folium.Marker( [i['Delivery_location_latitude'],
                        i['Delivery_location_longitude']],
                       popup=i[['City', 'Road_traffic_density']]).add_to( map )
    folium_static( map, width=900, height=600 )
