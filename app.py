import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from urllib.parse import quote as urlquote
import pickle as pickle
from textblob.classifiers import NaiveBayesClassifier
from nltk.tokenize import word_tokenize

# this is for pie charts
import plotly.graph_objects as go # or plotly.express as px


import pandas as pd

## Load Assets
#pickle_in = open('linear83.pickle','rb')
#sentiemoji = pickle.load(pickle_in)
cl = pickle.load( open( "linear83.pickle", "rb" ) )
df1 = pd.read_csv('alexa.csv')


def pie_star(a,b):

    labels = a.values.tolist()
    values = b.values.tolist()
    # Use `hole` to create a donut-like pie chart
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6)])
    return fig


# Components
# Building an example
def example():
    pie_star(df1['product'], df1['rating'])

def senti():
    df1['sentiment'] = df1['review'].apply(lambda tweet: cl.classify(str(tweet)))
    df1['emoji'] = df1['sentiment']
    df1['emoji'] = df1['emoji'].replace({"pos": "😃", "neg": "😡", "neu": "😐"})


### Upload

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MATERIA])

app.layout = html.Div([
    dbc.Jumbotron(
        [
            dbc.Container(
                [

                    html.H1("Senti Emoji", className="display-3"),
                    html.P(
                        "Sentiment analysis of amazon products",
                        className="lead",
                    ),
                    html.P(
                        "",
                        className="lead",
                    ),
                    html.Div(
                        [
                            dbc.Input(id="input", placeholder="Type to test...", type="text"),
                            html.Br(),
                            html.H4(id="output"),
                        ]
                    ),


                    html.H4("Total stars per product (example)"),
                    html.Div(dcc.Graph(figure=pie_star(df1['product'], df1['rating']))),

                    dbc.Collapse(
                        dbc.Card(
                            #senti(),
                            #html.Div(dcc.Graph(figure=pie_star(df1['sentiment'], df1['rating']))),
                            ),
                        id="collapse",
                    ),
                    html.H4("Files must have | rating | product | review | headers to be processed"),
                    dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                'Drag and Drop or ',
                                html.A('Select Files')
                            ]),
                            style={
                                'width': '95%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px'
                            },
                            # Allow multiple files to be uploaded
                            multiple=True
                        ),
                        html.Div(id='output-data-upload'),
                ],
                fluid=True,
            )
        ],
        fluid=True,
    ),
])


# Place output
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            df['sentiment'] = df['review'].apply(lambda tweet: cl.classify(str(tweet)))
            df['emoji'] = df['sentiment']
            df['emoji'] = df['emoji'].replace({"pos": "😃", "neg": "😡", "neu": "😐"})
            return html.Div([
                html.H5(filename),
                html.H6(datetime.datetime.fromtimestamp(date)),
                html.Div(
                    [
                        dbc.Button(
                            "View CSV",
                            id="collapse-button",
                            className="mb-3",
                            color="primary",
                        ),
                        dbc.Collapse(
                            dbc.Card(dbc.CardBody(dash_table.DataTable(
                                data=df.to_dict('records'),
                                columns=[{'name': i, 'id': i} for i in df.columns]
                            ),)),
                            id="collapse",
                        ),
                    ]
                ),
                html.Hr(),  # horizontal line
                html.H5("Total Stars per product"),
                html.Div(dcc.Graph(figure=pie_star(df['product'], df['rating']))),
                html.Div(dcc.Graph(figure=pie_star(df['product'], df['sentiment'])))

            ])
        else:
            return dbc.Alert(
                "Hello! Please submit a CSV with the appropriate headers: product_name rating etc.",
                id="alert-fade",
                dismissable=True,
                is_open=True,
            )

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

# upload function
@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@app.callback(
    Output("collapse1", "is_open"),
    [Input("collapse-button1", "n_clicks")],
    [State("collapse1", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# collapse function
@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# alert function
@app.callback(
    Output("alert-fade", "is_open"),
    [Input("alert-toggle-fade", "n_clicks")],
    [State("alert-fade", "is_open")],
)
def toggle_alert(n, is_open):
    if n:
        return not is_open
    return is_open


# input
@app.callback(Output("output", "children"), [Input("input", "value")])
def output_text(value):
    return cl.classify(str(value))


@app.callback(Output('output-data2', 'data1'),
               [Input("fade", "n_clicks")],
               [State("alert-fade", 'stttadf')],)
def alert(value):
    return

if __name__ == '__main__':
    app.run_server(debug=True)