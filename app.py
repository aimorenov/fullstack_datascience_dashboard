import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import os 

# page title and config
st.set_page_config(page_title="getaround dashboard", page_icon=":blue_car:", layout="wide")

# State current dir, necessary for Heroku app deployment
curren_dir = os.getcwd()



# --- App ---
st.title("Getaround delay analysis dashborad :blue_car: :red_car: :minibus: :alarm_clock: :bar_chart:")

st.markdown("""
   This dashboard has been built to analyse late car rental returns at checkout and how we can best solve this.   
    
    The dataset comes from getaround and contains information regarding unique rentals, delay at checkout, time lapse between two successive rentals etc.  
   Rentals can be done either through a mobile app or via connect, a feature which enables the user to open the car with his smartphone
   

   **Specific goals** :dart:  
   Define a new feature of minimum delay between rentals and investigate:  
   - Which share of our owner’s revenue would potentially be affected by the feature?  
   - How many rentals would be affected by the feature depending on the threshold and scope (mobile vs connect) we choose?  
   - How often are drivers late for the next check-in? How does it impact the next driver?  
   - How many problematic cases will it solve depending on the chosen threshold and scope?
""")
st.markdown("---")

# --- Sidebar ---

st.sidebar.image(os.path.join(curren_dir,"getaround_logo.png"), use_column_width=True)
e = st.sidebar.empty()
e.write("")
st.sidebar.write("Dashboard made by Aura Moreno Vega :computer: [github here](https://github.com/aimorenov/fullstack_datascience/tree/master/05-Getaround_app_deployment/dashboard)")



# ---  Load data --- 
def load_data():
    filename = os.path.join(curren_dir,'data/processed/get_around_delay_analysis.csv')
    df = pd.read_csv(filename)
    return df



st.subheader("Getaround data")
st.markdown("""
    Using the original getaround data, I created new columns to calculate if a let checkout of a previous rental could impact the state (cancelled or not) of a new rental:  
    - `previous_ended_rental_late`  - was the previous rental late at checkout?  
    - `previous_ended_rental_checkout_delay` - time delay of previous rental at checkout  (mins)  
    - `delta_checkin_previous_rental` - what is the time difference between actual checkout  of previous rental and new rental    
    - `delta_checkin_previous_rental_problematic_bool` - is delay of previous rental problematic with time of new checkin?  
    - `succesive_rental` - are rentals successive?  
""")

data_load_state = st.text('Loading data...')
df = load_data()
data_load_state.text("") # change text from "Loading data..." to "" once the the load_data function has run

## Run the below code if the check is checked 
if st.checkbox('Show my processing of the original data'):
    st.subheader('My processed data')
    st.write(df)  


# --- PLOTS ---

# --- Figure 1 --- Total number of rentals being late 

st.subheader("Number of total rental checkins that are late")

# Optional counts table to display
dfg = df.groupby(['checkin_late']).size().reset_index(name='counts')
dfg['proportion_of_total_rentals'] = dfg.counts / sum(dfg.counts)

total_rentals = sum(dfg.counts)

# Plot 
fig1 = px.bar(dfg, x="checkin_late", y ='proportion_of_total_rentals', 
title=" Fig1. Check-in late status of all rentals (n ={} rentals)".format(sum(dfg.counts)))

st.plotly_chart(fig1, use_container_width=True)

st.markdown("""
    *notapplicable* refers to cases where there was no previous rental or the delay with previous rental was higher than 12 hours 
    #### Fig1 conclusions  
    Forty-four percent of all rental checkouts are late
""")

## Show optional counts table if check is checked 
if st.checkbox('Show counts table for Fig 1 rentals'):
    st.subheader('Number of rental checkins that are late')
    st.write(dfg) 

st.markdown("***")

# --- Figure 2 --- Total number of rentals being late per checkin type

st.subheader("Number of total rental checkins that are late per checkin type")

# Optional counts table to display
dfg = df.groupby(['checkin_type','checkin_late']).size().reset_index(name='counts')


