import os.path, os

import frontmatter

from flask import json
from flask.ext.login import current_user

from contextlib import contextmanager
from subprocess import Popen, PIPE


class Repository:

    def __init__(self, name):
        self.name = name

    def path(self, filename=None):
        directory = os.path.join('/var/www/jekylledit', self.name)
        if filename is None:
            return directory
        return os.path.join(directory, filename)

    def open(self, filename, mode):
        # Python in Docker has ASCII as default encoding.
        return open(self.path(filename), mode, encoding='utf-8')

    @contextmanager
    def transaction(self):
        head = self.execute(['rev-parse', '--verify', '-q', 'HEAD']).strip()
        try:
            yield self
        except:
            self.execute(['reset', '--hard', head])
            raise

    def execute(self, args):
        cmd = [
            'git',
            '--git-dir={}'.format(self.path('.git')),
            '--work-tree={}'.format(self.path()),
            '-c', 'user.email={}'.format(current_user.email),
        ]
        cmd.extend(args)
        proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        if proc.returncode != 0:
            raise Exception(err)
        return out


class Sites:

    def __init__(self, name):
        self.name = name
        self.repository = Repository(name)

    def get_config(self, filename = None):
        if filename is None:
            filename = 'jekylledit.json'
        with self.repository.open(filename, 'r') as fp:
            self.config = json.load(fp)
            if not 'languages' in self.config:
                self.config.update({'languages': ['en']})
            return self.config

    def get_drafts(self, category=None):
        drafts = []
        directory = self.repository.path(category)
        files = os.listdir(directory)
        for f in files:
            filename = os.path.join(directory, f)
            with self.repository.open(filename, 'r') as fp:
                post = frontmatter.load(fp)
                if 'published' in post.metadata \
                and post.metadata['published'] is False:
                    drafts.append({
                        'author': post.metadata['author'],
                        'category': category,
                        'date' : post.metadata['date'],
                        'filename': os.path.join(category, f),
                        'title': post.metadata['title']
                    })
        return drafts