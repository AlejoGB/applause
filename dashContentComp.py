import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dashSettings import CONTENT_STYLE, TEXT_STYLE, CARD_TEXT_STYLE, CONTENT_TEXT_STYLE
''' Componentes principales ''' 

content = html.Div(
    [
        html.H2('Cartas de Superficie', style=CONTENT_TEXT_STYLE),
        html.Hr(),

        html.Div(id='row-1'),
        html.Div(id='row-2'),
        html.Div(id='row-3'),

    ],
    style=CONTENT_STYLE
)

def create_row_1(data):
    fig_sup = go.Figure()
    fig_sup.add_trace(go.Scatter(x=list(data['Posicion Ciclo']),
                            y=list(data['Fuerza escalada']),
                            mode='lines'
                            ))
    fig_sup.update_layout(xaxis_title='Desplazamiento (in)',
                        yaxis_title='Fuerza',
                        yaxis_range=[10000,20000],
                        plot_bgcolor='#FFF',
                        paper_bgcolor='#FFF',
                        font_color='#263246'
                        )
    return dbc.Row([
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H4(id='card_title_1', children=['Pozo: '], className='card-title',
                                    style=CARD_TEXT_STYLE),
                            html.P(id='card_text_1', 
                                children=['Fecha: '],
                                style=CARD_TEXT_STYLE
                            ),
                            html.Table([
                                html.Tr([html.Td('GPM: '), html.Td(id='gpm')]),
                                html.Tr([html.Td('Trabajo (lbf-in): '), html.Td(id='trabajo')]),
                                html.Tr([html.Td('Fuerza Max (lbf): '), html.Td(id='fza-max')]),
                                html.Tr([html.Td('Fuerza Min (lbf): '), html.Td(id='fza-min')]),
                                ],
                                style=CARD_TEXT_STYLE    
                            ),
                        ]
                    )
                ]
            ),
            width=3
        ),
        dbc.Col(
            dbc.Card(
                [
                    dcc.Graph(id='carta-sup',
                            figure=fig_sup),
                ]),
            width=9
        ),
 
    ])

def create_row_2(data):
    fig_input = go.Figure()
    fig_input.add_trace(go.Scatter(x=list(data['Muestras']),
                                y=list(data['Fuerza']),
                                mode='lines',
                                name='Fuerza'))
    fig_input.add_trace(go.Scatter(x=list(data['Muestras']),
                                y=list(data['Aceleración']),
                                mode='lines',
                                name='Aceleración'))
    fig_input.add_shape(dict(
            type="rect",
            xref="x",
            yref="paper",
            x0=0,
            y0=0,
            x1=data['Ciclo'],
            y1=1,
            fillcolor='LightSalmon',
            opacity=0.5,
            layer='below',
            line_width=0)
            )
    fig_input.update_layout(title='Datos de entrada y ciclo obtenido',
                        title_x=0.5,
                        xaxis_title='Muestras',
                        yaxis_title='Magnitud',
                        plot_bgcolor='#FFF',
                        paper_bgcolor='#FFF',
                        font_color='#263246'
    )

    fig_AVP = go.Figure()
    fig_AVP.add_trace(go.Scatter(x=list(data['Muestras Ciclo']),
                                y=list(data['Aceleracion Ciclo']),
                                mode='lines',
                                name='Aceleración'))
    fig_AVP.add_trace(go.Scatter(x=list(data['Muestras Ciclo']),
                                y=list(data['Velocidad Ciclo']),
                                mode='lines',
                                name='Velocidad'))
    fig_AVP.add_trace(go.Scatter(x=list(data['Muestras Ciclo']),
                                y=list(data['Posicion Ciclo']),
                                mode='lines',
                                name='Posición'))
    fig_AVP.update_layout(title='Aceleración Velocidad Y Posición',
                        title_x=0.5,
                        xaxis_title='Muestras',
                        yaxis_title='Magnitud escalada',
                        plot_bgcolor='#FFF',
                        paper_bgcolor='#FFF',
                        font_color='#263246'
)
    return dbc.Row([
        dbc.Col(
            dbc.Card(
                [
                dcc.Graph(id='input',
                    figure=fig_input)
                ]), 
            style={
                'width': '200%'
            },
            width=8
        ),
        dbc.Col(
            dbc.Card(
                [
                dcc.Graph(id='FVP',
                    figure=fig_AVP)
                ]),
            style={
                'width': '200%'
            },
            width=4
        ),
    ],
    )

def create_row_3(data):
    fig_frec = go.Figure()
    fig_frec.add_trace(go.Scatter(x=data['Frec'],
                                y=data['Acel Frec'],
                                mode='lines',
                                name='Acc'))
    fig_frec.add_trace(go.Scatter(x=data['Frec'],
                                y=data['Vel Frec'],
                                mode='lines',
                                name='Vel'))
    fig_frec.add_trace(go.Scatter(x=data['Frec'],
                                y=data['Pos Frec'],
                                mode='lines',
                                name='Pos'))
    fig_frec.update_layout(title='Aceleración Velocidad Y Posición',
                        title_x=0.5,
                        xaxis_title='Muestras',
                        yaxis_title='Magnitud escalada',
                        xaxis_range=[0,7],
                        plot_bgcolor='#FFF',
                        paper_bgcolor='#FFF',
                        font_color='#263246'
    )
    return dbc.Row(
    [
        dbc.Col(
            dbc.Card(
                [
                dcc.Graph(id='FFT',
                    figure=fig_frec)
                ]), md=12,
        )
    ]
    )