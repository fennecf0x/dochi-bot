import base64

def png_to_base64(path: str) ->str:
    return "data:image/png;base64," + base64.b64encode(open(path, "rb").read()).decode('utf-8')