tot_rentals_mobile = df.checkin_type.value_counts()['mobile']
tot_rentals_connect = df.checkin_type.value_counts()['connect']

# Plot 
fig2 = px.histogram(df, x="checkin_type", barmode='group',barnorm='percent', color="checkin_late",color_discrete_sequence=px.colors.qualitative.D3,
title="Fig2.Check-in late status of all rentals (n ={} mobile rentals; n = {} connect rentals)".format(tot_rentals_mobile, tot_rentals_connect))
st.plotly_chart(fig2, use_container_width=True)

st.markdown("""
    #### Fig2 conclusions
    The mobile check-in option is by far the most used, compared to connect  
    The proportion of late cases vs non-late cases is greater for the mobile checki-in option, compared to connect (46% vs 34% respectively)

""")

## Show optional counts table if check is checked 
if st.checkbox('Show counts table for Fig 2 rentals'):
    st.subheader('Number of rental checkins that are late per checkin type')
    st.write(dfg)

st.markdown("***")

# --- Figure 3 --- Proportion of succesive rentals

successive_rentals = df.succesive_rental.value_counts()['yes']

st.subheader("Proportion of successive rentals per checkin type")
st.subheader(f"There are {successive_rentals} successive rentals in total, representing {round(successive_rentals/total_rentals,2)}% of total rentals")

# Optional counts table to display
dfg = df.groupby(['checkin_type', 'succesive_rental']).size().reset_index(name='counts')

suc_rentals_mob = dfg.counts[(dfg.succesive_rental=='yes') & (dfg.checkin_type=="mobile")].values[0]
suc_rentals_conn = dfg.counts[ (dfg.succesive_rental=='yes') & (dfg.checkin_type=="connect")].values[0]

fig3 = px.histogram(df, x="checkin_type", barmode='group',barnorm='percent', color="succesive_rental",color_discrete_sequence=px.colors.qualitative.Safe,
title= f'Fig3.Successive rentals proportion (n= {suc_rentals_mob} and {suc_rentals_conn} successive rentals for mobile and connect respectively)')
st.plotly_chart(fig3, use_container_width=True)

st.markdown("""
    #### Fig3 conclusions
    Successive rentals represent a greater proportion of total connect rentals compared to the mobile option (19% vs 6% respectively) 
    

""")

## Show optional counts table if check is checked 
if st.checkbox('Show counts table for Fig 3 successive rentals'):
    st.subheader('Number of rental checkins that are late per checkin type')
    st.write(dfg)

st.markdown("***")



# --- Figure 4 --- Distribution of delay at checkout
st.subheader("Distribution of delay time at checkout")

# Quantile distribution of delay
delay_quantile = df['delay_at_checkout_in_minutes'].quantile((0,0.25,0.5,0.75,1))
# Count how many checkouts have a delay that is more than 12 hours (meaning that despite what is said in the documentation, some delays where computed)
mask_12hrs = df['delay_at_checkout_in_minutes'] >= (12*60)
delays_12hrs = sum(mask_12hrs)


# Optional table to display
df_quant =df['delay_at_checkout_in_minutes'].describe()

fig4 = px.histogram(df, x="delay_at_checkout_in_minutes", nbins=200, marginal="box", title='Fig4.Distribution of delay at checkout',
labels={'delay_at_checkout_in_minutes': 'Delay at chekout (mins)'})
st.plotly_chart(fig4, use_container_width=True)

st.markdown("""
    #### Fig4 conclusions  
""")
st.text('Fifty percent of rentals have a delay of checkout time between {} and {} minutes'.format(
    delay_quantile.loc[0.25],delay_quantile.loc[0.75])
    )
st.text('Although in the documentation it was stated that only delays under 12hours were reported, this is not the case:')    
st.text(f'There are {delays_12hrs} cases where there is a late checkout delay of more than 12 hours')

# Optional zoom in distribution figure
df_filt = df.copy()
delay_hours = 4
filter_mask = abs(df_filt['delay_at_checkout_in_minutes']) <= delay_hours*60
df_filt = df_filt[filter_mask]

