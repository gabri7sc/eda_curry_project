# Libraries

from datetime  import datetime
from PIL       import Image
from haversine import haversine

import numpy                as np
import plotly.graph_objects as go
import pandas               as pd
import plotly.express       as px
import streamlit            as st

st.set_page_config( page_title="Restaurants' View", page_icon='🏬', layout='wide' )

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

def overall_metrics_rest( df1 ):
    col1, col2, col3, col4, col5, col6 = st.columns( 6, gap='medium' )

    with col1:
        aux_1 = len( df1['Delivery_person_ID'].unique() )
        col1.metric( 'Unique Deliverymen', aux_1 )

    with col2:
        df1['Distance'] = df1.apply( lambda x: haversine( (
            x['Delivery_location_latitude'], x['Delivery_location_longitude'] ),
            ( x['Restaurant_latitude'], x['Restaurant_longitude'] ) ), axis=1 )
        aux_2 = df1['Distance'].mean()
        col2.metric( 'Average distance', round( aux_2, 2 ) )

    with col3:
        aux_3 = ( df1[['Festival', 'Time_taken(min)']].groupby( 'Festival' )
                 .agg({'Time_taken(min)': ['mean', 'std']} ) )
        aux_3.columns = ['avg_time', 'std_time']
        aux_3 = aux_3.reset_index()
        aux_3 = aux_3.loc[aux_3['Festival'] == 'Yes', 'avg_time']
        col3.metric( 'Festivals Avg Time', round( aux_3, 2 ) )

    with col4:
        aux_4 = ( df1[['Festival', 'Time_taken(min)']].groupby( 'Festival' )
                 .agg( {'Time_taken(min)': ['mean', 'std']} ) )
        aux_4.columns = ['avg_time', 'std_time']
        aux_4 = aux_4.reset_index()
        aux_4 = aux_4.loc[aux_4['Festival'] == 'Yes', 'std_time']
        col4.metric( 'Festivals Std Time', round( aux_4, 2 ) )

    with col5:
        aux_5 = ( df1[['Festival', 'Time_taken(min)']].groupby( 'Festival' )
                 .agg( {'Time_taken(min)': ['mean', 'std']} ) )
        aux_5.columns = ['avg_time', 'std_time']
        aux_5 = aux_5.reset_index()
        aux_5 = aux_5.loc[aux_5['Festival'] == 'No', 'avg_time']
        col5.metric( 'Normal Avg Time', round( aux_5, 2 ) )

    with col6:
        aux_6 = ( df1[['Festival', 'Time_taken(min)']].groupby( 'Festival' )
                 .agg( {'Time_taken(min)': ['mean', 'std']} ) )
        aux_6.columns = ['avg_time', 'std_time']
        aux_6 = aux_6.reset_index()
        aux_6 = aux_6.loc[aux_6['Festival'] == 'No', 'std_time']
        col6.metric( 'Festivals Std Time', round( aux_6, 2 ) )

    return aux_1, aux_2, aux_3, aux_4, aux_5, aux_6

def average_delivery_time( df1 ):

    col1, col2 = st.columns( 2 )

    with col1:

        st.markdown( '##### By city' )

        aux = df1[['City', 'Time_taken(min)']].groupby( 'City' ).agg( {'Time_taken(min)': ['mean', 'std']} )
        aux = aux.reset_index()
        aux.columns = ['City', 'avg_time_delivery', 'std_time_delivery']

        fig_1 = go.Figure()
        fig_1.add_trace( go.Bar( name='Control', x=aux['City'], y=aux['avg_time_delivery'],
                               error_y=dict(type='data', array=aux['std_time_delivery'] ) ) )
        fig_1.update_layout( barmode='group' )
        st.plotly_chart( fig_1, use_container_width=True )

    with col2:

        st.markdown( '##### by City and Food' )

        df_aux = ( df1[['City', 'Type_of_order', 'Time_taken(min)']].groupby( ['City', 'Type_of_order'] )
                  .agg( {'Time_taken(min)': ['mean', 'std']} ) )
        df_aux = df_aux.reset_index()
        df_aux.columns = ['City', 'Type_of_order', 'avg_time', 'std_time']
        st.dataframe( df_aux )

    return fig_1, df_aux

def time_distribution( df1 ):

    col1, col2 = st.columns( 2 )

    with col1:

        aux = df1[['City', 'Time_taken(min)']].groupby( 'City' ).agg( {'Time_taken(min)': ['mean', 'std']} )
        aux = aux.reset_index()
        aux.columns = ['City', 'avg_time_delivery', 'std_time_delivery']

        fig_avg = aux[['City', 'avg_time_delivery']]
        fig_1 = go.Figure( data=[go.Pie( labels=fig_avg['City'],
                                        values=fig_avg['avg_time_delivery'],
                                        pull=[0, 0, 0.1] )] )
        fig_1.update_layout( margin=dict( t=0, b=0, l=0, r=0 ) )
        st.plotly_chart( fig_1, use_container_width=True )

    with col2:

        aux = df1[['City', 'Road_traffic_density', 'Time_taken(min)']].groupby(
            ['City', 'Road_traffic_density']).agg( {'Time_taken(min)': ['mean', 'std']} )
        aux = aux.reset_index()
        aux.columns = ['City', 'Road_traffic_density', 'avg_time', 'std_time']

        fig_2 = px.sunburst( aux, path=['City', 'Road_traffic_density'],
                            values='avg_time',
                            color='std_time',
                            color_continuous_scale='RdBu',
                            color_continuous_midpoint=np.average(aux['std_time'] ) )
        st.plotly_chart( fig_2, use_container_width=True )

    return fig_1, fig_2

#-------------------#---------------------------------------#------------------------------------------#-----

# Read the training CSV

df = pd.read_csv( 'dataset/train_1.csv' )

# Cleaning and Modeling the data

df1 = clean_code( df )

# Company's View

# =============================
# Sidebar
# =============================

st.header( "Marketplace - Restaurant's View" )

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

        st.title( 'Overall Metrics' )
        overall_metrics_rest( df1 )

    with st.container():

        st.markdown("""___""")
        st.title('Average Delivery Time')
        average_delivery_time( df1 )

    with st.container():

        st.markdown( """___""" )
        st.title( 'Time distribution' )
        time_distribution( df1 )
