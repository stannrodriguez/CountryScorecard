import streamlit as st
import pandas as pd
import numpy as np
import quandl
import plotly.express as px
import os

st.title('Worldwide Governance')
	
def config():
	quandl.ApiConfig.api_key = 'cFbXcEt2Ggzhdpv_ZCdE'

config()	

def load_metadata():
	metadata = pd.read_csv('metadata.csv')
	metadata['metric'] = [name.split('; ')[0] for name in metadata.name]
	metadata['statistic'] = [name.split('; ')[1].split(' - ')[0] for name in metadata.name]
	metadata['country'] = [name.split(' - ')[1] for name in metadata.name]
	metadata = metadata[['code','metric','statistic','country']]
	metadata = metadata[metadata.country.isin(set(metadata.country))]

	global code_mapping
	metrics =['Control of Corruption','Government Effectiveness',
	 'Political Stability and Absence of Violence/Terrorism', 'Regulatory Quality',
	 'Rule of Law', 'Voice and Accountability']
	codes = ['CC', 'GE', 'PV', 'RQ', 'RL', 'VA']
	code_mapping = dict(zip(metrics, codes))

	return metadata

metadata = load_metadata()

# countries = list(set(metadata.country))
# metric = list(set(metadata.metric))
# selected_country = st.selectbox('Please select a country', countries)
# selected_metric = st.selectbox('Please select a metric', metric)


def load_data(metadata=metadata):
	if os.path.exists('master_data.csv'):
		master_data = pd.read_csv('master_data.csv')
	else:
		metadata = metadata[metadata.statistic.isin(['Estimate', 'Percentile Rank'])]
		master_data = pd.DataFrame()

		st.header(country_option)
		for index, row in metadata.iterrows():
			country_data = quandl.get('WWGI/' + row.code)
			country_data['Metric'] = row.metric
			country_data['Country'] = row.country
			country_data['Statistic'] = row.statistic

			master_data = master_data.append(country_data)

		master_data.reset_index(inplace=True)
		master_data.to_csv('master_data.csv', index=False)

	return master_data

master_data = load_data()

def chart_data():
	countries = list(set(metadata.country))
	metric = list(set(metadata.metric))
	selected_country = st.selectbox('Please select a country', countries)
	selected_metric = st.selectbox('Please select a metric', metric)

	ranked_countries = master_data[(master_data.Date == max(master_data.Date)) &
								(master_data.Statistic == 'Percentile Rank') &
								(((master_data.Value <= 5) | (master_data.Value >= 95)) |
								 (master_data.Country == selected_country))]

	filtered_data = master_data[((master_data.Country == selected_country) |
								(master_data.Country.isin(ranked_countries.Country))) &
								(master_data.Metric == selected_metric) &
								(master_data.Date == max(master_data.Date)) &
								(master_data.Statistic == 'Estimate') ] 
	filtered_data = filtered_data.sort_values('Value')
	fig = px.scatter(filtered_data, x='Value', y='Country')

	selected_country_data = filtered_data[master_data.Country == selected_country]
	info = f'Estimate of {selected_country_data.Metric.values[0]} for {selected_country_data.Country.values[0]}: {selected_country_data.Value.values[0].round(2)}'

	info2 = f'Percentile Ranking: {ranked_countries.loc[(ranked_countries.Country == selected_country) & (ranked_countries.Metric == selected_metric), "Value"].values[0].round(2)}'
	st.header(info)
	st.subheader(info2)
	st.plotly_chart(fig)

	return filtered_data

filtered_data = chart_data()


if st.checkbox('Show Data Preview'):
    st.subheader('Raw data')
    st.write(filtered_data.head())
