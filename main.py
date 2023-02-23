import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objs as go

filename = "C:/Users/User/Desktop/datasets/netflix_titles.csv"
data = pd.read_csv(filename)
print(data.head())

# Data Cleaning

print(data.info())
print(data.isna().sum())
print(data['rating'].unique())
print(data[data['rating'].isna()])

replace_rating = {211: 'TV-14', 2411: 'TV-14', 3288: 'PG-13', 4056: 'TV-G', 4402: 'TV-G', 4403: 'TV-G',
                  4706: 'TV-14', 5015: 'TV-14', 5234: 'TV-14', 6231: 'TV-Y'}
for id, rate in replace_rating.items():
    data.iloc[id, 8] = rate

print(data['rating'].isna().sum())
data = data.drop(['director', 'cast'], axis=1)
print(data.columns)
print(data.isna().sum())
print(data[data['date_added'].isna()])
data = data[data['date_added'].notna()]
data['country'] = data['country'].fillna(data['country'].mode()[0])
data = data[data['duration'].notna()]
print(data.isna().sum())
data['years'] = data['date_added'].apply(lambda x: x.split(" ")[-1])
data['years'] = pd.to_numeric(data['years'])
print(data['years'].head())
print(data['rating'].unique())
ratings_in_age = {
    'TV-PG': 'Older Kids', 'TV-MA': 'Adults', 'TV-Y7-FV': 'Older Kids', 'TV-Y7': 'Older Kids', 'TV-14': 'Teens',
    'R': 'Adults', 'TV-Y': 'Kids', 'NR': 'Adults', 'PG-13': 'Teens', 'TV-G': 'Kids', 'PG': 'Older Kids',
    'G': 'Kids', 'UR': 'Adults', 'NC-17': 'Adults'}
data['target_groups'] = data['rating'].replace(ratings_in_age)
print(data['target_groups'].unique())

data['country_name'] = data['country'].apply(lambda x: x.split(",")[0])
print(data['country_name'].head())

data['genre'] = data['listed_in'].apply(lambda x: x.replace(' ,', ',').replace(', ', ',').split(','))
print(data['genre'].head())

data['target_groups'] = pd.Categorical(data['target_groups'], categories=['Kids', 'Older Kids', 'Teens', 'Adults'])

# Data Analysis, Visualization

# Tv Show and Movies
figure = px.pie(data['type'].value_counts().reset_index(), names='index', values='type',
                color_discrete_sequence=px.colors.sequential.Aggrnyl)
figure.update_traces(textposition='inside', textinfo='percent+label')
figure.show()


# Ratings By Type Of Content
grouped_movies = data[data['type'] == 'Movie']
grouped_show = data[data['type'] == 'TV Show']


def generate_rating(info):
    rating_df = info.groupby(['rating', 'target_groups']).agg({'show_id': 'count'}).reset_index()
    rating_df = rating_df[rating_df['show_id'] != 0]
    rating_df.columns = ['rating', 'target_groups', 'counts']
    rating_df = rating_df.sort_values('target_groups')
    return rating_df


movie_ratings = generate_rating(grouped_movies)
show_ratings = generate_rating(grouped_show)

figure = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]])
figure.add_trace(go.Pie(labels=movie_ratings['target_groups'], values=movie_ratings['counts']), row=1, col=1)
figure.add_trace(go.Pie(labels=movie_ratings['target_groups'], values=show_ratings['counts']), row=1, col=2)
figure.show()

# Countries by Users in Percents

country_dataframe = data['country_name'].value_counts().reset_index()
country_dataframe = country_dataframe[
    country_dataframe['country_name'] / country_dataframe['country_name'].sum() > 0.01]
figure = px.pie(country_dataframe, values='country_name', names='index')
figure.update_traces(textposition='inside', textinfo='percent+label')
figure.show()

# Trends in Time

year_released_dataframe = data.loc[data['release_year'] > 2012].groupby(['release_year', 'type']). \
    agg({'show_id': 'count'}).reset_index()
year_updated_dataframe = data.loc[data['years'] > 2012].groupby(['years', 'type']).agg({'show_id': 'count'}). \
    reset_index()

figure = go.Figure()


figure.add_trace(go.Scatter(
    x=year_released_dataframe.loc[year_released_dataframe['type'] == 'Movie']['release_year'],
    y=year_released_dataframe.loc[year_released_dataframe['type'] == 'Movie']['show_id'], mode='lines+markers',
    name='Release Year Of Movie'))

figure.add_trace(go.Scatter(
    x=year_released_dataframe.loc[year_released_dataframe['type'] == 'TV Show']['release_year'],
    y=year_released_dataframe.loc[year_released_dataframe['type'] == 'TV Show']['show_id'],
    mode='lines+markers', name='Release Year Of TV Show'))

figure.add_trace(go.Scatter(
    x=year_updated_dataframe.loc[year_updated_dataframe['type'] == 'Movie']['years'],
    y=year_updated_dataframe.loc[year_updated_dataframe['type'] == 'Movie']['show_id'],
    mode='lines+markers', name='Added Year Of Movie'))

figure.add_trace(go.Scatter(
    x=year_updated_dataframe.loc[year_updated_dataframe['type'] == 'TV Show']['years'],
    y=year_updated_dataframe.loc[year_updated_dataframe['type'] == 'TV Show']['show_id'],
    mode='lines+markers', name='Added Year Of TV Show'))
figure.update_xaxes(categoryorder='total descending')
figure.show()

# TV Show Duration

tvshow_dataframe = data.loc[data['type'] == 'TV Show']
tvshow_dataframe['duration'] = tvshow_dataframe['duration'].str.replace(' Seasons', ' Season')
tvshow_dataframe['duration'] = tvshow_dataframe['duration'].str.replace(' Season', ' Season(s)')

show_duration = pd.DataFrame(data=tvshow_dataframe.groupby('duration').size().reset_index())
show_duration.rename(columns={0: 'Number of TV Show'}, inplace=True)

figure = px.pie(show_duration, values='Number of TV Show', names='duration',
                color_discrete_sequence=px.colors.sequential.RdBu, title='TV Show Duration')

figure.update_traces(textposition='inside', textinfo='percent+label')
figure.show()