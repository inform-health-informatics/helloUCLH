#!/usr/bin/env python
# coding: utf-8

# # UCLH live coding demonstator

# Import external code libraries to process and manage data

# In[186]:


# Data wrangling
import pandas as pd
import geopandas as gpd 
import numpy as np
import requests
import json
from datetime import datetime, timedelta

# HL7 wrangling
import hl7apy as hp
from hl7apy.parser import parse_message, parse_segment, parse_components, parse_field

# Data visualisation
import altair as alt


# ## Connect to the live database 
# This tracks patient admissions, transfers and discharges via HL7 messages at UCLH

# In[150]:


# load up database scripts and connect to db
get_ipython().run_line_magic('run', '../code/ids_demo.py')
conn = psycopg2.connect(DSN)


# Let's quickly inspect the last 100 patient registrations

# In[200]:


SQL = """
SELECT 
    messagedatetime, unid, hospitalnumber, patientlocation, messageformat 
FROM 
    tbl_ids_master 
WHERE 
    messagetype = 'ADT^A04' 
ORDER BY 
    messagedatetime DESC
LIMIT 100;"""
df = pd.read_sql(SQL, conn, index_col='messagedatetime')
df.head()


# ## Events from the last week
# Now let's bring on all registrations from the last 7 days  
# That's normally around 80k events

# In[207]:


SQL = """
SELECT 
    messagedatetime, unid, hospitalnumber, patientlocation, messageformat 
FROM 
    tbl_ids_master 
WHERE 
    messagetype = 'ADT^A04' 
    AND
    messagedatetime > CURRENT_TIMESTAMP - interval '7 days'
ORDER BY 
    messagedatetime DESC
;"""
df = pd.read_sql(SQL, conn, index_col='messagedatetime')
df.shape


# ## Focus on A&E
# And filter just the A&E events

# In[220]:


dfAE = df.patientlocation.str.split('^', expand=True)
dfAE['AandE'] = dfAE[0] == 'AEU'
dfAE['Area'] = dfAE[1] 
dfAE = dfAE[dfAE['AandE']][['Area']]
dfAE.Area.value_counts()


# # Let's visualise activity over the last 7 days

# In[304]:


grouper = dfAE.groupby([pd.Grouper(freq='1H'), 'Area'])
dfViz = grouper['Area'].count().unstack('Area').fillna(0).stack()
dfViz = pd.DataFrame({'n':dfViz}).reset_index()


# In[305]:


alt.Chart(
    dfViz[dfViz.Area.isin(['WAIT', 'MAJOR', 'RESUS'])]).mark_line().encode(
    x='messagedatetime:T',
    y=alt.Y('n:Q'),
    color='Area'
)


# ## Let's visualise activity in the UTC and GP attendances by time of day

# In[399]:


dfViz = dfAE.reset_index()
dfViz['hour'] = dfViz.messagedatetime.dt.hour
dfViz['minute'] = dfViz.messagedatetime.dt.minute
dfViz['hour'] = dfViz.hour + dfViz.minute/60


# In[586]:


alt.Chart(
    dfViz[dfViz.Area.isin(['GPAE', 'UTC'])]
).mark_bar(
    opacity=0.7,
    interpolate='step'
).encode(
    alt.X('hour:Q', 
          title='Hour of day',
          bin=alt.Bin(extent=[0,24], step=0.25)),
    alt.Y('count()', title='Registration count'),
    color='Area'
)


# # Where is this work coming from?
# Let's use the postcode information and plot this out

# In[587]:


SQL = """
SELECT 
    messagedatetime, unid, hospitalnumber, patientlocation, messageformat, hl7message
FROM 
    tbl_ids_master 
WHERE 
    messagetype = 'ADT^A04' 
    AND
    messagedatetime > CURRENT_TIMESTAMP - interval '7 days'
ORDER BY 
    messagedatetime DESC
;"""
df = pd.read_sql(SQL, conn, index_col='messagedatetime')
df.shape


