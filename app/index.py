import codecs
import os
import re

import bottle
import bottle as app
from bottle import static_file
import misaka as m
import pystache

STATIC_PATH = os.path.abspath(
  os.path.join(os.path.abspath(__file__), '../../assets')
)
NOTES_PATH = os.path.abspath(
  os.path.join(os.path.abspath(__file__), '../../notes')
)
TEMPLATE_PATH = os.path.abspath(
  os.path.join(os.path.abspath(__file__),'../../html')
)

loader = pystache.loader.Loader(search_dirs=[TEMPLATE_PATH], extension='html')
renderer = pystache.renderer.Renderer(
  search_dirs=[TEMPLATE_PATH],
  file_extension='html',
  file_encoding='utf8'
)

def render(filename, template, edit=False):
  filename = filename.replace('.', '') # remove periods
  filename = filename.replace(' ', '-')
  filepath = os.path.join(NOTES_PATH, '%s.md' % (filename, ))

  if not os.path.exists(filepath):
    if edit:
      note = ''
    else:
      bottle.redirect('/edit/%s' % (filename, ))
  else:
    with codecs.open(filepath, 'r', 'utf8') as file_obj:
      note = file_obj.read()



  def replacement(match):
     match_str =  match.groups()[0]
     replace_match = match_str.replace(' ', '-')

     replace_match = replace_match.replace('.', '')
     return "<a href='/notes/%s'>%s</a>" % (replace_match, match_str)

  if not edit:
   note = re.sub(
      r'\[\[([A-Z \.a-z0-9]+)\]\]',
      replacement,
      m.html(note)
    )

  return pystache.render(loader.load_name(template), {
    'title': ' '.join(x.capitalize() for x in filename.split('-')),
    'filename': filename,
    'content': note
  })

@app.route('/')
def route_home():
  bottle.redirect('/notes/index')

@app.route('/assets/<path:path>')
def serve_static(path):
  return static_file(path, root=STATIC_PATH)


@app.route('/notes/<filename>')
def render_note(filename):
  return render(filename, 'entry')


@app.route('/edit/<filename>')
def render_note(filename):
  return render(filename, 'entry-edit', edit=True)


@app.route('/edit/<filename>', method='POST')
def handle_note_post(filename):
  data = bottle.request.forms.get('string')

  #import pdb;pdb.set_trace()

  with codecs.open(os.path.join(NOTES_PATH, '%s.md' % (filename, )), 'w', 'utf8') as file_obj:
    file_obj.write(data)
  return {'success': True}


webapp = bottle.default_app()
