import json

from kegapi.app import db


class JobRun(db.Model):
    __tablename__ = 'jobrun'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    done = db.Column(db.Integer, nullable=False)
    variants = db.relationship('Variant',
                               backref=db.backref('pubmedarticles', lazy=True))
    pubmedarticles = db.relationship('PubMedArticle',
                                     backref=db.backref('variant', lazy=True))

    @staticmethod
    def serialize_json(obj):
        return {
            'id': obj.id,
            'user_id': obj.user_id,
            'timestamp': obj.timestamp,
            'done': obj.done,
            'variants': [Variant.serialize_json(v) for v in obj.variants],
            'pubmedarticles': [PubMedArticle.serialize_json(a) for a in obj.pubmedarticles]
        }


class Variant(db.Model):
    __tablename__ = 'variant'
    id = db.Column(db.Integer, primary_key=True)
    rsid = db.Column(db.String(500), nullable=True)

    locus = db.Column(db.String(500))
    outcome = db.Column(db.String(500))
    phenotype = db.Column(db.String(500))
    frequency = db.Column(db.Integer)
    polyphene = db.Column(db.Float)
    sift = db.Column(db.Float)

    run_id = db.Column(db.Integer, db.ForeignKey('jobrun.id'),
                       nullable=False)

    @staticmethod
    def serialize_json(obj):
        return {
            'id': obj.id,
            'rsid': obj.rsid,
            'locus': obj.locus,
            'outcome': obj.outcome,
            'phenotype': obj.phenotype,
            'polyphen': obj.polyphene,
            'sift': obj.sift
        }


class PubMedArticle(db.Model):
    __tablename__ = 'pubmedarticle'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500))
    summary = db.Column(db.Text)

    run_id = db.Column(db.Integer, db.ForeignKey('jobrun.id'),
                       nullable=False)

    def __repr__(self):
        return '<PubMedArticle {}>'.format(self.url)

    @staticmethod
    def serialize_json(obj):
        return {
            'id': obj.id,
            'url': obj.url,
            'summary': json.loads(obj.summary)
        }


def populate_pubmed_data(job, pubmed_data):
    for data in pubmed_data:
        summary_str = json.dumps(data['summary'])
        url = data['url']
        db.session.add(PubMedArticle(
            run_id=job.id,
            summary=summary_str,
            url=url
        ))
    db.session.commit()


def populate_variant_data(job, variant_data):
    for data in variant_data['data']:
        db.session.add(
            Variant(
                run_id=job.id,
                sift=data.get('SIFT_score')
            )
        )
    db.session.commit()


if __name__ == '__main__':
    db.create_all()
