import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
import plotly.express as px
import re
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html
import datetime

path = r"C:\Users\HomePC\Documents\HTMLcSS\Plane\Data\planes.csv"


df = pd.read_csv(path)

threshod = 0.05 * len(df)
col2drop = df.columns[df.isna().sum()<=threshod]

df.dropna(subset= col2drop, inplace= True)

df.drop(columns = "Additional_Info", inplace= True)
priceDict = df.groupby("Airline")["Price"].median().to_dict()

df["Price"].fillna(df["Airline"].map(priceDict), inplace = True)

df["Arrival_Time"] = df["Arrival_Time"].apply(lambda x: x[:5])
df["Arrival_Time"] = pd.to_datetime(df["Arrival_Time"]).dt.strftime('%H:%M')

df["Duration"] = df["Duration"].apply(lambda x: re.sub("[hm]", "", x)).apply(lambda x: re.sub(" ", ":",x))

df["Duration"] = df["Duration"].apply(lambda x: x+":00"if len(x) < 3 else x)

def pad_duration(duration):
    try:
        hours, minutes = duration.split(":")
        hours = hours.zfill(2)
        minutes = minutes.zfill(2)

        if not (0<= int(hours)<= 23 and 0 <=int(minutes)<=59):
            raise ValueError
        return f"{hours}:{minutes}"

    except (ValueError, TypeError):
        return None


df["Duration"] = pd.to_datetime(df["Duration"].apply(lambda x:pad_duration(x)))
df["Duration"] = df["Duration"].dt.strftime("%H:%M:%S")

df["Duration"] = round((pd.to_timedelta(df["Duration"]).dt.total_seconds()/60)/60, 1)

df["Date_of_Journey"] = pd.to_datetime(df["Date_of_Journey"], format='mixed')

df["Month"] = df["Date_of_Journey"].dt.strftime("%b")
df["Day"] = df["Date_of_Journey"].dt.strftime("%A")

categories = ["Monday", "Tuesday",'Wednesday', 'Thursday','Friday','Saturday','Sunday']
df["Day"] = pd.Categorical(df["Day"], categories= categories, ordered= True)

categories2 = ['Jan','Mar','Apr','May','Jun','Sep','Dec']
df["Month"] = pd.Categorical(df["Month"], categories= categories2, ordered= True)

df["Total_Stops"] = df["Total_Stops"].str.strip("stops").replace("non-", 0).astype("int")

airline_count = df["Airline"].value_counts().reset_index()
airLine_fig = px.bar(data_frame= airline_count, x = "Airline" , y = "count")
airLine_fig.update_layout({"width":400, "height":300, "bargap": 0.2}, paper_bgcolor='rgba(0,0,0,0)',  # Transparent background for the paper
    plot_bgcolor='rgba(0,0,0,0)')


priceByAirline = round(df.groupby("Airline")["Price"].mean(),1)
bar_fig = px.bar(data_frame=priceByAirline, y = "Price")
bar_fig.update_layout({"width":400, "height":300, "bargap": 0.2},  paper_bgcolor='rgba(0,0,0,0)',  # Transparent background for the paper
    plot_bgcolor='rgba(0,0,0,0)', xaxis = dict(tickangle = 49))


priceByMonth = df.sort_values(by = "Month").groupby("Month")["Price"].mean()
month_fig = px.bar(data_frame=priceByMonth, y = "Price")
month_fig.update_layout({"width":400, "height":270, "bargap": 0.2}, paper_bgcolor='rgba(0,0,0,0)',  # Transparent background for the paper
    plot_bgcolor='rgba(0,0,0,0)')


priceByDay = df.groupby("Day")["Price"].mean()
day_fig = px.bar(data_frame=priceByDay, y = "Price")
day_fig.update_layout({"width":400, "height":268, "bargap": 0.2}, paper_bgcolor='rgba(0,0,0,0)',  # Transparent background for the paper
    plot_bgcolor='rgba(0,0,0,0)')


scatter_fig = px.scatter(data_frame= df, x = "Duration", y= "Price",  hover_data= "Total_Stops")
scatter_fig.update_layout({"width":400, "height":290}, paper_bgcolor='rgba(0,0,0,0)',  # Transparent background for the paper
    plot_bgcolor='rgba(0,0,0,0)')

count_data = df.groupby(['Airline', 'Total_Stops'])["Price"].mean().unstack(fill_value=0)
import plotly.graph_objects as go
stop_fig = go.Figure()

# Add traces for each Total_Stop category
for column in count_data.columns:
    stop_fig.add_trace(go.Bar(
        x=count_data.index, 
        y=count_data[column], 
        name=column
    ))

# Update layout
stop_fig.update_layout({"width":350, "height":350, "bargap": 0.2},
    #title="Number of Total Stops by Airline",
    xaxis_title="Airline",
    yaxis_title="Price",
    barmode='stack', paper_bgcolor='rgba(0,0,0,0)',  # Transparent background for the paper
    plot_bgcolor='rgba(0,0,0,0)', xaxis = dict(tickangle = 45)
)





import dash
from dash import dcc, html

# Initialize the Dash app
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
server = app.server


# Define the layout of the app
app.layout = html.Div(children=[

    # Header section
    html.Div(children=[
        html.Img(src="assets/logo.jpg", style={
            "margin-top": "2px",
            "border": "solid rgb(88, 140, 215) 1px",
            "width": "30px", 
            "height": "30px"
        }),
        html.H1(html.B("AIRLINE ANALYSIS"))
    ], className="heading"),
    
    # Main content section
    html.Div(children=[
        
        # Sidebar
        html.Div(id="side-bar", children=[
            # Dropdown
            dcc.Dropdown(
                id='airline_dd',
                options=[
                    {'label': 'Jet Airways', 'value': 'Jet Airways'},
                    {'label': 'IndiGo', 'value': 'IndiGo'},
                    {'label': 'SpiceJet', 'value': 'SpiceJet'},
                    {'label': 'Multiple carriers', 'value': 'Multiple carriers'},
                    {'label': 'Air India', 'value': 'Air India'},
                    {'label': 'GoAir', 'value': 'GoAir'},
                    {'label': 'Vistara', 'value': 'Vistara'},
                    {'label': 'Air Asia', 'value': 'Air Asia'}
                
                ], value = None, placeholder='Select airline', className='my-dropdown'
            ),
            
            html.Div(children=[
                                dcc.RadioItems(
                                    id='stop_id',
                                    options=[
                                        {'label': 0, 'value': 0},
                                        {'label': 1, 'value': 1},
                                        {'label': 2, 'value': 2},
                                        {'label': 3, 'value': 3},
                                        {'label': 4, 'value': 4}
                                        
                                    ],
                                    value=None,
                                    labelStyle={
                                        'display': 'inline-flex',
                                        'padding': '10px 10px',
                                        'border': '1px solid #ccc',
                                        'border-radius': '5px',
                                        'margin': '2px',
                                        'cursor': 'pointer',
                                        'background-color': '#f9f9f9',
                                        'color': '#333',
                                        'font-size': '12px',
                                        'height': '50%',
                                        'line-height': '30px',
                                        'box-sizing': 'border-box'
                                    },
                                    inputStyle={
                                        'margin-right': '5px'}
                                    ,
                                    style={
                                        'display': 'flex',
                                        'flex-wrap': 'wrap',
                                        'justify-content': 'center',
                                        'align-items': 'center',
                                        'width': '90%',
                                        'height': '50%',
                                        'border': '1px solid #ddd',
                                        'border-radius': '10px',
                                        'padding': '0 10px',
                                        'box-sizing': 'border-box',
                                        'background-color': '#fff',
                                        'margin-top' : "20px",
                                        "position": "relative",
                                        "left": "10px"
                                    }
                                )
                                ]),
            
            html.Div(children = [ 
            dcc.DatePickerRange(id='airline_date',
                                start_date=None,
                                end_date=None,
                                #placeholder='Select date range',
                                initial_visible_month=df["Date_of_Journey"].min()
                                 )], style={
                                            "width": "80%", 
                                            "margin-top": "20px",
                                            "padding": "8px",
                                            "position": "relative",
                                            "left": "10px",
                                            "border": "solid 1px #007bff",
                                            "border-radius": "5px",
                                            "background-color": "#f8f9fa",
                                            "color": "#495057",
                                            "box-shadow": "0 4px 8px rgba(0, 123, 255, 0.2)",
                                            "font-size": "16px"
                                        }
                                             ), 
            html.Button("Reset", id="reset_button", n_clicks=0,
                                        style={
                                            "position": "relative",
                                            "left": "45px",
                                            "margin-top": "20px",
                                            "padding": "10px 20px",
                                            "background-color": "#007bff",
                                            "color": "#ffffff",
                                            "border": "none",
                                            "border-radius": "5px",
                                            "cursor": "pointer",
                                            "box-shadow": "0 4px 8px rgba(0, 123, 255, 0.2)",
                                            "font-size": "16px"}), 


        ], style={"width": "15%", "float": "left"}),  
        
        # Main panel
        html.Div(children=[
            
            # Top bar
            html.Div(id="top-bar", children=[
                html.Div(
                    id='total_count_display', 
                    children=html.Div([
                        html.P(html.B("Total Count:")),
                        html.P(html.B("0"), style={"font-size": "24px", 
                                                   "margin-top": "5px",
                                                   "position": "relative",
                                                   "top": "40px"})
                    ]), 
                    style={"width": "150px", 
                           "height": "50px", 
                           "box-shadow": "3px 3px 2px 2px gray",
                           "display": "flex", 
                           "flex-direction": "column",
                           "align-items": "center", 
                           "justify-content": "center",
                           "position": "relative",
                            "top": "5px",
                            "left": "5px"}
                ),
                html.Div(
                    id='Average_Price', 
                    children=html.Div([
                        html.P(html.B("Average Price:")),
                        html.P(html.B("0"), style={"font-size": "24px", "margin-top": "5px"})
                    ]), 
                    style={"width": "150px", 
                           "height": "50px", 
                           "box-shadow": "3px 3px 2px 2px gray",
                           "display": "flex", 
                           "flex-direction": "column",
                           "align-items": "center", 
                           "justify-content": "center",
                           "position": "relative",
                            "top": "5px",
                            "left": "30px"}
                ),

                html.Div(
                    id='Average_Duration', 
                    children=html.Div([
                        html.P(html.B("Average Duration:")),
                        html.P(html.B("0"), style={"font-size": "24px", "margin-top": "5px"})
                    ]), 
                    style={"width": "150px", 
                           "height": "50px", 
                           "box-shadow": "3px 3px 2px 2px gray",
                           "display": "flex", 
                           "flex-direction": "column",
                           "align-items": "center", 
                           "justify-content": "center",
                           "position": "relative",
                            "top": "5px",
                            "left": "60px"}
                ),
                html.Div(
                    id='Total_Stop', 
                    children=html.Div([
                        html.P(html.B("0"), style={"font-size": "24px", "margin-top": "5px"}),
                        html.P(html.B("Total Stop"))
                    ]), 
                    style={"width": "150px", 
                           "height": "50px", 
                           "box-shadow": "3px 3px 2px 2px gray",
                           "display": "flex", 
                           "flex-direction": "column",
                           "align-items": "center", 
                           "justify-content": "center",
                           "position": "relative",
                            "top": "5px",
                            "left": "90px"}
                ),

                html.Img(src= "assets/plane.png", style= {"width": "300px", 
                                                          "height": "300px",
                                                          "position": "relative",
                                                          "bottom": "120px",
                                                          "left": "95px"})
            ], className="title_bar"),

            # First box with graph
            html.Div(id="firstbox", children=[
                html.Div(children=[
                    html.Div(children=[
                        html.H2(html.B("Count by Airline", style={"text-align": "center", 
                                                                  "font-size": "14px", 
                                                                  "position": "relative", 
                                                                  "top": "30px",
                                                                  "margin-left": "150px",
                                                                  "border-bottom": "solid 2px black"
                                                                  })),
                        dcc.Graph(id="airline_graph", figure=airLine_fig, style={"height": "90%", 
                                                                                 "width": "90%",
                                                                                 "position": "relative",
                                                                                 "left" : "10px",
                                                                                 "bottom": "45px"
                                                                                 })
                    ], className="airline_count"),

                    html.Div(children=[
                        html.H2(html.B("Price by Airline", style={"text-align": "center", 
                                                                  "font-size": "14px", 
                                                                  "position": "relative", 
                                                                  "top": "35px",
                                                                  "left" : "90px",
                                                                  "margin-left": "150px",
                                                                  "border-bottom": "solid 2px black"
                                                                  })),
                        dcc.Graph(id="price_graph", figure=bar_fig, style={"height": "90%", 
                                                                           "width": "90%",
                                                                           "position": "relative",
                                                                           "left" : "50px",
                                                                           "bottom": "40px"})
                    ], className="airline_price"),

                    html.Div(children=[
                        html.H2(html.B("Price by Airline Stop", style={"text-align": "center", 
                                                                  "font-size": "14px", 
                                                                  "position": "relative", 
                                                                  "top": "65px",
                                                                  "left" : "90px",
                                                                  "margin-left": "150px",
                                                                  "border-bottom": "solid 2px black"
                                                                  })),
                        dcc.Graph(id="stop_graph", figure=stop_fig, style={"height": "90%", 
                                                                           "width": "90%",
                                                                           "position": "relative",
                                                                           "left" : "70px",
                                                                           "bottom": "60px"
                                                                           })
                    ], className="stop_price")
                ], className="displayPosition"),
            ]),
            
            # Second box
            html.Div(id="secondbox", children=[
                html.Div(children=[
                    html.H2(html.B("Price by Duration", style={"text-align": "center", 
                                                          "font-size": "14px", 
                                                          "position": "relative", 
                                                          "top": "70px",
                                                          "margin-left": "150px",
                                                          "border-bottom": "solid 2px black"
                                                          })),
                    dcc.Graph(id="scatter_graph", figure=scatter_fig, style={"height": "90%", 
                                                                             "width": "90%",
                                                                             "position": "relative",
                                                                        "left" : "20px",
                                                                           "bottom": "10px"})
                ], className="duration_price"),

                html.Div(children=[
                    html.H2(html.B("Price by Day", style={"text-align": "center", 
                                                      "font-size": "14px", 
                                                      "position": "relative", 
                                                      "top": "40px",
                                                      "left" : "60px",
                                                      "border-bottom": "solid 2px black",
                                                      "margin-left": "150px"
                                                      })),
                    dcc.Graph(id="day_price", figure=day_fig, style={"height": "90%", 
                                                                     "width": "90%",
                                                                     "position": "relative",
                                                                        "left" : "70px",
                                                                           "bottom": "40px"})
                ], className="price_day"),

                html.Div(children=[
                    html.H2(html.B("Price by Month", style={"text-align": "center", 
                                                        "font-size": "14px", 
                                                        "position": "relative", 
                                                        "top": "40px",
                                                        "left": "60px",
                                                        "margin-left": "150px",
                                                        "border-bottom": "solid 2px black"
                                                        })),
                    dcc.Graph(id="month_price", figure=month_fig, style={"height": "90%", 
                                                                         "width": "90%",
                                                                         "position": "relative",
                                                                        "left" : "70px",
                                                                           "bottom": "40px"})
                ], className="price_month"),
            ], className="displayPosition2")
        ], className="main-content", style={"width": "75%", "float": "right"})  # Adjust the width and float to the right
    ], className="content-wrapper")
])


@app.callback(
    [Output('airline_date', 'start_date'),
     Output('airline_date', 'end_date'),
     Output('stop_id', 'value')],
    [Input('reset_button', 'n_clicks')
     ]
)
def reset_date_range(n_clicks):
    if n_clicks > 0:
        return None, None, None
    return dash.no_update, dash.no_update, dash.no_update


@app.callback(
    [Output(component_id='total_count_display', component_property='children'),
     Output(component_id='Average_Price', component_property='children'),
     Output(component_id='Average_Duration', component_property='children'),
     Output(component_id="Total_Stop", component_property='children')],
    [Input(component_id='airline_dd', component_property='value'),
    Input(component_id='stop_id', component_property='value'),
     Input(component_id='airline_date', component_property='start_date'),
     Input(component_id='airline_date', component_property='end_date')]
)
def update_metrics(selected_airline, selected_stop, start_date, end_date):

    filtered_data = df.copy()
    if start_date and end_date:
        filtered_data = filtered_data[(df['Date_of_Journey'] >= start_date) & (df['Date_of_Journey'] <= end_date)]
    
    if selected_airline:
        filtered_data = filtered_data[filtered_data['Airline'] == selected_airline]

    if selected_stop is not None:
        filtered_data = filtered_data[filtered_data['Total_Stops'] == selected_stop]

    # Calculate metrics
    total_count = len(filtered_data)
    average_price = round(filtered_data["Price"].mean(), 2) if not filtered_data.empty else 0
    average_duration = round(filtered_data["Duration"].mean(), 2) if not filtered_data.empty else 0
    total_stop = filtered_data["Total_Stops"].sum() if not filtered_data.empty else 0

    # Update displays
    total_count_display = html.Div([
        html.P(html.B(f"{total_count}"), style={"font-size": "24px", "margin-top": "5px", "position":"relative", "top": "12px"}),
        html.P(html.I("Total Count"), style={"position":"relative", "bottom": "5px", "font-size": "12px"})
    ])

    average_price_display = html.Div([
        html.P(html.B(f"{average_price}"), style={"font-size": "24px", "margin-top": "5px", "position":"relative", "top": "12px"}),
        html.P(html.I("Average Price"), style={"position":"relative", "bottom": "5px", "font-size": "12px"})
    ])

    average_duration_display = html.Div([
        html.P(html.B(f"{average_duration}"), style={"font-size": "24px", "margin-top": "5px","position":"relative", "top": "12px"}),
        html.P(html.I("Average Duration"), style={"position":"relative", "bottom": "5px", "font-size": "12px"})
    ])

    total_stop_display = html.Div([
        html.P(html.B(f"{total_stop}"), style={"font-size": "24px", "margin-top": "5px", "position":"relative", "top": "12px"}),
        html.P(html.I("Total Stop"), style={"position":"relative", "bottom": "5px", "font-size": "12px"})
    ])

    return total_count_display, average_price_display, average_duration_display, total_stop_display

@app.callback(
    [Output(component_id='airline_graph', component_property='figure'),
     Output(component_id='price_graph', component_property='figure'),
     Output(component_id='stop_graph', component_property='figure'),
     Output(component_id='scatter_graph', component_property='figure'),
     Output(component_id='month_price', component_property='figure'),
     Output(component_id='day_price', component_property='figure')],
    [Input(component_id='airline_dd', component_property='value'),
     Input(component_id='stop_id', component_property='value'),
     Input(component_id='airline_date', component_property='start_date'),
     Input(component_id='airline_date', component_property='end_date')]
)
def update_graphs(selected_airline, selected_stop, start_date, end_date):
    filtered_df = df
    if start_date and end_date:
        filtered_df = filtered_df[(df['Date_of_Journey'] >= start_date) & (df['Date_of_Journey'] <= end_date)]

    if selected_airline:
        filtered_df = filtered_df[filtered_df['Airline'] == selected_airline]

    if selected_stop is not None:
        filtered_df = filtered_df[filtered_df['Total_Stops'] == selected_stop]

    # Generate graphs
    airline_count = filtered_df["Airline"].value_counts().reset_index()
    airline_count.columns = ['Airline', 'count']
    airLine_fig = px.bar(airline_count, x="Airline", y="count")
    airLine_fig.update_layout(width=400, height=300, bargap=0.2, paper_bgcolor='rgba(0,0,0,0)',
                              plot_bgcolor='rgba(0,0,0,0)')

    priceByAirline = round(filtered_df.groupby("Airline")["Price"].mean(), 1).reset_index()
    bar_fig = px.bar(priceByAirline, x="Airline", y="Price")
    bar_fig.update_layout(width=400, height=300, bargap=0.2, paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(tickangle=49))

    count_data = filtered_df.groupby(['Airline', 'Total_Stops'])["Price"].mean().unstack(fill_value=0)
    stop_fig = go.Figure()
    for column in count_data.columns:
        stop_fig.add_trace(go.Bar(x=count_data.index, y=count_data[column], name=column))
    stop_fig.update_layout(width=350, height=350, bargap=0.2, xaxis_title="Airline", yaxis_title="Price",
                           barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                           xaxis=dict(tickangle=45))

    scatter_fig = px.scatter(filtered_df, x="Duration", y="Price", hover_data=["Total_Stops"])
    scatter_fig.update_layout(width=400, height=290, paper_bgcolor='rgba(0,0,0,0)',
                               plot_bgcolor='rgba(0,0,0,0)')

    priceByMonth = filtered_df.sort_values(by="Month").groupby("Month")["Price"].mean().reset_index()
    month_fig = px.bar(priceByMonth, x="Month", y="Price")
    month_fig.update_layout(width=400, height=270, bargap=0.2, paper_bgcolor='rgba(0,0,0,0)',
                             plot_bgcolor='rgba(0,0,0,0)')

    priceByDay = filtered_df.groupby("Day")["Price"].mean().reset_index()
    day_fig = px.bar(priceByDay, x="Day", y="Price")
    day_fig.update_layout(width=400, height=268, bargap=0.2, paper_bgcolor='rgba(0,0,0,0)',
                           plot_bgcolor='rgba(0,0,0,0)')

    return airLine_fig, bar_fig, stop_fig, scatter_fig, month_fig, day_fig

# Run the server
if __name__ == '__main__':
    app.run_server(debug=True)
    
