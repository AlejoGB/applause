import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dashSettings import SIDEBAR_STYLE, UPLOAD_STYLE, TEXT_STYLE, schema, ITEM_STYLE, IMG_STYLE
import base64, ast
import jsonschema


''' Componentes barra lateral '''

controls = dbc.FormGroup([
    html.Div(id='output-json-upload-comp'),
    dcc.Upload(
        id='upload-json',
        children=html.Div([
            'Arrastrar o ',
            html.A('seleccionar JSON')
        ]), 
        style=UPLOAD_STYLE,
        multiple=True
    ),
    html.Div(id='output-json-upload-data', style={'display': 'none'}),    
    html.Div(id='temp-data', style={'display': 'none'})
    
])


sidebar = html.Div([
    html.Img(src='http://www.rfindustrial.com/wp-content/uploads/2020/06/logo-sin-fondo-1024x512.png',
    style=IMG_STYLE,
    ),
    html.H2('Muestras', style=TEXT_STYLE),
    html.Hr(),
    controls
    ],
    style=SIDEBAR_STYLE,
)


def create_list_item(contents, filename, idx):
    ''' creates component from file'''
    data = base64.b64decode(contents[contents.find(',')+1:].encode('ascii'))
    data = ast.literal_eval(data.decode("UTF-8"))
    v = jsonschema.Draft7Validator(schema)
    for error in v.iter_errors(data):
        error = {'JSON_FORMAT_ERROR': str(error.message)}
        return
    #kw = str('json-button-'+str(idx))
    kw = idx
    return dbc.ListGroupItem([
        dbc.ListGroupItemHeading(filename),
        dbc.ListGroupItemText(data['id']),
        #html.Div(data['muestras'], style={'display': 'none'}),
        #html.Div(data['data'], style={'display': 'none'})
        ],
        id={
            'role': 'data-button',
            'index': kw
        },
        style=ITEM_STYLE,
        action=True
    )

def create_list_group(content_list, filename_list):
    ''' creates list of components '''
    ITEMS = [
        create_list_item(c, f, i) for c, f, i in
        zip(content_list, filename_list, range(len(filename_list))) 
    ]
    return dbc.ListGroup(ITEMS)

def create_data_dict(c):
    ''' creates a div for each file '''
    data = base64.b64decode(c[c.find(',')+1:].encode('ascii'))
    data = ast.literal_eval(data.decode("UTF-8"))
    v = jsonschema.Draft7Validator(schema)
    for error in v.iter_errors(data):
        # TODO: Levantar un error para archivos de formato incorrecto
        error = {'JSON_FORMAT_ERROR': str(error.message)}
        return
    return data