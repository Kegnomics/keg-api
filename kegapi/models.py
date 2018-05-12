from kegapi import db


class JobRun(db.Model):
    __tablename__ = 'jobrun'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    variants = db.relationship('Variant',
                               backref=db.backref('pubmedarticles', lazy=True))
    pubmedarticles = db.relationship('PubMedArticle',
                                     backref=db.backref('variant', lazy=True))


class Variant(db.Model):
    __tablename__ = 'variant'
    id = db.Column(db.Integer, primary_key=True)
    rsid = db.Column(db.Integer, nullable=True)

    locus = db.Column(db.String(500))
    outcome = db.Column(db.String(500))
    phenotype = db.Column(db.String(500))
    frequency = db.Column(db.Integer)
    polyphene = db.Column(db.Float)
    sift = db.Column(db.Float)

    run_id = db.Column(db.Integer, db.ForeignKey('jobrun.id'),
                       nullable=False)


class PubMedArticle(db.Model):
    __tablename__ = 'pubmedarticle'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500))
    summary = db.Column(db.Text)

    run_id = db.Column(db.Integer, db.ForeignKey('jobrun.id'),
                       nullable=False)

    def __repr__(self):
        return '<PubMedArticle {}>'.format(self.url)


if __name__ == '__main__':
    db.create_all()
