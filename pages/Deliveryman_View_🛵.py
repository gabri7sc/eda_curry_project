# Libraries

from datetime import datetime
from PIL      import Image

import pandas    as pd
import streamlit as st

st.set_page_config( page_title="Deliveryman's View", page_icon='🛵', layout='wide' )

# Functions

def clean_code( df1 ):

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

    return df1

def overall_metrics_deliveryman( df1 ):

    col1, col2, col3, col4 = st.columns(4, gap='large')

    with col1:
        oldest_deliveryman = df1[["Delivery_person_ID", "Delivery_person_Age"]].max()[1]
        col1.metric('The Oldest Driver', oldest_deliveryman)

    with col2:
        youngest = df1[["Delivery_person_ID", "Delivery_person_Age"]].min()[1]
        col2.metric('The Youngest Driver', youngest)

    with col3:
        best_condition = df1[["Delivery_person_ID", "Vehicle_condition"]].max()[1]
        col3.metric('Best condition', best_condition)

    with col4:
        worst_condition = df1[["Delivery_person_ID", "Vehicle_condition"]].min()[1]
        col4.metric('Worst condition', worst_condition)

    return oldest_deliveryman, youngest, best_condition, worst_condition

def ratings( df1 ):

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('##### Average delivery Rating by Deliveryman')
        aux_1 = (df1[['Delivery_person_ID', 'Delivery_person_Ratings']].groupby('Delivery_person_ID')
                 .mean().sort_values('Delivery_person_Ratings', ascending=False).reset_index())
        st.dataframe(aux_1, height=520)

    with col2:
        st.markdown('##### Average delivery rating by Traffic density')

        aux_2 = (df1[['Delivery_person_Ratings', 'Road_traffic_density']]
                 .groupby('Road_traffic_density').agg({'Delivery_person_Ratings': ['mean', 'std']}))
        aux_2.columns = ['Delivery_mean', 'Delivery_std']
        aux_2.sort_values('Delivery_mean', ascending=False).reset_index()
        st.dataframe(aux_2)

        st.markdown('##### Average delivery rating by Weather')

        aux_3 = (df1[['Weatherconditions', 'Delivery_person_Ratings']]
                 .groupby('Weatherconditions').agg({'Delivery_person_Ratings': ['mean', 'std']}))
        aux_3.columns = ['mean_ratings', 'std_ratings']
        aux_3.sort_values('mean_ratings', ascending=False).reset_index()
        st.dataframe(aux_3)

    return aux_1, aux_2, aux_3

def delivery_time( df1 ):

    col1, col2 = st.columns( 2 )

    with col1:

        st.markdown( '##### The top 10 fastest deliverymen' )
        aux = df1[['City', 'Delivery_person_ID', 'Time_taken(min)']]

        # Get the top 10 fastest deliveries for each city

        aux_Urban = aux[aux['City'] == 'Urban'].nsmallest( 10, 'Time_taken(min)' )
        aux_Metropo = aux[aux['City'] == 'Metropolitian'].nsmallest( 10, 'Time_taken(min)' )
        aux_Semi_Urban = aux[aux['City'] == 'Semi-Urban'].nsmallest( 10, 'Time_taken(min)' )

        # Concatenate the results

        fastest_10 = pd.concat( [aux_Urban, aux_Metropo, aux_Semi_Urban] )

        # Display the result

        fastest_10 = fastest_10.reset_index( drop=True )
        st.dataframe( fastest_10 )

    with col2:

        st.markdown( '##### The top 10 slowest deliverymen' )
        aux = df1[['City', 'Delivery_person_ID', 'Time_taken(min)']]

        # Get the top 10 fastest deliveries for each city

        aux_Urban = aux[aux['City'] == 'Urban'].nlargest( 10, 'Time_taken(min)' )
        aux_Metropo = aux[aux['City'] == 'Metropolitian'].nlargest( 10, 'Time_taken(min)' )
        aux_Semi_Urban = aux[aux['City'] == 'Semi-Urban'].nlargest( 10, 'Time_taken(min)' )

        # Concatenate the results

        slowest_10 = pd.concat( [aux_Urban, aux_Metropo, aux_Semi_Urban] )

        # Display the result

        slowest_10 = slowest_10.reset_index( drop=True )
        st.dataframe( slowest_10 )

    return fastest_10, slowest_10

#------------------------#-----------------------------------------#---------------------------------#-------

# Read the training CSV

df = pd.read_csv( 'dataset/train_1.csv' )

# Cleaning and Modeling the data

df1 = clean_code( df )

# Company's View

# =============================
# Sidebar
# =============================

st.header( "Marketplace - Deliveryman's View" )

# image_path = 'C:/Users/gabre/DS IN PROGRESS/DS_2023/Ciclo_Basico/FTC Analisando dados com Python/FTC_pycharm/'
# image_filename = 'environmental_data science.jpg'
# full_image_path = image_path + image_filename
# image = Image.open( full_image_path )
image = Image.open( 'environmental_data science.jpg' )

st.sidebar.image( image, width=250, use_column_width=True )

st.sidebar.markdown( '# Curry Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """___""" )
st.sidebar.markdown( '## Choose a limit period date' )

date_slider = st.sidebar.slider(
    'Limit Date',
    value=datetime( 2022, 4, 13 ),
    min_value=datetime( 2022, 2, 11 ),
    max_value=datetime( 2022, 4, 6 ),
    format='DD-MM-YYYY'
)

st.sidebar.markdown( """___""" )

traffic_options = st.sidebar.multiselect(
    'Traffic Conditions',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown( """___""" )

weather_options = st.sidebar.multiselect(
    'Weather Conditions',
    ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
     'conditions Cloudy', 'conditions Fog', 'conditions Windy'],
    default=['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms', 'conditions Cloudy',
             'conditions Fog', 'conditions Windy']
)

st.sidebar.markdown( """___""" )
st.sidebar.markdown( '### Powered by CDS' )

# Date filter
selected_line = df1['Order_Date'] <= date_slider
df1 = df1.loc[selected_line, :]

# Traffic filter
selected_line = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[selected_line, :]

# Weather Filter
selected_line = df1['Weatherconditions'].isin( weather_options )
df1 = df1.loc[selected_line, :]

# =============================
# Layout Streamlit
# =============================

tab1, tab2, tab3 = st.tabs( ['Management View', 'soon', 'soon'] )

with tab1:

    with st.container():

        st.title('Overall Metrics')
        overall_metrics_deliveryman( df1 )

    with st.container():

        st.markdown( """___""" )
        st.title( 'Ratings' )
        ratings( df1 )

    with st.container():

        st.markdown( """___""" )
        st.title( 'Delivery Time' )
        delivery_time( df1 )
