from flask import render_template, json, jsonify, request
from flask.ext.login import login_required
from base64 import b64decode
import frontmatter
from subprocess import call

from .base import app, admin_role


SITES_FOLDER = '/var/www/jekyledit'
JE_CONFIG_NAME = 'jekylledit.json'


def commit(repository, filename):
    try:
        gitdir = SITES_FOLDER + repository + '/'
        call(['git', '--git-dir=' + gitdir + '.git', '--work-tree=' + gitdir, 'add', filename])
        call(['git', '--git-dir=' + gitdir + '.git', '--work-tree=' + gitdir, 'commit', '-m', 'File ' + filename + 'updated'])
      # call(['git', '--git-dir=' + gitdir + '.git', '--work-tree=' + gitdir, 'push'])
        return True
    except:
        return False


@app.route('/')
def index():
    return render_template('index.html')


#site config response
@app.route('/site/<string:site_id>/config')
def site_config(site_id):

    f = open(SITES_FOLDER + '/' + site_id + '/' + JE_CONFIG_NAME, 'r')
    config = json.loads(f.read())
    # TODO: Validate
    return jsonify(config)


# Handle working with posts
@app.route('/site/<string:site_id>/<string:file_id>', methods = ['GET', 'POST', 'PUT'])
def site_get(site_id, file_id):
    filename = b64decode(file_id).decode()

    # Save new post
    if request.method == 'POST':
        data = request.json
        post = frontmatter.loads()

        if 'metadata' in data:
            post.metadata = data['metadata']
        if 'content' in data:
            post.content = data['content']

        file = open(SITES_FOLDER + '/' + site_id + '/' + filename, 'r+b')
        file.write(frontmatter.dumps(post))
        file.close()
        resp = {'status': status, 'site': site_id, 'file': filename}
        return jsonify(resp)

    # Save content of post to file
    elif request.method == 'PUT':
        data = request.json

        if data != None:
            # Save post data to file
            file = open(SITES_FOLDER + '/' + site_id + '/' + filename, 'r+b')
            post = frontmatter.loads(file.read())
            file.seek(0)
            file.truncate()

            if 'metadata' in data:
                post.metadata = data['metadata']
            if 'content' in data:
                post.content = data['content']

            file.write(frontmatter.dumps(post))
            file.close()

            # Commit changes
            commited = commit(site_id, filename)
            if commited:
                status = 'ok'
            else:
                status = 'failed'
        else:
            status = 'failed'
        resp = {'status': status, 'site': site_id, 'file': filename}
        return jsonify(resp)

    # Return post's attributes
    else:
        file = open(SITES_FOLDER + '/' + site_id + '/' + filename, 'r', encoding='utf-8')
        fm = frontmatter.loads(file.read())
        resp = {'metadata': fm.metadata}
        return jsonify(resp)


@app.route('/private')
@login_required
def private():
    return render_template('private.html')


@app.route('/admin')
@login_required
@admin_role.require()
def admin():
    return render_template('admin.html')