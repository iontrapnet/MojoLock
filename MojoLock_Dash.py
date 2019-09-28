# coding: utf-8
import time
import random

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import scipy.integrate as integrate
from dash.dependencies import State, Input, Output

app = dash.Dash(__name__)

server = app.server

df = pd.read_csv("control_curves.csv")

states = ["IDLE", "TEST", "DDS_DAC", "ADC", "DDS_DAC_ADC","DDS_DAC_ADC_MIXER_FILTER","DDS_DAC_ADC_MIXER_FILTER_PID", "DDS_DAC_ADC_PID"]
trigs =  ["DDS", "ROM", "MIXER","FILTER","DAC", "ADC","PID"]                                                    
outs = ["DDS0", "DDS1", "ROM", "MIXER", "FILTER", "ADC0","ADC1","ADC2", "ADC12", "PID"]

app.layout = html.Div(
             [
	  html.Div([
                html.H2("FPGA Control", 
                  ),           
            ], 
             className="banner",
        ),
      html.Div(
          [
           	 html.Div( 
           	      [
              html.Div(
                    [   
                     html.H3("Test", 
                       style={"textAlign": "center"}),                      
                         html.Div(
                            children=      
                                  [
                                 html.Div(
                                       [
                                    daq.StopButton(
                                          id="start-button",
                                          buttonText="Start",
                                           style={
                                                "display": "flex",
                                                "justify-content": "center",
                                                "align-items": "center",
                                                "paddingBottom": "6%",
                                                            },
                                              n_clicks=0,
                                                        ),
                                      daq.StopButton(
                                            id="stop-button",
                                            buttonText="Stop",
                                             style={
                                                "display": "flex",
                                                "justify-content": "center",
                                                "align-items": "center",
                                                      },
                                               n_clicks=0,
                                                 ),            
                                                   ],
                                            className="row",
                                            style={"marginLeft": "2%"},
                                                ),
                                  html.Div(
                                        [   
                                      html.Div(
                                          [
                                             dcc.Dropdown(
                                             id="port",         
                                             options=[
                                                    {
                                                    "label": i,
                                                     "value": i,} 
                                                     for i in ["COM3","COM4","LPT1","Refresh"]],
                                             value="COM3", 
                                             style={
                                                "display": "flex",
                                                "justify-content": "center",
                                                "align-items": "center",
                                                "paddingBottom": "13%"
                                                            },             
                                              ),           
                                              daq.StopButton(
                                              buttonText="Load",
                                              style={
                                                "display": "flex",
                                                "justify-content": "center",
                                                "align-items": "center",
                                                      },
                                             n_clicks=0,
                                                ),
                                             ],
                                            className="row",
                                            style={  
                                                "marginLeft": "18%"},
                                                 ),                                                          
                                                ], 
                                                ),
                                                ],
                                            className="row",
                                             style={
                                                 "display": "flex",   
                                                 "marginTop": "8%", 
                                                   },
                                                ), 
                                                ],                                               
                                                className="row",
                                                 ), 
                                                  ],
                                                className="two columns",
                                                style={
                                                     "border-radius": "5px",
                                                     "border-width": "5px",
                                                     "border": "1px solid rgb(216, 216, 216)",
                                                     "position":"relative",
                                                     "height": "200px",
                                                 },
                                                  ),
                             html.Div(
                                   [      
                                  html.Div( 
                                        [
                                        html.H3("DAC", style={"textAlign": "center"}), 
                                           html.Div(
                                              children=
                                               	[
                                      		    html.Div(
                                     			   [
                                                        daq.StopButton(
                                                         id="initialize -button",
                                                         buttonText="initialize",
                                                         style={
                                                             "display": "flex",
                                                             "justify-content": "center",
                                                             "align-items": "center",
                                                                },
                                                         n_clicks=0,
                                                             ),
                                                            ],
                                                         className="row",
                                                                  ),
                                               html.Div(
                                                    [                      
                                                    html.Div(
                                                         [  
                                                          daq.NumericInput( 
                                                          id="DAC set",
                                                          label="DAC 0",                 
                                                          labelPosition="bottom",
                                                          style={
                                                               "paddingBottom": "1%",
                                                                 },
                                                                          ),  
                                                          ],
                                                          className="four columns",
                                                          style={
                                                                "marginLeft": "15%",
                                                                "marginRight": "10%",
                                                                },
                                                            ),
                                                     html.Div(
                                                          [  
                                                           daq.NumericInput(
                                                         	  label="DAC 1",                 
                                                           labelPosition="bottom",
                                                                            ),  
                                                          ],
                                                           className="four columns",
                                                           style={"zIndex":"50"},
                                                              ),
                                                       ],
                                                           style={
                                                                "marginTop": "8%", 
                                                                 },
                                                          ),      
                                                   ],
                                                         className="row",
                                                         style={"marginTop": "-5%", "marginBottom": "4%"},
                                                     )
                                         ]  
                                                   ),  
                                                       ],
                                                        className="two columns",
                                                        style={
                                                             "border-radius": "5px",
                                                             "border-width": "5px",
                                                             "border": "1px solid rgb(216, 216, 216)",
                                                             "height": "200px",
                                                              },
                                            ),
                         html.Div(
                                [
                                 html.H3("Filter&ADC", 
                                     style={"textAlign": "center"}),
                             html.Div(
                                children=
                                  [
                                  html.Div(
                                         [
                                           daq.NumericInput(
											   id="filter_param", 
                                               label="Filter Param",
											   value=10,
                                               max=15,
                                               min=0,
                                               size=75,                 
                                               labelPosition="bottom",
                                               style={
                                                    "paddingBottom": "13%",
                                                     "marginBottom": "50%",
                                                     },
										   ),
										   dcc.Dropdown(
                                             id="state",         
                                             options=[
                                                    {
                                                     "label": states[i], "value": i,} 
                                                     for i in range(len(states))],
                                             value=0,
                                             style={
                                                "display": "flex",
                                                "justify-content": "center",
                                                "align-items": "center",
                                                "paddingBottom": "13%", 
                                                 "marginBottom": "50%",
                                                            },             
                                              ), 
                                            dcc.Dropdown(
                                             id="t",         
                                             options=[
                                                    {
                                                     "label": trigs[i], "value": i,} 
                                                     for i in range(len(trigs))],
                                             value=0,
                                             style={
                                                "display": "flex",
                                                "justify-content": "center",
                                                "align-items": "center",
                                                "paddingBottom": "21%", 
                                                 "marginBottom": "50%",
                                                            },             
                                              ),
                                          ],
                                          className="two columns",
                                          style={
                                               "marginLeft": "10%",
                                                "marginRight": "0%",
                                               },
                                          ),
                                html.Div(
                                         [
                                           daq.NumericInput( 
											   id="adc_offset", 
                                               label="ADC Offset",
											   value=950,
                                               max=32767,
                                               min=-32768,
                                               size=75,              
                                               labelPosition="bottom",
                                               style={
                                                    "paddingBottom": "5%",
                                                    "marginBottom": "55%",
                                                     },
                                           ),
                                            dcc.Dropdown(
                                             id="X",         
                                             options=[
                                                    {
                                                     "label": outs[i], "value": i,} 
                                                     for i in range(len(outs))],
                                             value=0,
                                             style={
                                                "display": "flex",
                                                "justify-content": "center",
                                                "align-items": "center",
                                                "paddingBottom": "5%", 
                                                "marginBottom": "50%",
                                                            },             
                                              ),
                                             dcc.Dropdown(
                                             id="Y",         
                                             options=[
                                                    {
                                                     "label": outs[i], "value": i,} 
                                                     for i in range(len(outs))],
                                             value=4,
                                             style={
                                                "display": "flex",
                                                "justify-content": "center",
                                                "align-items": "center",
                                                "paddingBottom": "20%", 
                                                "marginBottom": "45%",
                                                            },             
                                              ),        
                                          ],
                                          className="two columns",
                                          style={
                                               "marginLeft": "40%",
                                                "marginRight": "0%",
                                               },
                                          ),
                                       ],
                                        className="row",
                                          style={
                                               "marginTop": "5%", 
                                               "marginBottom": "4%", 
                                               "marginLeft": "10%",
                                               "marginRight": "0%",
                                                 },
                                      )
                                   ],
                                   className="two columns",
                                   style={
                                         "border-radius": "5px",
                                         "border-width": "5px",
                                         "border": "1px solid rgb(216, 216, 216)",
                                         "height": " 380px",
                                          },
                                     ),                                                                  
                                                                                                                        
                               html.Div(
                                     [
                                       html.H3("DDS 0/1", style={"textAlign": "center"}),
                                 html.Div(
                                     children=[
                                       html.Div(
                                            [      
                                         html.Div(
                                                 [  
                                            daq.NumericInput(
                                            	id="dds0_freq", 
                                                label="Frequency",
                                                value=15000,
                                                max=65535,
                                                min=0,
                                                size=75,
                                                labelPosition="bottom",
                                                style={
                                                      "paddingBottom": "5%",
                                                      },
                                                              ),
                                             daq.NumericInput(
                                             	id="dds0_atten",
                                                label="Attenuation",
                                                value=2,
                                                max=15,
                                                min=0,
                                                size=75,
                                                labelPosition="bottom",
                                                style={
                                                      "paddingBottom": "5%",
                                                      },
                                                              ),
                                             daq.NumericInput(
                                             	id="dds0_phase",
                                                label="Phase", 
                                                value=0,
                                                max=2,
                                                min=0,
                                                size=75,
                                                labelPosition="bottom",
                                                style={
                                                      "paddingBottom": "5%",
                                                      },
                                                              ),                 
                                                  ],
                                                 className="two columns",
                                                 style={
                                                       "marginLeft": "-1%",
                                                       "marginRight": "-1%",
                                                       },
                                           ),
                                        html.Div(
                                                 [  
                                            daq.NumericInput(
                                            	id="dds1_freq",
                                                label="Frequency",
                                                value=32,
                                                max=65535,
                                                min=0,
                                                size=75,
                                                labelPosition="bottom",
                                                style={
                                                      "paddingBottom": "5%",
                                                      },
                                                              ),
                                             daq.NumericInput(
                                             	id="dds1_atten",
                                                label="Attenuation",
                                                value=2,
                                                max=15,
                                                min=0,
                                                size=75,
                                                labelPosition="bottom",
                                                style={
                                                      "paddingBottom": "5%",
                                                      },
                                                              ),
                                             daq.NumericInput(
                                             	id="dds1_phase",
                                                label="Phase", 
                                                value=0,
                                                max=2,
                                                min=0,
                                                size=75,
                                                labelPosition="bottom",
                                                style={
                                                      "paddingBottom": "5%",
                                                      },
                                                              ),                 
                                                  ],
                                                 className="two columns",
                                                 style={
                                                       "marginLeft": "-2%",
                                                       "marginRight": "0%",
                                                       },
                                           ), 
                                          ]
                                          ),
                                          ],                    
                                          className="row",
                                          style={
                                               "marginTop": "2%",
                                               "position": "absolute",
                                               "height": "100%",
                                               "width": "100%",
                                                 },
                                          ),
                                      ],
                                      className="three columns",
                                      style={
                                            "border-radius": "5px",
                                            "border-width": "5px",
                                            "border": "1px solid rgb(216, 216, 216)",
                                            "height": " 380px",
                                            },
                                         ), 
                                html.Div(
                                     [
                                       html.H3("PID Control", style={"textAlign": "center"}),
                                 html.Div(
                                     children=[
                                       html.Div(
                                            [      
                                         html.Div(
                                                 [  
                                            daq.NumericInput(
                                            	id="PID_Setpoint",
                                                label="Setpoint",
                                                value=0,
                                                max=500,
                                                min=0,
                                                size=75,
                                                labelPosition="bottom",
                                                style={
                                                      "paddingBottom": "5%",
                                                      },
                                                              ),
                                             daq.NumericInput(
                                             	id="PID_Offset",
                                                label="Offset",
                                                value=950,
                                                max=10000,
                                                min=0,
                                                size=75,
                                                labelPosition="bottom",
                                                style={
                                                      "paddingBottom": "5%",
                                                      },
                                                              ),
                                              daq.StopButton(
                                                  buttonText="LOCK",
                                                  style={
                                                       "display": "flex",
                                                       "justify-content": "center",
                                                       "align-items": "center",
                                                       "paddingBottom": "5%",
                                                            },
                                                  n_clicks=0,
                                                        ),
                                              daq.StopButton(
                                                  buttonText="UNLOCK",
                                                  style={
                                                       "display": "flex",
                                                       "justify-content": "center",
                                                       "align-items": "center",
                                                            },
                                                  n_clicks=0,
                                                        ),                                                             
                                                  ],
                                                 className="two columns",
                                                 style={
                                                       "marginLeft": "-1%",
                                                       "marginRight": "1%",
                                                       },
                                           ),
                                        html.Div(
                                                 [  
                                            daq.NumericInput(
                                            	id="PID_P",
                                                label="P",
                                                value=10,
                                                max=100000,
                                                min=-100000,
                                                size=75,
                                                labelPosition="bottom",
                                                style={
                                                      "paddingBottom": "5%",
                                                      },
                                                              ),
                                             daq.NumericInput(
                                             	id="PID_I",
                                                label="I",
                                                value=1,
                                                max=1000,
                                                min=-1000,
                                                size=75,
                                                labelPosition="bottom",
                                                style={
                                                      "paddingBottom": "5%",
                                                      },
                                                              ),
                                            daq.LEDDisplay(
                                              id="PID_Ivalue",
                                              value="12345",
                                              style={
                                                  "paddingTop": "0%",
                                                  "paddingLeft": "20.5%",
                                                  "marginLeft": "13%",
                                                  "marginRight": "2%",
                                            },
                                            className="eight columns",
                                            size=12,
                                                        ),                                                              
                                                  ],
                                                 className="two columns",
                                                 style={
                                                       "marginLeft": "-6%",
                                                       "marginRight": "10%",
                                                       },
                                           ), 
                                          ]),
                                          ],                    
                                          className="row",
                                          style={
                                               "marginTop": "2%",
                                               "position": "absolute",
                                               "height": "100%",
                                               "width": "100%",
                                                 },
                                          ),
                                      ],
                                      className="three columns",
                                      style={
                                            "border-radius": "5px",
                                            "border-width": "5px",
                                            "border": "1px solid rgb(216, 216, 216)",
                                            "height": " 380px",
                                            },
                                         ),
                             html.Div(
                                [
                               html.Div(
                                   [
                                  dcc.Graph(
                                    id="xy", 
                                    style={"height": "400px", "marginBottom": "1%", 
                                    "paddingTop": "3%", "paddingBottom": "2%",},
                                    figure={
                                        "layout": go.Layout(
                                            xaxis={
                                                "title": "X",
                                                "autorange": True,
                                            },
                                            yaxis={"title": "Y"},
                                            margin={"l": 70, "b": 100, "t": 0, "r": 25},
                                        ),
                                    },
                                ),
                                 ],
                              className="six columns",
                              style={ 
                                      "border-radius": "5px",
                                      "border-width": "5px",
                                      "border": "1px solid rgb(216, 216, 216)",
                                      "marginBottom": "2%",
                                      "height": " 434px",
                                      "marginTop": "1%"
                            },
                                      ),  
                               html.Div(
                                   [
                                  dcc.Graph(
                                    id="txy", 
                                    style={"height": "400px", "marginBottom": "1%", 
                                    "paddingTop": "3%" , "paddingBottom": "2%",},
                                    figure={
                                        "layout": go.Layout(
                                            xaxis={
                                                "title": "X",
                                                "autorange": True,
                                            },
                                            yaxis={"title": "Y"},
                                            margin={"l": 70, "b": 100, "t": 0, "r": 25},
                                        ),
                                    },
                                ),
                                 ],
                              className="six columns",
                              style={ 
                                      "border-radius": "5px",
                                      "border-width": "5px",
                                      "border": "1px solid rgb(216, 216, 216)",
                                      "marginBottom": "2%",
                                      "height": " 434px",
                                      "marginTop": "1%"
                            },
                                      ), 
                               ],
                             className="row",
                             style={"marginTop": "0%"},
                                ),                                                        
                              ],
                            ),
                            #daq.NumericInput(id="test-input",min=0,max=100,value=50),
							#dcc.Markdown(id='test-output',children=''),
							html.Div(
								[
									html.Div(id="start_output"),
									html.Div(id="filter_adc_output"),
									html.Div(id="dds0_output"),
									html.Div(id="dds1_output"),
									dcc.Interval(id='refresh', interval=1000, n_intervals=0),
								],
								style={"visibility": "hidden"},
							),
                    ],
                    style={
                         "padding": "0px 10px 0px 10px",
                         "marginLeft": "auto",
                         "marginRight": "auto",
                         "width": "auto",
                         "height": "955px",
                         "boxShadow": "0px 0px 5px 5px rgba(204,204,204,0.4)",
                           },
                )

