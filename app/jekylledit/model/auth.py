from flask_login import UserMixin

from .base import JSON, db


class Site(db.Model):

    __tablename__ = 'site'

    id = db.Column(db.Unicode, primary_key=True)
    mtime = db.Column(db.Integer, nullable=False)
    gitkit_options = db.Column(JSON)


class Account(UserMixin, db.Model):

    __tablename__ = 'account'

    id = db.Column(db.Unicode, primary_key=True)
    email = db.Column(db.Unicode, unique=True, nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    name = db.Column(db.Unicode)
    photo_url = db.Column(db.Unicode)

    roles = db.relationship('Roles')


class Roles(db.Model):

    __tablename__ = 'roles'

    email = db.Column(db.Unicode, db.ForeignKey('account.email'), primary_key=True)
    site_id = db.Column(db.Unicode, db.ForeignKey('site.id'), primary_key=True, index=True)
    roles = db.Column(JSON, nullable=False)


class OobAction(db.Model):

    __tablename__ = 'oob_action'

    oob_code = db.Column(db.Unicode, primary_key=True)
    site_id = db.Column(db.Unicode, db.ForeignKey('site.id'), nullable=False)
    moment = db.Column(db.DateTime, nullable=False)