# The HL7 message format is quite complicated and tricky to unpack.  
# Let's look at the **header** of just one message

# In[588]:


msg = df.hl7message[0].replace('\n', '\r')
parse_message(msg).msh.to_er7()


# Let's extract the postcodes so we can see where the patient's are coming from

# In[475]:


def extract_outcode(txt, HL7apy=False, verbose=False):
    'Using HL7 parser or simple text processing'
    if HL7apy:
        adr = parse_message(txt).pid.patient_address
        try:
            return adr.ad_5.to_er7().split()[0]
        except:
            if verbose:
                print(adr.to_er7())
    else:
        try:
            return txt.splitlines()[2].split('|')[11].split('^')[4]
        except IndexError:
            if verbose:
                print(txt.splitlines()[2])


# In[616]:


msgs = df.hl7message[:]
outcodes = msgs.apply(extract_outcode).str.split(expand=True)[0]
outcodes.value_counts().head(10)


# In[505]:





# ## Let's plot an empty map of London postcodes

# In[617]:


def gen_base(geojson):
    '''Generates baselayer of DC ANC map'''
    base = alt.Chart(alt.Data(values=geojson)).mark_geoshape(
        stroke='black',
        strokeWidth=1
    ).encode(
    ).properties(
        width=400,
        height=400
    )
    return base

with open('../data/imported/london_postcodes.json') as json_data:
    london_json = json.load(json_data)
base_layer = gen_base(geojson=london_json)
base_layer


# In[604]:


# Convert GeoJSON to Geopandas Dataframe 
gdf = gpd.GeoDataFrame.from_features((london_json))
# determine centroids of each polygon
gdf['centroid_lon'] = gdf['geometry'].centroid.x
gdf['centroid_lat'] = gdf['geometry'].centroid.y


# In[592]:



def last_hours(ser, n):
    'return the last M hours of a pd.Series indexed by a timestamp'
    hourM = datetime.now() - timedelta(hours=n)    
    return ser.truncate(after=hourM)

def append_recent_registrations(df_base, ser, n):
    col_label = 'last_' + str(n)
    return df_base.merge(pd.DataFrame({col_label:last_hours(ser, n).value_counts()}), 
                how='left', left_on='Name', right_index=True)


# In[619]:


# Recent IP admissions to UCLH
outcodes_adt01 = pd.read_csv('../data/adt_pcodes.csv', header=None, names=['id', 'postcode'])
outcodes_adt01 = outcodes_adt01['postcode'].str.split(expand=True)[0]
outcodes_adt01 = outcodes_adt01.rename('outcode', inplace=True)
outcodes_adt01 = pd.DataFrame(outcodes_adt01.value_counts()).reset_index().rename(columns={'index':'Name', 'outcode':'last_all'})


# In[622]:


# Now join the UCLH inpatient admssion postcode counts
dfViz = gdf.merge(outcodes_adt01, how='left', left_on='Name', right_on='Name')

# Now join most recent registrations
dfViz = append_recent_registrations(dfViz, outcodes, 24)
dfViz = append_recent_registrations(dfViz, outcodes, 6)
dfViz = append_recent_registrations(dfViz, outcodes, 3)
dfViz.head()


# In[609]:


choro_json = json.loads(dfViz.to_json())
choro_data = alt.Data(values=choro_json['features'])


# In[666]:


# Draw plot
# TODO: fix, need to repeat title by column 
viz = alt.Chart(choro_data).mark_geoshape(
    stroke='black',
    strokeWidth=1
).encode(
    alt.Color(alt.repeat('column'), type='quantitative', scale=alt.Scale(scheme='bluegreen')),
).properties(
    width=400,
    height=400
).repeat(
    column=['properties.last_24', 'properties.last_6', 'properties.last_3']
).configure_title('middle')
viz


# In[ ]:




