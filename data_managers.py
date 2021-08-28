import dash
import dash_core_components as dcc
import dash_html_components as html
from dash_html_components import Br
from numpy import append
import plotly.express as px
import dash_table
import pandas as pd
from readDB import ReadMongoData as db
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.figure_factory as ff
from dash.dependencies import Input, Output

dash_app = dash.Dash(__name__)
# app = dash.Dash("app")
app = dash_app.server

# df_bookdetails = db.getBookingDetails()
#Import data collections
df_bookdetails = db.getBookingDetails()
df_bookings = db.getBookings()
df_customers = db.getCustomers()
df_agents = db.getAgents()
df_ppsupliers = db.getPPSupliers()
df_products_suppliers = db.getProductsSuppliers()
df_suppliers = db.getSuppliers()
df_packages = db.getPackages()

#Extract the necessary columns and get rid of extra data that is not required for data analytics
df_bookdetails_c = df_bookdetails[['BookingId', 'Destination', 'BasePrice',	'AgencyCommission', 'TripStart', 'TripEnd', 'ProductSupplierId' ]]
df_bookings_c = df_bookings[['BookingId',	'BookingDate', 'TravelerCount',	'CustomerId',	'PackageId']]
df_customers_c = df_customers[['CustomerId', 'AgentId']]
df_agents_c = df_agents[['AgentId', 'AgtFirstName', 'AgtLastName','AgtPosition','AgencyId' ]]
df_packages = df_packages[["PackageId", "PkgName"]]

#1st merge
df_bb = pd.merge(df_bookdetails_c, df_bookings_c, on="BookingId")
df_bb = df_bb.reset_index()

#2nd merge
df_bb = pd.merge(df_bb, df_packages, on="PackageId")

#3rd merge
df_customers_c= df_customers_c.reset_index()
df_bbc = df_bb.merge(df_customers_c, on="CustomerId", how="left")

#4th merge
df_bbca = df_bbc.merge(df_agents_c, on= "AgentId", how="left")

#5th merge
df_bbcap= df_bbca.merge(df_products_suppliers, on= "ProductSupplierId", how="left")

#************************************Final*******************************************************************
#7th merge. This is the final database for data analytics
df_bbcaps= df_bbcap.merge(df_suppliers, on= "SupplierId", how="left")

#******************************************************************************************************

#converting decimal to float
df_bbcaps[['BasePrice', 'AgencyCommission']] = df_bbca[['BasePrice', 'AgencyCommission']].astype('str').astype('float64')

#calculate total price and create a new column
df_bbcaps['TotalPrice'] = df_bbcaps['BasePrice'] * df_bbcaps['TravelerCount']

#sort by date
df_bbcaps=df_bbcaps.sort_values(by="BookingDate")

#Cumulative sales
df_bbcaps['CumSales'] = df_bbcaps['TotalPrice'].cumsum()

#Cumulative Commission
df_bbcaps["CumCommission"] = df_bbcaps["AgencyCommission"].cumsum()

# Average sales
df_bbcaps["AverageSales"] = df_bbcaps['TotalPrice'].rolling(window=2).mean()

#Average Commission
df_bbcaps["AverageCommission"] = df_bbcaps['AgencyCommission'].rolling(window=2).mean()

#Create username column
df_bbcaps["UserName"] = df_bbcaps["AgtLastName"].str.lower()


#*******************************************agent*************************************************

#Group by agent
df_bbcaps_byagentlname = df_bbcaps.groupby("AgtLastName")

#Calculate total sales per agent
total_sales_agent = df_bbcaps_byagentlname['TotalPrice'].sum()
#convert to dataframe
total_sales_agent_df = df_bbcaps_byagentlname['TotalPrice'].sum().to_frame(name = 'Total Sales').reset_index()

#Calculate average sales per agent
avg_sales_agent = df_bbcaps_byagentlname['TotalPrice'].mean()

#convert to dataframe
avg_sales_agent_df = df_bbcaps_byagentlname['TotalPrice'].mean().to_frame(name = 'Average Sales').reset_index()


#Calculate total commission per agent
total_com_agent = df_bbcaps_byagentlname['AgencyCommission'].sum()

#convert to dataframe
total_com_agent_df = df_bbcaps_byagentlname['AgencyCommission'].sum().to_frame(name = 'Total Commission').reset_index()

#Calculate average commission per agent
avg_com_agent = df_bbcaps_byagentlname['AgencyCommission'].mean()

#convert to dataframe
avg_com_agent_df = df_bbcaps_byagentlname['AgencyCommission'].mean().to_frame(name = 'Average Commission').reset_index()

