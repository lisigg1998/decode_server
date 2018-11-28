from app_decode import db

class User(db.Model):
    real_id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.String(255), unique=True, nullable=False)
    tokens = db.relationship('Token', backref='user', lazy=True, uselist=False)

    def __repr__(self):
        return '<User {}>'.format(self.real_id)


class Token(db.Model):
    user_id = db.Column(db.String(255), db.ForeignKey('user.user_id'), primary_key=True)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expiration = db.Column(db.DateTime, nullable=False)

    def _repr_(self):
        return '<Token {} for User {}>'.format(self.token, self.user_id)


class Admin(db.Model):
    username = db.Column(db.String(255), primary_key=True)
    password_hash = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<Admin {}>'.format(self.username)


class DecodeUser(db.Model):
    username = db.Column(db.String(255), primary_key=True)
    password_hash = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<Decode user {}>'.format(self.username)


class EmailSettings(db.Model):
    pri_key = db.Column(db.Integer, primary_key=True)
    email_address_regex = db.Column(db.String(255), nullable=False)
    smtp_host = db.Column(db.String(255), nullable=False)
    smtp_port = db.Column(db.Integer(), nullable=False)
    use_ssl = db.Column(db.Boolean(), nullable=False)
    sender_address = db.Column(db.String(255), nullable=False)
    test_receiver = db.Column(db.String(255), nullable=False)
    supervisor_address = db.Column(db.String(255), nullable=False)

