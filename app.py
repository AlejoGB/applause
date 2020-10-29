# Dash components
import dash
import dash_auth
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL
from dashSettings import schema
from dashSidebarComp import controls, sidebar, create_list_group, create_data_dict
from dashContentComp import content, create_row_3, create_row_2, create_row_1
# RFI components
import dinalib as dl
# Other components
import json
''' Main Dash APP Cartas Dinamometricas '''

# with open('dash-client.json') as f:
#     try:
#         VALID_USERNAME_PASSWORD_PAIRS = json.load(f)
#     except json.decoder.JSONDecodeError as e:
#         print("de formato de archivo JSON : {}".format(e)) 

VALID_USERNAME_PASSWORD_PAIRS = {
    "rfindustrial": "RFI#123"
}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

server = app.server

app.layout = html.Div([sidebar, content])



@app.callback(
        Output('output-json-upload-comp', 'children'),
        Output('output-json-upload-data', 'children'),
        [Input('upload-json', 'contents')],
        [State('upload-json', 'filename')],
        prevent_initial_call=True,
        )
def update_output(content_list, file_list):
    if file_list is not None:
        data = [create_data_dict(c) for c in content_list]
        children = [create_list_group(content_list,file_list)]
        return children, str(data)
    return None

@app.callback(
        Output('temp-data', 'children'),
        [Input({'role': 'data-button', 'index': ALL}, 'n_clicks_timestamp')],
        [State('output-json-upload-data', 'children')],
        prevent_initial_call=True
        )
def count_clicks(n, files_data):
    ctx = dash.callback_context
    data_list = eval(files_data)    
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = eval(ctx.triggered[0]['prop_id'].split('.')[0])
        data = data_list[button_id['index']]
        if data:
            if data['data'][-2] == ',':
                data['data'] = data['data'][0:-2] + data['data'][-1]

        config = {
            "Celda": {
                "PesoConocido1": 0,
                "PesoConocido2": 22046.23,
                "Referencia1": 718,
                "Referencia2": 1159
            },
            "Pozo": {
                "ID": "C143",
                "Carrera": 168
            },
            "Server": {
                "Puerto":20011,
                "idPost":21
                },
            "Response": {
                "KeepAlive": "Base\tHOLA\n",
                "Init": ["CARTA\tHOLA\n"]
                }
        } 
        cartas = dl.DinaProc(config, data['data'], len(data), 'hexa', sample_rate=64, splitchar=':', config_dtype='dict')
        data ={
            'Muestras': list(range(len(cartas.data_array.T[0]))),
            'Fuerza': list(map(int,cartas.data_array.T[0])),
            'Fuerza escalada': list(map(int,cartas.scaled_cycle_data)),
            'Aceleración': list(map(int,cartas.data_array.T[1])),
            'Ciclo': int(cartas.cycle[1]),
            'Muestras Ciclo': list(range(len(cartas.cycle_data))),
            'Aceleracion Ciclo': list(map(int,cartas.cycle_data.T[1])),
            'Velocidad Ciclo': list(cartas.vel),
            'Posicion Ciclo': list(cartas.pos),
            'Frec': list(cartas.frec),
            'Acel Frec': list(map(abs,cartas.cycle_data_fft.T[0])),
            'Vel Frec': list(map(abs,cartas.cycle_data_fft.T[1])),
            'Pos Frec': list(map(abs,cartas.cycle_data_fft.T[1])),
        }
    return json.dumps(data)

@app.callback(
    [Output('row-1', 'children'),
    Output('row-2', 'children'),
    Output('row-3', 'children')],
    [Input('temp-data', 'children')],
        prevent_initial_call=True
)
def update_content(data):
    return create_row_1(json.loads(data)), create_row_2(json.loads(data)), create_row_3(json.loads(data))


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port='8050')
    #app.run_server(debug=False) #True, port='8085')