fig4a = px.histogram(df_filt, x="delay_at_checkout_in_minutes", marginal="box",
nbins=200, title=f'Fig4a.Distribution of delay at checkout (max {delay_hours}hrs early or late)', 
labels={'delay_at_checkout_in_minutes': 'Delay at chekout (mins)'})


# Optional distribution of late checkouts only
df_filt = df.copy()
delay_hours = 4
filter_mask = abs(df_filt['delay_at_checkout_in_minutes']) <= delay_hours*60
filter_mask2 = df_filt['checkin_late'] == 'late'
df_filt = df_filt[filter_mask & filter_mask2]

delay_quantile_late = df_filt['delay_at_checkout_in_minutes'].quantile((0,0.25,0.5,0.75,1))

fig4c = px.histogram(df_filt, x="delay_at_checkout_in_minutes", marginal="box",
nbins=200, title=f'Fig4c.Distribution of delay at checkout when late (max {delay_hours}hrs late)', 
labels={'delay_at_checkout_in_minutes': 'Delay at chekout (mins)'

})


## Show optional quantile distribution table if check is checked 
if st.checkbox('Show quantile distribution table for Fig 4 delay between two rentals'):
    st.subheader('Distribution of delay time at checkout')
    st.write(df_quant)

st.text("")

if st.checkbox('Zoom into Fig4 distribution: 4hrs max absolute'):
    st.subheader('Distribution of delay time at checkout (max 4hrs absolute)')
    st.plotly_chart(fig4a, use_container_width=True)

st.text("")

if st.checkbox('Distribution of delay for late checkouts only: max 4 hrs late'):
    st.subheader('Distribution of delay time at checkout (max 4hrs late)')
    st.text('Fifty percent of late rentals have a delay of checkout time between {} and {} minutes'.format(
    delay_quantile_late.loc[0.25],delay_quantile.loc[0.75])
    )
    st.plotly_chart(fig4c, use_container_width=True)

st.markdown("***")



# --- Figure 5 --- Rental state based on delay at checkout: ended vs rental
st.subheader("Rental state based on delay at checkout: ended vs rental")

# Optional counts table
dfg = df.groupby(['previous_ended_rental_late', 'checkin_type', 'state']).size().reset_index(name='counts')


# Plot
fig5 = px.histogram(df, x="previous_ended_rental_late", facet_col="checkin_type",barmode='group',barnorm='percent', color="state",
title="Fig5.Cancelled and ended status for different delay categories: proportions")
st.plotly_chart(fig5, use_container_width=True)

st.markdown("""
    #### Fig5 conclusions
    Overall, late checkouts do not result in a cancelled rental:  
     - 9% of late mobile checkin rentals are cancelled due to a late previous rental checkout  
     - 19% of late connect checkin rentals are cancelled due to a late previous rental checkout 
    Interestingly, despite an early arrival checkout, there are: 
     - 9% and 14% of mobile and connect rentals that are cancelled, respectively
    For *notapplicable* cases where there are either no successive rentals or rentals more than 12hrs appart, there is an important proportion of cancelled rentals for the connect checkin option

""")

# Optional counts plot
dfg = df.groupby(['previous_ended_rental_late', 'checkin_type', 'state']).size().reset_index(name='counts')

fig5a = px.histogram(df, x="previous_ended_rental_late", facet_col="checkin_type",barmode='group', color="state",
title="Fig5a.Cancelled and ended status for different delay categories")


## Show optional counts table if check is checked 
if st.checkbox('Show counts table for Fig 5 rental state based on delay at checkout'):
    st.subheader('Number of rentals that are ended or cancelled based on previous checkout delay: mobile vs connect')
    st.write(dfg)

st.text("")

if st.checkbox('Counts barplot for Figure5'):
    st.subheader('Number of rentals that are ended or cancelled based on previous checkout delay: mobile vs connect')
    st.plotly_chart(fig5a, use_container_width=True)

st.markdown("***")

