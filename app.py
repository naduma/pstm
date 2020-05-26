import os
import string

from bottle import Bottle, run, auth_basic, redirect, request, response

app = Bottle()

cache = {
    'text': '',
    'filename': '',
    'file': None,
}

text_template = string.Template('''
<html>
<head>
  <meta charset="UTF-8">
  <title>pstm</title>
</head>
<body>
  <h1>private short-term memory</h1>
  <ul style="margin:0;padding:0;">
    <li style="display:inline;font-size:large;">Text</li>
    <li style="display:inline;margin-left:1rem;"><a href="/file">File</a></li>
  </ul>
  <form action="/text" method="post" enctype="multipart/form-data">
    <p><textarea name="t" rows="6" cols="60">${text}</textarea></p>
    <p><input type="submit"></p>
  </form>
</body>
</html>
''')

file_template = string.Template('''
<html>
<head>
  <meta charset="UTF-8">
  <title>pstm</title>
</head>
<body>
  <h1>private short-term memory</h1>
  <ul style="margin:0;padding:0;">
    <li style="display:inline;margin-right:1rem;"><a href="/text">Text</a></li>
    <li style="display:inline;font-size:large;">File</li>
  </ul>
  <form action="/file" method="post" enctype="multipart/form-data">
    ${file_download}
    <p><input type="file" name="f"></p>
    <p><input type="submit"></p>
  </form>
</body>
</html>
''')

credentials = {
    'username': os.environ.get('USERNAME', ''),
    'password': os.environ.get('PASSWORD', '')
}


def check(username, password):
    return username == credentials['username'] and password == credentials['password']


@app.route('/', method='GET')
@app.route('/text', method='GET')
@auth_basic(check)
def restore_text():
    return text_template.substitute({
        'text': cache['text'],
    })

@app.route('/text', method='POST')
@auth_basic(check)
def store_text():
    global cache
    cache['text'] = request.forms.get('t')
    redirect('/text')


@app.route('/file', method='GET')
@auth_basic(check)
def restore_file():
    file_download = ''
    if cache['file'] is not None:
        filename = cache['filename']
        file_download = f'<p>File: <a href="/download">{filename}</a></p>'
    else:
        file_download = '<p>File: none</p>'
    return file_template.substitute({
        'file_download': file_download,
    })

@app.route('/file', method='POST')
@auth_basic(check)
def store_file():
    global cache
    f = request.files.get('f')
    if f is not None:
        cache['filename'] = f.raw_filename
        cache['file'] = f.file.read()
    else:
        cache['filename'] = ''
        cache['file'] = None
    redirect('/file')


@app.route('/download', method='GET')
def donwload_file():
    response.content_type = 'application/octet-stream'
    filename = cache['filename']
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    return cache['file']


if __name__ == '__main__':
    run(app, server="waitress", host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
