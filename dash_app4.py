import os
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
from flask_cors import CORS

# Load CSV data
csv_path = r"Test Try 2.csv"
df = pd.read_csv(csv_path, encoding='latin1')

# Ensure 'date' column is in datetime format
df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')

# Add an index column
df[' index'] = range(1, len(df) + 1)

# Define color mappings
feature_colors = {
    'All-Wheel Drive': '#000000',
    'Steering': '#004aad',
    'Interior Quality': '#ff914d',
    'Engine': '#5ce1e6',
    'Brake': '#ff66c4',
    'Seats': '#98FB98',
    'Transmission': '#800080',
    'Electric Motor': '#006400'
}

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server  # Expose Flask server for Gunicorn
CORS(server, resources={r"/": {"origins": ""}})

# Define dropdown button style
dropdown_button_style = {
    'width': '150px',
    'min-width': '200px',
    'max-width': '200px',
    'color': 'black',
    'backgroundColor': '#fff',
    'margin-bottom': '10px',
    'padding': '8px 10px',
    'border': 'none',
    'border-radius': '20px',
    'cursor': 'pointer',
    'textAlign': 'center',
    'fontSize': '20px'
}

# Define layout
app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='brand-dropdown',
                options=[{'label': 'Select All', 'value': 'select_all'}] +
                        [{'label': brand, 'value': brand} for brand in df['brand'].unique()],
                placeholder='Select Brand',
                style=dropdown_button_style,
                multi=True
            ),
            dcc.Dropdown(
                id='model-dropdown',
                options=[],
                placeholder='Select Model',
                style=dropdown_button_style,
                multi=True
            ),
            dcc.Dropdown(
                id='fact-dropdown',
                options=[],
                placeholder='Select Fact',
                style=dropdown_button_style,
                multi=True
            ),
            dcc.Dropdown(
                id='country-dropdown',
                options=[],
                placeholder='Select City',
                style=dropdown_button_style,
                multi=True
            ),
            dcc.Dropdown(
                id='source-dropdown',
                options=[],
                placeholder='Select Source',
                style=dropdown_button_style,
                multi=True
            ),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=df['date'].min().strftime('%Y-%m-%d'),
                end_date=df['date'].max().strftime('%Y-%m-%d'),
                display_format='DD-MM-YYYY',
                style=dropdown_button_style
            ),
        ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'flex-start', 'width': '300px', 'padding': '10px'}),

        html.Div([
            dash_table.DataTable(
                id='datatable-paging-page-count',
                columns=[{"name": i, "id": i, "type": "text"} for i in ['brand', 'model', 'feedback']],
                page_current=0,
                page_size=5,
                page_action='custom',
                style_table={'height': '450px', 'overflowY': 'auto', 'overflowX': 'auto', 'width': '100%'},
                style_header={'textAlign': 'center', 'fontSize': '20px'},
                style_cell={'textAlign': 'left', 'whiteSpace': 'normal', 'overflow': 'auto', 'textOverflow': 'ellipsis',
                            'minWidth': '50px', 'maxWidth': '180px', 'fontSize': '18px'},
                style_cell_conditional=[
                    {'if': {'column_id': 'brand'}, 'width': '10%'},
                    {'if': {'column_id': 'model'}, 'width': '10%'}
                ],
            ),
        ], style={'flex': '1', 'padding': '20px', 'overflow': 'hidden'})
    ], style={'display': 'flex', 'flexDirection': 'row'}),

    dcc.Store(id='stored-dropdown-values', storage_type='local'),
])
@app.callback(
    Output('stored-dropdown-values', 'data'),
    [Input('brand-dropdown', 'value'),
     Input('model-dropdown', 'value'),
     Input('fact-dropdown', 'value'),
     Input('country-dropdown', 'value'),
     Input('source-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def save_dropdown_values(brand, model, fact, country, source, from_date, to_date):
    return {
        'brand': brand,
        'model': model,
        'fact': fact,
        'country': country,
        'source': source,
        'from_date': from_date,
        'to_date': to_date
    }

@app.callback(
    [Output('brand-dropdown', 'value'),
     Output('model-dropdown', 'value'),
     Output('fact-dropdown', 'value'),
     Output('country-dropdown', 'value'),
     Output('source-dropdown', 'value'),
     Output('date-picker-range', 'start_date'),
     Output('date-picker-range', 'end_date')],
    [Input('stored-dropdown-values', 'data')]
)
def load_dropdown_values(stored_values):
    if stored_values is None:
        return [None] * 7
    return (
        stored_values.get('brand'),
        stored_values.get('model'),
        stored_values.get('fact'),
        stored_values.get('country'),
        stored_values.get('source'),
        stored_values.get('from_date'),
        stored_values.get('to_date')
    )

# Update model dropdown options based on selected brand(s)
@app.callback(
    Output('model-dropdown', 'options'),
    [Input('brand-dropdown', 'value')]
)
def update_model_dropdown(selected_brands):
    if not selected_brands:
        return []
    if 'select_all' in selected_brands:
        models = df['model'].unique()
    else:
        models = df[df['brand'].isin(selected_brands)]['model'].unique()
    return [{'label': 'Select All', 'value': 'select_all'}] + [{'label': model, 'value': model} for model in models]

# Update fact dropdown options based on selected model(s)
@app.callback(
    Output('fact-dropdown', 'options'),
    [Input('model-dropdown', 'value')]
)
def update_fact_dropdown(selected_models):
    if not selected_models:
        return []
    if 'select_all' in selected_models:
        facts = df['fact'].unique()
    else:
        facts = df[df['model'].isin(selected_models)]['fact'].unique()
    return [{'label': 'Select All', 'value': 'select_all'}] + [{'label': fact, 'value': fact} for fact in facts]

# Update country dropdown options based on selected model(s) and fact(s)
@app.callback(
    Output('country-dropdown', 'options'),
    [Input('model-dropdown', 'value'),
     Input('fact-dropdown', 'value')]
)
def update_country_dropdown(selected_models, selected_facts):
    if not selected_models or not selected_facts:
        return []
    if 'select_all' in selected_models or 'select_all' in selected_facts:
        countries = df['country'].unique()
    else:
        countries = df[(df['model'].isin(selected_models)) & (df['fact'].isin(selected_facts))]['country'].unique()
    return [{'label': 'Select All', 'value': 'select_all'}] + [{'label': country, 'value': country} for country in countries]

# Update source dropdown options based on selected model(s), fact(s), and country(s)
@app.callback(
    Output('source-dropdown', 'options'),
    [Input('model-dropdown', 'value'),
     Input('fact-dropdown', 'value'),
     Input('country-dropdown', 'value')]
)
def update_source_dropdown(selected_models, selected_facts, selected_countries):
    if not selected_models or not selected_facts or not selected_countries:
        return []
    if 'select_all' in selected_models or 'select_all' in selected_facts or 'select_all' in selected_countries:
        sources = df['source'].unique()
    else:
        sources = df[(df['model'].isin(selected_models)) & 
                     (df['fact'].isin(selected_facts)) & 
                     (df['country'].isin(selected_countries))]['source'].unique()
    return [{'label': 'Select All', 'value': 'select_all'}] + [{'label': source, 'value': source} for source in sources]

# Update table based on selected features and date range
@app.callback(
    Output('datatable-paging-page-count', 'data'),
    [Input('brand-dropdown', 'value'),
     Input('model-dropdown', 'value'),
     Input('fact-dropdown', 'value'),
     Input('country-dropdown', 'value'),
     Input('source-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_table(brand, model, fact, country, source, from_date, to_date):
    filtered_df = df.copy()

    if brand and 'select_all' not in brand:
        filtered_df = filtered_df[filtered_df['brand'].isin(brand)]
    if model and 'select_all' not in model:
        filtered_df = filtered_df[filtered_df['model'].isin(model)]
    if fact and 'select_all' not in fact:
        filtered_df = filtered_df[filtered_df['fact'].isin(fact)]
    if country and 'select_all' not in country:
        filtered_df = filtered_df[filtered_df['country'].isin(country)]
    if source and 'select_all' not in source:
        filtered_df = filtered_df[filtered_df['source'].isin(source)]

    filtered_df = filtered_df[(filtered_df['date'] >= pd.to_datetime(from_date)) & 
                              (filtered_df['date'] <= pd.to_datetime(to_date))]

    return filtered_df.to_dict('records')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8063))  # Render sets the PORT environment variable
    app.run_server(host='0.0.0.0', port=port, debug=False)