# --- Figure 6 --- Identifying a minimum delay between rentals threshold
st.subheader("Identifying a minimum delay between rentals threshold")

# Filter dataframe for max 4hr delta
df_filt = df.copy()
delay_hours = 4
filter_mask = abs(df_filt['delta_checkin_previous_rental']) <= delay_hours*60
filter_mask2 = df_filt.succesive_rental=="yes"
df_filt = df_filt[filter_mask & filter_mask2]

# Plot
fig6 = px.box(df_filt, x="state", y="delta_checkin_previous_rental", 
boxmode='group', points='all', facet_col ="checkin_type", 
                labels={
                    "parameter": "Rental status",
                    "delta_checkin_previous_rental": "Delta between checkout and new checkin (mins)",
                    "delta_checkin_previous_rental_problematic": "Time delta category"
                },
                title=f'Fig6.Delta of time between succesive rental and delay of checkout (max {delay_hours} hours displayed)')

st.plotly_chart(fig6, use_container_width=True)

# Plot option 2
# Categorize delta of previous rental checkin delay and time between next rental. Use bins
bins = [-np.inf,0, 10, 30, 60, np.inf]
labs = ['problematic' ,'[0-10 mins]', '[10-30 mins]', '[30-60 mins]', '[>60mins]']
df['delta_checkin_previous_rental_problematic'] = pd.cut(df['delta_checkin_previous_rental'], bins = bins, labels=labs)


dfg = df.groupby(['state','delta_checkin_previous_rental_problematic']).size().reset_index(name='counts')


df_filt = df.copy()
filter_mask = df_filt.succesive_rental=="yes"
df_filt = df_filt[filter_mask]
df_filt.dropna(subset=['delta_checkin_previous_rental_problematic'], inplace=True)

fig6b = px.histogram(df_filt, x="state", barmode='group',barnorm='percent', color="delta_checkin_previous_rental_problematic",color_discrete_sequence=px.colors.qualitative.D3,
title='Fig6b.Categories of time delta between checkout and new checkin for successive rentals: state of new rental', 
labels={
   'delta_checkin_previous_rental_problematic': 'Delta checkout vs new checkin category' 
})
st.plotly_chart(fig6b, use_container_width=True)
st.text("problematic cases are cases where delay of previous rental checkout overlaps checkin time of new rental")

st.markdown("""
    #### Fig6 conclusions
    There are 12% of problematic rentals which still had place (ended) vs 18% of problematic rentals which were cancelled due to the new checkin rental having to wait due to late checkout
    Cancelled rentals: Successive rentals that are late for connect checkins have a greater delay compared to mobile  
    Delta of time between actual checkout and new checkout between succesive rentals which are cancelled is a lot more disperse than ended rentals
""")

st.markdown("***")
st.markdown("***")

# --- Evaluate threshold ---
st.subheader("Evaluate threshold of a minimum time delta between rentals: impact on solving problematic cases and on ended cases")

st.markdown("""
    ### Test threshold values for the minimum time delta to have between successive rentals so that the car in question can appear for rental on app:  
     - Evaluate how many previously problematic cases are solved under the new minimum delay feature  
     - Evaluate how many rentals that would've had place are negative impacted. i.e. they become problematic because the time between successive rentals is < minimum rental time  
""")

