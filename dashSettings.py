# the style arguments for the sidebar.
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '20%',
    'padding': '20px 10px',
    'background-color': '#263246'
}

# the style arguments for the main content page.
CONTENT_STYLE = {
    'margin-left': '25%',
    'margin-right': '5%',
    'padding': '20px 10p'
}

TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#FFF'
}

CONTENT_TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#263246'
}

CARD_TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#0074D9',
    
}

UPLOAD_STYLE = {
    'width': '100%',
    'height': '60px',
    'lineHeight': '60px',
    'borderWidth': '2px',
    'borderStyle': 'dashed',
    'borderRadius': '7px',
    'textAlign': 'center',
    'color': '#FFF'
}

IMG_STYLE = {
    'max-width': '100%',
    'max-height': '100%',
}

ITEM_STYLE = {
    'whiteSpace': 'pre-wrap',
    'wordBreak': 'break-all',
    'background-color': '#263246',
    'borderWidth': '2px',
    'borderRadius': '7px',
    'textAlign': 'center',
}

########################## FORMATO DEL JSON A VALIDAR ##########################################
schema = {
  "$schema": "dinaRead",
  "type": "object",
  "properties": {
    "id": {
      "type": "integer"
    },
    "muestras": {
      "type": "integer"
    },
    "data": {
      "type": "string"
    }
  },
  "required": [
    "id",
    "muestras",
    "data"
  ]
}