import os, sys, math, struct
from Mojo import Mojo

mojo = Mojo()

@app.callback(
	Output("start_output", "children"), 
	[Input("start-button", "n_clicks"), Input("state", "value")], 
	[State("t", "value"), State("X", "value"), State("Y", "value")]
)
def on_start(start, state, t, X, Y):
    mojo.write(0, [0])
    mojo.write(0, [16*(16*(16*Y+X)+t)+state])
    #mojo.write(0, [16*(16*(16*4+0)+0)+1])
    mojo.write(1, [0])
	
@app.callback(
	Output("filter_adc_output", "children"), 
	[Input("filter_param", "value"), Input("adc_offset", "value")]
)
def update_filter_adc(param, offset):
    mojo.write(5, [int(param)])
    mojo.write(7, [int(offset)])

@app.callback(
	Output("dds0_output", "children"), 
	[Input("dds0_freq", "value"), Input("dds0_atten", "value"), Input("dds0_phase", "value")]
)
def update_dds0(freq, atten, phase):
	mojo.write(2, [65536*(4096*int(atten)+int(2048*phase+0.5))+int(freq)])

@app.callback(
	Output("dds1_output", "children"), 
	[Input("dds1_freq", "value"), Input("dds1_atten", "value"), Input("dds1_phase", "value")]
)
def update_dds1(freq, atten, phase):
	mojo.write(3, [65536*(4096*int(atten)+int(2048*phase+0.5))+int(freq)])
	                                                                        