# Selection form
with st.form("threshold_testing"):
    threshold = st.number_input("Minimum time delta to have between successive rentals (mins)", min_value = 0, step = 1)
    button_sent = st.form_submit_button("Submit chosen threshold")

    if button_sent:
        
        
        # Dataframe for plotting: Prepare new colums from threshold
        df_new = df.copy()

        df_new['new_delta_checkin_previous_rental'] = threshold - df_new.previous_ended_rental_checkout_delay
        df_new['new_thresh_problematic_case'] = ['no' if delay<0 else 'yes' for delay in df_new.new_delta_checkin_previous_rental.tolist()]

        # Cases which also become problematic: those that have a lower time delta between checkin and chekout than new threshold
        new_thres_problematic = (df_new['time_delta_with_previous_rental_in_minutes'] < threshold)
        df_new.loc[new_thres_problematic, 'new_thresh_problematic_case'] = 'yes'


        # Count number of problematic cases before and after new threshold
        df_new_filt = df_new.copy()
        filter_mask = df_new_filt.succesive_rental=="yes"
        df_new_filt = df_new_filt[filter_mask]

        # Optional count table
        dfg = df_new_filt.delta_checkin_previous_rental_problematic_bool.value_counts()
        
        problematic_cases = df_new_filt.delta_checkin_previous_rental_problematic_bool.value_counts()['yes']

        dfg_new = df_new_filt.groupby(['delta_checkin_previous_rental_problematic_bool','new_thresh_problematic_case' ]).size().reset_index(name='counts')
        
        prev_problematic_cases_solved = dfg_new.loc[(dfg_new.delta_checkin_previous_rental_problematic_bool=='yes') & (dfg_new.new_thresh_problematic_case=="no"), 'counts'].tolist()[0]

        impacted_ended_rentals_now_problematic = dfg_new.loc[(dfg_new.delta_checkin_previous_rental_problematic_bool=='no') & (dfg_new.new_thresh_problematic_case=="yes"), 'counts'].tolist()[0]

        # Count per checkin type
        dfg_new_scope = df_new_filt.groupby(['checkin_type', 'delta_checkin_previous_rental_problematic_bool','new_thresh_problematic_case' ]).size().reset_index(name='counts')


        mask_connect = (dfg_new_scope.checkin_type=="connect") & (dfg_new_scope.delta_checkin_previous_rental_problematic_bool=='yes') & (dfg_new_scope.new_thresh_problematic_case=="no")
        mask_mobile =  (dfg_new_scope.checkin_type=="mobile") & (dfg_new_scope.delta_checkin_previous_rental_problematic_bool=='yes') & (dfg_new_scope.new_thresh_problematic_case=="no")

        mask_connect_2 = (dfg_new_scope.checkin_type=="connect") & (dfg_new_scope.delta_checkin_previous_rental_problematic_bool=='no') & (dfg_new_scope.new_thresh_problematic_case=="yes")
        mask_mobile_2 = (dfg_new_scope.checkin_type=="mobile") & (dfg_new_scope.delta_checkin_previous_rental_problematic_bool=='no') & (dfg_new_scope.new_thresh_problematic_case=="yes")


        prev_problematic_cases_solved_connect = dfg_new_scope.loc[mask_connect, 'counts'].tolist()[0]
        prev_problematic_cases_solved_mobile = dfg_new_scope.loc[mask_mobile, 'counts'].tolist()[0]


        impacted_ended_rentals_now_problematic_conn = dfg_new_scope.loc[mask_connect_2, 'counts'].tolist()[0]
        impacted_ended_rentals_now_problematic_mob = dfg_new_scope.loc[mask_mobile_2, 'counts'].tolist()[0]


        # Print result
        st.success(f'''After using a threshold of {threshold} minutes, there were {prev_problematic_cases_solved} previous problematic cases solved ({prev_problematic_cases_solved_connect} mobile and {prev_problematic_cases_solved_mobile} connect).
However, previously ended rentals which would no longer take place with new threshold are: {impacted_ended_rentals_now_problematic} ({impacted_ended_rentals_now_problematic_conn}  mobile and {impacted_ended_rentals_now_problematic_mob} connect)''')

        fig7 = go.Figure(data=[go.Sankey(
            node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = ["not problematic", "problematic", "not problematic", "problematic"],
            color = ["darkblue", 'darkred', "blue", "red"]
            ),
            link = dict(
            source = [0, 0, 1, 1], # indices correspond to labels
            target = [2, 3, 2, 3],
            value = dfg_new.counts.tolist()
        ))])

        fig7.update_layout(title_text=f"Fig7.Evolution of number of problematic cases after new minimun rental delta threshold: {threshold} mins", font_size=10)
        st.plotly_chart(fig7, use_container_width=True)




