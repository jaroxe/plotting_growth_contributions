from bokeh.plotting import figure, output_file, show
from bokeh.io import output_notebook, show
from bokeh.models.tickers import FixedTicker
from bokeh.models import NumeralTickFormatter, Legend
import pandas as pd
import numpy as np
import bokeh.palettes


def extract_dfs(df):
	"""
	df: A pandas dataframe where:
		- The index (rows) contains years or other temporal period
		- The columns represent categories, countries etc
		- If the rows are years and the columns are countries (for example)
			then an entry in the dataframe represents whichever quantity is
			being measured (e.g. GDP) for that country and year.
		(For more details view the example.ipynb)
	returns:
		- Dataframe with total interannual percentage growth
		- Datframe with contributions to growth of each original column
	"""
	dff = df.copy()
	categories = list(dff.columns)
	dff['total'] = dff.sum(axis=1)
	dff['pctg_growth_total'] = (dff['total'] - dff['total'].shift(1)) / dff['total'].shift(1)
	for cat in categories:
	    dff[f'pctg_growth_{cat}'] = (dff[cat] - df[cat].shift(1)) / dff[cat].shift(1)
	for cat in categories:
	    dff[f'contrib_{cat}'] = dff[f'pctg_growth_{cat}']*(dff[cat].shift(1)) / dff['total'].shift(1)
	growth_df = dff[['pctg_growth_total']]
	growth_df.columns = ['total']

	contrib_df = dff[[f'contrib_{cat}' for cat in categories]]
	contrib_df.columns = categories
	return growth_df.iloc[1:], contrib_df.iloc[1:]


def plot_growth(df, period='year', bar_width=0.5):
	"""
	df: A pandas dataframe (typically the first output of extract_dfs)
	period: string, the periodicity of the data
	bar_width: float, width of the bars in the plot

	The function plots the overall percentage interannual growth
	"""

	# output to static HTML file
	output_file(f'{period}_growth.html')

	# create a new plot
	p = figure(tools='pan,box_zoom,reset,save',
	           title=f'{period} to {period} growth (total)'.capitalize(),
	           x_axis_label=f'{period}'.capitalize())

	p.vbar(df.index, top=df['total'], width=bar_width)
	p.yaxis[0].formatter = NumeralTickFormatter(format="0%")
	p.xaxis.ticker = FixedTicker(ticks=list(df.index))
	show(p)


def tops_bottoms(df):
	"""
	df: A pandas dataframe (typically the second output of extract_dfs)
	
	Using the input dataframe, the function returns two dataframes that
	contain the bottom and top limits of bar segments in a stacked bar chart
	"""
	dfa = np.array(df)
	tops = np.zeros(dfa.shape)
	bots = np.zeros(dfa.shape)

	for i in range(tops.shape[0]):
	    neg = 0
	    pos = 0
	    for j in range(tops.shape[1]):
	        if dfa[i, j] >= 0:
	            bots[i, j] = pos 
	            pos += dfa[i, j]
	            tops[i, j] = pos
	        else:
	            tops[i, j] = neg
	            neg += dfa[i, j]
	            bots[i, j] = neg
	tops_df = pd.DataFrame(tops)
	tops_df.columns = df.columns
	tops_df.index = df.index
	bots_df = pd.DataFrame(bots)
	bots_df.columns = df.columns
	bots_df.index = df.index
	return tops_df, bots_df


def plot_contrib(df, palette='Colorblind', period='year', bar_width=0.5, legend_loc='top_right'):
	"""
	df: A pandas dataframe (typically the second output of extract_dfs)
	palette: string, the name of a bokeh color palette to be applied to the plot
	period: string, the periodicity of the data
	bar_width: float, width of the bars in the plot
	legend_loc: string, location of the legend in the plot e.g: 'bottom_left'

	The function plots the contributions of each column to the overall
	interannual growth
	"""
	categories = list(df.columns)
	colors = eval(f'bokeh.palettes.{palette}')[len(categories)]
	tops, bottoms = tops_bottoms(df)

	# output to static HTML file
	output_file(f'Growth_contribs.html')

	# create a new plot
	p = figure(tools='pan,box_zoom,reset,save',
	           title='Contributions to total growth',
	           x_axis_label=f'{period}'.capitalize())

	for i in range(len(categories)):
	    p.vbar(df.index, bar_width, bottom=bottoms[categories[i]], top=tops[categories[i]],
	          color=colors[i], legend=categories[i])
	p.yaxis[0].formatter = NumeralTickFormatter(format="0%")
	p.xaxis.ticker = FixedTicker(ticks=list(df.index))
	p.legend.location = legend_loc
	show(p)


def plot_contributions(df, palette='Colorblind', period='year', bar_width=0.5,
	legend_loc='top_right', total_growth=True):
	"""
	df: A pandas dataframe with the appropriate format (see example.ipynb)
	palette: string, the name of a bokeh color palette to be applied to the plot
	period: string, the periodicity of the data
	bar_width: float, width of the bars in the plot
	legend_loc: string, location of the legend in the plot e.g: 'bottom_left'
	total_growth: bool, whether to plot total period to period growth

	This function plots:
		- Percentage total period to period growth (optional)
		- Contributions to growth of each column in the dataframe
	"""
	growth, contribs = extract_dfs(df)
	if total_growth:
		plot_growth(growth, period=period, bar_width=bar_width)
	plot_contrib(contribs, palette=palette, period=period, bar_width=bar_width, legend_loc=legend_loc)