@app.callback(
    [Output("xy", "figure"),Output("txy", "figure")], 
    [Input("refresh", "n_intervals")], 
    [State("state", "value"), State("t", "value"), State("X", "value"), State("Y", "value")]
)                                                
def on_refresh(n, state, t, X, Y):
    size = 8192
    #t = np.linspace(1, size, size)
    #x = np.sin(t/1024.+n)
    #y = np.cos(t/1024.+n)
    x = np.zeros(size)
    y = np.zeros(size)
    mojo.read(0, size, False, True, id = 0)
    mojo.read(1, 1, id = 1)
    ret0 = mojo['read0']
    ret1 = mojo['read1']
    if ret0:
        data = struct.unpack(b'<'+b'h'*2*size, ret0)
        for i in range(size):
            x[i] = data[2*i]
            y[i] = data[2*i+1]
    if ret1:
        #self.pid.ival.setValue(ret1[0])
        pass
    mojo.write(0, [16*(16*(16*Y+X)+t)+state])
    #mojo.write(0, [16*(16*(16*4+0)+0)+1])
    #mojo.write(0, [16*(16*(16*5+1)+5)+6])             
    return {
        "data": [
            go.Scatter(
                x=x, 
                y=y, 
                mode="lines", 
                marker={"size": 6}, 
                name="XY"
            )
        ],
        "layout": go.Layout(
            autosize=True,
            showlegend=True,
            xaxis={"title": "X", "autorange": True},
            yaxis={"title": "Y", "autorange": True},
            margin={"l": 70, "b": 100, "t": 0, "r": 25},
        ),
    }, {
        "data": [
            go.Scatter(
                x=np.linspace(1, size, size), 
                y=x, 
                mode="lines", 
                marker={"size": 6}, 
                name="X"
            ),
            go.Scatter(
                x=np.linspace(1, size, size),
                y=y,
                mode="lines",
                marker={"size": 6},
                name="Y",
            ),
        ],
        "layout": go.Layout(
            autosize=True,
            showlegend=True,
            xaxis={"title": "t", "autorange": True},
            yaxis={"title": "XY", "autorange": True},
            margin={"l": 70, "b": 100, "t": 0, "r": 25},
        ),
    }
                                                
if __name__ == "__main__":
    mojo.open('COM4')
    app.run_server(debug=False, threaded=False)     