df_bbcaps_agent = df_bbcaps.drop(['TotalPrice','CumSales', 'CumCommission', 'AverageSales', 'AverageCommission'], axis=1)

#*******************************************supplier****************** *******************************
#Group by supplier
df_bbcaps_bysupname = df_bbcaps.groupby("SupName")

#total sales per suplier
total_sales_sup = df_bbcaps_bysupname["TotalPrice"].sum()

#conver to dataframe
total_sales_sup_df = df_bbcaps_bysupname["TotalPrice"].sum().to_frame(name = 'Total Sales per Supplier').reset_index()

#average sales per supplier
avg_sales_sup = df_bbcaps_bysupname["TotalPrice"].mean()

#*******************************************package*************************************************
#Group by package
df_bbcaps_bypack = df_bbcaps.groupby("PkgName")

#total sales per package
total_sales_pack = df_bbcaps_bypack["TotalPrice"].sum()
#conver to dataframe
total_sales_pack_df = df_bbcaps_bypack["TotalPrice"].sum().to_frame(name = 'Total Sales per Package').reset_index()

#************************************************************plots********************************
#total sales
fig1 = px.line(df_bbcaps, x="BookingDate", y="CumSales")
fig1.update_xaxes(title_text='Date')
fig1.update_yaxes(title_text='Total Sales')

#total commission
fig2 = px.line(df_bbcaps, x="BookingDate", y="CumCommission")
fig2.update_xaxes(title_text='Date')
fig2.update_yaxes(title_text='Total Commision')

#total sales per agent
fig3 = px.bar(total_sales_agent, x=total_sales_agent.index, y="TotalPrice")
fig3.update_xaxes(title_text='Agent')
fig3.update_yaxes(title_text='Total Sales($)')

#average sales per agent
fig4 = px.bar(avg_sales_agent, x=avg_sales_agent.index, y="TotalPrice")
fig4.update_xaxes(title_text='Agent')
fig4.update_yaxes(title_text='Average Sales($)')

#total sales per supplier
fig5 = px.bar(total_sales_sup, x=total_sales_sup.index, y="TotalPrice")
fig5.update_xaxes(title_text='Supplier')
fig5.update_yaxes(title_text='Total Sales($)')

#total sales per package
fig6 = px.bar(total_sales_pack, x=total_sales_pack.index, y="TotalPrice")
fig6.update_xaxes(title_text='Package')
fig6.update_yaxes(title_text='Total Sales($)')

fig7 = px.pie(total_sales_pack, values='TotalPrice', names=total_sales_pack.index)
fig13 = px.pie(df_bbcaps, values='TotalPrice', names="Destination")

#*********************************************************dash****************************************

dash_app.layout = html.Div(
    children=[
        dcc.Location(id='url', refresh=False),

        html.Div(id='manager-content'),
        html.Br(),  
        
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.H1(children=''),

        html.Div(id='table-content'),
        html.Br(),                 
        html.H1(children=''),

        html.Div(id='graph-content'),
        html.Br(),        


    ]
)

