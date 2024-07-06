from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import dash_table
import plotly.io as pio
pio.templates
pio.templates.default = 'plotly_dark'


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Import dataset
df = pd.read_csv('GlobalWeather.csv') 

# Konversi kolom 'last_updated' ke datetime
df['last_updated'] = pd.to_datetime(df['last_updated'])


pollutants = [
    'air_quality_Carbon_Monoxide', 'air_quality_Ozone', 'air_quality_Nitrogen_dioxide',
    'air_quality_Sulphur_dioxide', 'air_quality_PM2.5', 'air_quality_PM10'
]

app.layout = html.Div([
    html.Div([
        html.H1('Global Weather Dashboard')
    ], style={
        'font-family': 'poppins',
        'font-size': '30',
        'text-align': 'center',  
        'padding': '10px', 
        'backgroundColor': '#111', 
        'borderRadius': '5px',
        'color': '#fff'}),

    html.Div([
        html.Div([
            dcc.Dropdown(
                df['condition_text'].unique(),
                df['condition_text'].unique()[0],
                id='crossfilter-xaxis-column',
            )
        ], style={
                'width': '50%', 
                'margin': '10px',
                'padding': '10px',
                'fontSize': '16px',
                'backgroundColor': '#111',
                'color': '#111',
                'border': '1px solid #ccc', 
                'borderRadius': '5px', 
                'boxShadow': '2px 2px 12px rgba(0, 0, 0, 0.1)'}),
    ],
    style={'display': 'flex',
           'justifyContent': 'center',  
           'alignItems': 'center', 
           'textAlign': 'center',
           'background-color': '#111'}),

    html.Div([
        dcc.Graph(
            id='geo-map',
        )
    ], style={'width': '65%', 'display': 'inline-block', 'padding': '0 20'}),

    html.Div([
    html.H3('History Temparature', style={
        'color': '#fff',  
        'padding': '5px',  
        'backgroundColor': '#333',  
        'textAlign': 'center',  
        'borderRadius': '5px' 
    }),  
    dash_table.DataTable(
            id='temperature-table',
        columns=[
            {'name': 'Last Updated', 'id': 'last_updated'},
            {'name': 'Temperature (Celsius)', 'id': 'temperature_celsius'},
            {'name': 'Temperature (Fahrenheit)', 'id': 'temperature_fahrenheit'}
        ],
        data = [],
        style_table={
            'maxHeight': '400px', 
            'overflowY': 'auto',
            'borderRadius': '5px',  
            'padding': '10px',
            'backgroundColor': '#2b2b2b',
            },
        style_cell={
            'textAlign': 'left',
            'padding': '10px',  
            'color': '#fff',  
            'backgroundColor': '#333',  
            'fontFamily': 'Arial, sans-serif',  
            'fontSize': '10px' 
            },
        style_header={
            'backgroundColor': '#555', 
            'fontWeight': 'bold',
            'color': '#fff',  
            'fontSize': '11px',  
            'borderBottom': '2px solid #fff'
            }
    )
    ], style={'width': '35%', 'float': 'right', 'display': 'inline-block', 'padding': '25 25', 'backgroundColor': '#111'}),

    html.Div([
        dcc.Graph(
            id='scatter-chart',
        )
    ], style={'width': '70%', 'float': 'left', 'display': 'inline-block', 'padding': '0', 'backgroundColor': '#111'}),

    html.Div([
        dcc.Graph(
            id='bar-polar',
        )
    ], style={'width': '30%', 'float': 'right', 'display': 'inline-block', 'backgroundColor': '#111'}),

    html.Div([
        dcc.Graph(
            id='gauge-chart',
        )
    ], style={'width': '35%', 'float': 'right', 'display': 'inline-block', 'padding': '0 5px', 'backgroundColor': '#111'}),



    html.Div([
        dcc.Graph(
        id='air_quality_bar_chart'
        ),
    ],  style={'width': '65%', 'float': 'left', 'display': 'inline-block', 'padding': '0 20'})
    
],
 style={
        'backgroundColor': '#111',  
})

@callback(
    Output('geo-map', 'figure'),
    Output('scatter-chart', 'figure'),
    Output('bar-polar', 'figure'),
    Output('gauge-chart','figure'),
    Output('temperature-table', 'data'),
    Output('air_quality_bar_chart', 'figure'),
    Input('crossfilter-xaxis-column', 'value'),
    Input('geo-map', 'clickData')
)
def update_graphs(condition_text, click_data):
    # Filter the data based on the input filters
    filtered_df_geo = df[df['condition_text'] == condition_text]

    # Check if any country is selected, if not use the first country in the filtered data
    if click_data:
        country_value = click_data['points'][0]['location']
        filtered_df_scatter = df[df['ISO_alpha'] == country_value]
    else:
        filtered_df_scatter = df[df['country'] == filtered_df_geo['country'].iloc[0]]

    # Create a new geo map graph with the filtered data
    fig_geo = px.choropleth(filtered_df_geo, locations='ISO_alpha', color='condition_text', 
                            hover_name='country',
                            projection='natural earth', 
                           )
    fig_geo.update_layout(showlegend=False, title={'text': "Global Weather Conditions"})

    # Create a new scatter chart graph with the filtered data
    fig_scatter = px.line(filtered_df_scatter, 
                          x='last_updated_epoch',
                          y='temperature_celsius', 
                          color='country', 
                          markers=True,
                          title='Tren Perubahan Temperature (Celsius)'
                         )
    fig_scatter.update_layout(showlegend=False)

    # Create a new bar polar chart with the filtered data
    fig_bar_polar = px.bar_polar(filtered_df_scatter,
                                 r="wind_mph", 
                                 theta="wind_direction",
                                 color="wind_kph", 
                                 template="plotly_dark",
                                 color_discrete_sequence=px.colors.sequential.Plasma_r,
                                 title='Wind speed and Direction'
                                 )
    current_uv_index = filtered_df_scatter['uv_index'].iloc[-1] if not filtered_df_scatter.empty else 0

    # Create a new gauge chart with the filtered data
    fig_gauge_chart = go.Figure(go.Indicator(
        mode="gauge+number",
        value=current_uv_index,
        title={'text': "Current UV Index", 'font': {'size': 24, 'color': '#fff'}},
        gauge={
            'axis': {'range': [None, 11], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 5.5], 'color': 'yellow'},
                {'range': [5.5, 11], 'color': 'red'}],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': current_uv_index},
                
        }
    ))

    fig_gauge_chart.update_layout(
        font={'color': "darkblue", 'family': "Arial"},
        margin={'t': 50, 'b': 0, 'l': 0, 'r': 0}
    )

    #update table with the filtered country
    table_data = filtered_df_scatter[['last_updated', 'temperature_celsius', 'temperature_fahrenheit']].to_dict('records')

    pollutant_data = []
    for pollutant in pollutants:
        pollutant_data.append({
            'Pollutant': pollutant,
            'Concentration': filtered_df_scatter[pollutant].iloc[0]  # Mengambil nilai pertama untuk polutan tersebut
        })
    df_pollutants = pd.DataFrame(pollutant_data)

    # bar chart polusi udara
    fig_bar_chart = px.bar(df_pollutants,
                            x='Pollutant', 
                            y='Concentration', 
                            labels={'Concentration': 'Concentration (µg/m³)', 'Pollutant': 'Pollutant'},
                            title='Air Quality Data for Different Pollutants',
                            barmode='group'
                           )


    return fig_geo, fig_scatter, fig_bar_polar, fig_gauge_chart, table_data, fig_bar_chart

if __name__ == '__main__':
    app.run(debug=True)
