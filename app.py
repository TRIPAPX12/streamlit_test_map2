import streamlit as st 
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)


APP_TITLE = "Patient Density Report"
APP_SUB_TITLE = "Source : CMS LDS Data"

def display_claims(df,field_name,metric_title):
    total = df[field_name].sum()
    st.metric(metric_title, '{:,}'.format(total))

def display_facility_count(df,field_name,metric_title):
    total = df[field_name].count()
    st.metric(metric_title, '{:,}'.format(total))

def display_map(df):
    
    map = folium.Map(location = [38, -90]
                    ,zoom_start = 3
                    #,scrollWheelZoom=False # Freezes the zoom
                    #,tiles = 'CartoDB positron'
                    )
                    
    choropleth = folium.Choropleth(
        name="State Level Counts"
        ,geo_data = 'us-state-boundaries.geojson'
        ,data = df
        ,columns = ["Mapped_State_Name","State_Level_Claim_Count"]
        ,key_on = 'feature.properties.name'
        ,fill_color='YlGn'
        ,line_opacity = 0.8
        ,highlight = True
    ).add_to(map)

    choropleth.geojson.add_child(folium.features.GeoJsonTooltip(['name'], labels = False))
    
    claimsLayer = folium.FeatureGroup("#Claims")

    for itr in range(len(df)):
        latStr = df.iloc[itr]["Final_Latitude"]
        lngStr = df.iloc[itr]["Final_Longitude"]
        site_name = df.iloc[itr]["Provider Organization Name (Legal Business Name)"]
        npi = df.iloc[itr]["ORG_NPI_NUM"]
        claims = df.iloc[itr]["Claims"]
        non_white = df.iloc[itr]["% non-white"]
        masked_non_white = df.iloc[itr]["Masked Racial Diversity"]
        extirpation = df.iloc[itr]["% treated with extirpation"]
        masked_extirpation = df.iloc[itr]["Masked Extirpation"]
        #clr = "blue" if df.iloc[itr]["Deciles"] == 'Decile 1' else 'red'
        clr = "blue"
        radius = (df.iloc[itr]["Claims"])*100
    
        # derive the circle pop up html content
        popUpStr = 'Site Name - {0}<br>NPI - {1}<br>Claims - {2}<br>%Non-white - {3}<br>%Extirpation - {4}'.format(
            site_name,
            npi,
            claims,
            masked_non_white,
            masked_extirpation)
        folium.Circle(
            location = [latStr, lngStr],
            popup = folium.Popup(popUpStr, min_width=100, max_width=700),
            radius = radius,
            color = clr,
            weight=2,
            fill=True,
            fill_color=clr,
            fill_opacity=0.1
        ).add_to(claimsLayer)


    RacialDiversity = folium.FeatureGroup("Racial Diversity")

    for itr in range(len(df)):
        latStr = df.iloc[itr]["Final_Latitude"]
        lngStr = df.iloc[itr]["Final_Longitude"]
        site_name = df.iloc[itr]["Provider Organization Name (Legal Business Name)"]
        npi = df.iloc[itr]["ORG_NPI_NUM"]
        claims = df.iloc[itr]["Claims"]
        non_white = df.iloc[itr]["% non-white"]
        masked_non_white = df.iloc[itr]["Masked Racial Diversity"]
        extirpation = df.iloc[itr]["% treated with extirpation"]
        masked_extirpation = df.iloc[itr]["Masked Extirpation"]
        clr = 'red'
        radius = (df.iloc[itr]["% non-white"])*1000
        
        # derive the circle pop up html content
        popUpStr = 'Site Name - {0}<br>NPI - {1}<br>Claims - {2}<br>%Non-white - {3}<br>%Extirpation - {4}'.format(
            site_name,
            npi,
            claims,
            masked_non_white,
            masked_extirpation)
        folium.Circle(
            location = [latStr, lngStr],
            popup = folium.Popup(popUpStr, min_width=100, max_width=700),
            radius = radius,
            color = clr,
            weight=2,
            fill=True,
            fill_color=clr,
            fill_opacity=0.1
        ).add_to(RacialDiversity)

    Extirpation = folium.FeatureGroup("Extirpation")

    for itr in range(len(df)):
        latStr = df.iloc[itr]["Final_Latitude"]
        lngStr = df.iloc[itr]["Final_Longitude"]
        site_name = df.iloc[itr]["Provider Organization Name (Legal Business Name)"]
        npi = df.iloc[itr]["ORG_NPI_NUM"]
        claims = df.iloc[itr]["Claims"]
        non_white = df.iloc[itr]["% non-white"]
        masked_non_white = df.iloc[itr]["Masked Racial Diversity"]
        extirpation = df.iloc[itr]["% treated with extirpation"]
        masked_extirpation = df.iloc[itr]["Masked Extirpation"]
        clr = "green"
        radius = (df.iloc[itr]["% treated with extirpation"])*10000
		
		# derive the circle pop up html content
        popUpStr = 'Site Name - {0}<br>NPI - {1}<br>Claims - {2}<br>%Non-white - {3}<br>%Extirpation - {4}'.format(
            site_name,
            npi,
            claims,
            masked_non_white,
            masked_extirpation)
        folium.Circle(
            location = [latStr, lngStr],
            popup = folium.Popup(popUpStr, min_width=100, max_width=700),
            radius = radius,
            color = clr,
            weight=2,
            fill=True,
            fill_color=clr,
            fill_opacity=0.1
        ).add_to(Extirpation)

    claimsLayer.add_to(map)
    RacialDiversity.add_to(map)
    Extirpation.add_to(map)
    folium.LayerControl().add_to(map)
    st_map = st_folium(map, width = 800, height = 500)

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()
    df = df[df['Claims']>=100] # Filtering for Sites > 100 claims

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df

def main():
    st.set_page_config(layout="wide")
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)

    # Load Data
    df = pd.read_csv('Sample_Data_RMap_07022023.csv')
    df[['ORG_NPI_NUM','ZIP_CODE']] = df[['ORG_NPI_NUM','ZIP_CODE']].astype(str)
    df['Claims'] = df['Claims'].astype('float')
    
    df_agg = df.groupby(["Provider Business Mailing Address State Name"])['Claims'].sum()
    df_agg = pd.DataFrame(df_agg).reset_index()
    df_agg.columns = ['Provider Business Mailing Address State Name','State_Level_Claim_Count']
    df = df.merge(df_agg, on = 'Provider Business Mailing Address State Name', how = 'left')
    
    df = filter_dataframe(df)
    # df['State_Level_Claim_Count'] = df.groupby(["Provider Business Mailing Address State Name"]).sum()

    # st.write(df.shape)
    # st.write(df.head())
    # st.write(df.columns)

    # Display Filters and Map
    st.subheader("#Claims and Facilities")
    col1, col2 = st.columns(2)
    with col1:
        display_claims(df,"Claims","#Claims")
    with col2:
        display_facility_count(df,"ORG_NPI_NUM","#Facilties")


    display_map(df)
    df2 = df.copy()
    df2.rename(columns={'Masked Racial Diversity': 'Racial Diversity','Masked Extirpation':'Extirpation'}, inplace=True)
    cols = ['ORG_NPI_NUM','Provider Organization Name (Legal Business Name)','Provider First Line Business Practice Location Address',
    'Provider Business Mailing Address City Name','Provider Business Mailing Address State Name','Claims','Racial Diversity','Extirpation']
    st.dataframe(df2[cols])

    # Display Metrics


if __name__ == "__main__":
    main()