@dash_app.callback(dash.dependencies.Output('graph-content', 'children'),
                   [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):

    if isinstance(pathname, str):
        pathname = pathname[1:].split('/')
        print(pathname, '\n')
        # pathname = pathname.replace('/', '')
        # print(pathname)
    
        df_agent_select= df_bbcaps_agent[df_bbcaps_agent["UserName"]== pathname[0]]

        #Coville
        #calculate total price and create a new column
        df_agent_select['TotalPrice'] = df_agent_select['BasePrice'] * df_agent_select['TravelerCount']

        #Cumulative sales
        df_agent_select['CumSales'] = df_agent_select['TotalPrice'].cumsum()

        #Cumulative Commission
        df_agent_select["CumCommission"] = df_agent_select["AgencyCommission"].cumsum()

        # Average sales
        df_agent_select["AverageSales"] = df_agent_select['TotalPrice'].rolling(window=2).mean()

        #Average Commission
        df_agent_select["AverageCommission"] = df_agent_select['AgencyCommission'].rolling(window=2).mean()



        fig8 = px.bar(df_agent_select, x="Destination", y="TotalPrice")
        fig8.update_xaxes(title_text='Destination')
        fig8.update_yaxes(title_text='Total Sales($)')
        fig9 = px.bar(df_agent_select, x="PkgName", y="AgencyCommission")
        fig9.update_xaxes(title_text='Package')
        fig9.update_yaxes(title_text='Total Commission($)')
        fig10 = px.line(df_agent_select, x="BookingDate", y="CumSales")
        fig10.update_xaxes(title_text='Date')
        fig10.update_yaxes(title_text='Cumulative Sales($)')
        fig11 = px.line(df_agent_select, x="BookingDate", y="CumCommission")
        fig11.update_xaxes(title_text='Date')
        fig11.update_yaxes(title_text='Cumulative Commission($)')

        fig12 = px.pie(df_agent_select, values='TotalPrice', names="PkgName")


       
        return html.Div([
            # html.H3('You are on page {}'.format(pathname))
            html.Br(),
            html.Div(children='Total Sales per Destination'),
            html.Br(),
            dcc.Graph(figure=fig8),
            html.Div(children='Total Commission per Package'),
            html.Br(),
            dcc.Graph(figure=fig9),
            html.Div(children='Cumulative Sales'),
            html.Br(),
            dcc.Graph(figure=fig10),
            html.Div(children='Cumulative Commission'),
            html.Br(),
            dcc.Graph(figure=fig11),
            html.Div(children='Sales per Package Comaprison'),
            html.Br(),
            dcc.Graph(figure=fig12),
            html.Br(),

            html.Div(children=['Popular Destination']),

            dcc.Graph(figure=fig13),

            html.Br(),
            # dcc.Graph(figure=fig)
        ])

@dash_app.callback(dash.dependencies.Output('table-content', 'children'),
                   [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):

    if isinstance(pathname, str):
        pathname = pathname[1:].split('/')
        print(pathname, '\n')
        # pathname = pathname.replace('/', '')
        # print(pathname)
        df_agent_select= df_bbcaps_agent[df_bbcaps_agent["UserName"]== pathname[0]]
        pathnamec = pathname[0].upper()

        return html.Div([
            
            html.H1(children="Agent's Name: " + pathnamec),
            html.Div(children= "Summary Table"),
            
            html.Br(),
            # html.H3('You are on page {}'.format(pathname))
            dash_table.DataTable(
            id='maintable',
            columns=[{"name": i, "id": i} for i in df_agent_select.columns],
            data=df_agent_select.to_dict('records'), 
            style_cell={'textAlign': 'center'},
            style_header={
                'backgroundColor': 'lightblue',
                'fontWeight': 'bold',
                'border': '1px solid black'
            },            
            page_action='native',   # all data is passed to the table up-front
            page_size=10,
            style_table={'height': '400px', 'overflowY': 'auto'}
        ),
            # dcc.Graph(figure=fig)
        ])

@dash_app.callback(dash.dependencies.Output('manager-content', 'children'),
                   [dash.dependencies.Input('url', 'pathname')])
def display_manager(pathname):
    print("manager",pathname, '\n')
    if isinstance(pathname, str) and (pathname=="/"):
        print("manager2",pathname, '\n')
        # pathname = pathname[1:].split('/')
        

        return html.Div([
                dcc.Link('Home', href='/'),
                html.Br(),

                dcc.Link('Agent: Coville', href='/coville'),
                html.Br(), 
                dcc.Link('Agent: Dahl', href='/dahl'),
                html.Br(), 
                dcc.Link('Agent: Delton', href='/delton'),
                html.Br(), 
                dcc.Link('Agent: Dixon ', href='/dixon '),
                html.Br(), 
                dcc.Link('Agent: Jones', href='/jones'),
                html.Br(),
                dcc.Link('Agent: Lisle', href='/lisle'),
                html.Br(), 
                dcc.Link('Agent: Merrill', href='/merrill'),
                html.Br(), 
                dcc.Link('Agent: Peterson', href='/peterson'),
                html.Br(),
                dcc.Link('Agent: Reynolds', href='/reynolds'),
                html.Br(),                            
                html.Br(),
                # content will be rendered in this element
                html.Div(id='page-content'),

                html.Br(),        
                html.H1(children='Overall Performance'),
                html.Div(children=[
                    'All Data'
                ]),
                html.Br(),
                dash_table.DataTable(
                    id='maintable',
                    columns=[{"name": i, "id": i} for i in df_bbcaps.columns],
                    data=df_bbcaps.to_dict('records'), 
                    #style_cell={'textAlign': 'center'},
                    style_cell={'padding': '5px', 'textAlign': 'center'},   # style_cell refers to the whole table
                    style_header={
                        'backgroundColor': 'lightblue',
                        'fontWeight': 'bold',
                        'border': '1px solid black'
                    },
                style_data_conditional=[        
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        }
                        ],
                    page_action='native',   # all data is passed to the table up-front
                    page_size=10,
                    style_table={'height': '400px', 'overflowY': 'auto'}
                ),                
                # dash_table.DataTable(
                #     id='maintable',
                #     columns=[{"name": i, "id": i} for i in df_bbcaps.columns],
                #     data=df_bbcaps.to_dict('records'), 
                #     style_cell={'textAlign': 'center'},
                #     page_action='native',   # all data is passed to the table up-front
                #     page_size=10,
                #     style_table={'height': '400px', 'overflowY': 'auto'}
                # ),
                html.Br(),
                html.Div(children=[
                    'Performance Summary'
                ]),
                html.Br(),
                dash_table.DataTable(
                    id='maintable2',
                    columns= [
                    {"name": "Destination", "id": "Destination"},
                    {"name": "CumSales", "id": "CumSales"},
                    {"name": "CumCommission", "id": "CumCommission"},
                    {"name": "AverageSales", "id": "AverageSales"},
                    {"name": "AverageCommission", "id": "AverageCommission"},],

                    data=df_bbcaps[["Destination","CumSales", "CumCommission","AverageSales","AverageCommission"]].to_dict('records'), 
                    style_cell={'textAlign': 'center'},
                    page_action='native',   # all data is passed to the table up-front
                    style_header={
                        'backgroundColor': 'lightblue',
                        'fontWeight': 'bold',
                        'border': '1px solid black'
                    },
                    page_size=10,
                    style_table={'height': '400px', 'overflowY': 'auto'}
                ),
                html.Br(),
                html.Div(children=[
                    'Cumulative Sales'
                ]),
                dcc.Graph(figure=fig1),

                html.Div(children=[
                    'Cumulative Commission'
                ]),
                dcc.Graph(figure=fig2),

                html.Br(),
                html.Br(),


                html.H1(children='Agent Data'),
                html.Div(children=[
                    'Total Sales Per Agent'
                ]),

                html.Br(),
                dash_table.DataTable(
                    id='totalsales_agent',
                    columns=[{"name": i, "id": i} for i in total_sales_agent_df.columns],
                    data=total_sales_agent_df.to_dict('records'),
                    # style_cell={'textAlign': 'center'},
                    style_cell={'padding': '5px', 'textAlign': 'center'},   # style_cell refers to the whole table
                    style_header={
                        'backgroundColor': 'lightblue',
                        'fontWeight': 'bold',
                        'border': '1px solid black'
                    },
                style_data_conditional=[        
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        }
                        ],                        
                    page_size=8
                ),

                dcc.Graph(figure=fig3),       
                html.Br(),

                html.Div(children=[
                    'Average Sales Per Agent'
                ]),
                html.Br(),
                dcc.Graph(figure=fig4),

                html.H1(children='Supplier Data'),
                html.Div(children=[
                    'Total Sales Per Supplier'
                ]),
                html.Br(),
                dash_table.DataTable(
                    id='totalsales_sup',
                    columns=[{"name": i, "id": i} for i in total_sales_sup_df.columns],
                    data=total_sales_sup_df.to_dict('records'),
                    # style_cell={'textAlign': 'center'},
                    style_cell={'padding': '5px', 'textAlign': 'center'},   # style_cell refers to the whole table
                    style_header={
                        'backgroundColor': 'lightblue',
                        'fontWeight': 'bold',
                        'border': '1px solid black'
                    },
                style_table={'height': '400px', 'overflowY': 'auto'},                    
                style_data_conditional=[        
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        }
                        ],                        
                    page_size=40
                ),                
                dcc.Graph(figure=fig5),

                html.H1(children='Package Data'),
                html.Div(children=[
                    'Total Sales Per Package'
                ]),

                html.Br(),
                dash_table.DataTable(
                    id='totalsales_pack',
                    columns=[{"name": i, "id": i} for i in total_sales_pack_df.columns],
                    data=total_sales_pack_df.to_dict('records'),
                    # style_cell={'textAlign': 'center'},
                    style_cell={'padding': '5px', 'textAlign': 'center'},   # style_cell refers to the whole table
                    style_header={
                        'backgroundColor': 'lightblue',
                        'fontWeight': 'bold',
                        'border': '1px solid black'
                    },
                style_data_conditional=[        
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        }
                        ],                        
                    page_size=4
                ),

                dcc.Graph(figure=fig6),

                html.Div(children=[
                    'Popular Packages'
                ]),

                dcc.Graph(figure=fig7),

                html.Div(children=[
                    'Popular Destination'
                ]),

                dcc.Graph(figure=fig13),

                html.Br(),

            ])

if __name__ == '__main__':
    dash_app.run_server(debug=True)
