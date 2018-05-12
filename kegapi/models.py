import json

import re
from kegapi.app import db
from kegapi.constants import CLINVAR_GROUP_REGEX


class JobRun(db.Model):
    __tablename__ = 'jobrun'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    done = db.Column(db.Integer, nullable=False)
    runname = db.Column(db.String(500))
    variants = db.relationship('Variant',
                               backref=db.backref('pubmedarticles', lazy=True))
    pubmedarticles = db.relationship('PubMedArticle',
                                     backref=db.backref('variant', lazy=True))

    @staticmethod
    def serialize_json(obj):
        return {
            'id': obj.id,
            'runname': obj.runname,
            'user_id': obj.user_id,
            'timestamp': obj.timestamp,
            'done': obj.done,
            'variants': [Variant.serialize_json(v) for v in obj.variants],
            'pubmedarticles': [PubMedArticle.serialize_json(a) for a in obj.pubmedarticles]
        }


class Variant(db.Model):
    __tablename__ = 'variant'
    id = db.Column(db.Integer, primary_key=True)
    rsid = db.Column(db.String(500), nullable=True)  # ID

    locus = db.Column(db.String(500))  # chromosome, position
    outcome = db.Column(db.String(500))  # ?????
    phenotype = db.Column(db.String(500))  # ??????
    frequency = db.Column(db.Integer)  # ExAC_ALL
    polyphene = db.Column(db.Float)  # Polyphene2_....ceva
    sift = db.Column(db.Float)  # SIFT_score

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
    abstract = db.Column(db.Text)

    run_id = db.Column(db.Integer, db.ForeignKey('jobrun.id'),
                       nullable=False)

    def __repr__(self):
        return '<PubMedArticle {}>'.format(self.url)

    @staticmethod
    def serialize_json(obj):
        abstract = obj.abstract if hasattr(obj, 'abstract') else ''
        return {
            'id': obj.id,
            'url': obj.url,
            'summary': json.loads(obj.summary),
            'abstract': abstract
        }


def populate_pubmed_data(job, pubmed_data):
    for data in pubmed_data:
        summary_str = json.dumps(data['summary'])
        url = data['url']
        db.session.add(PubMedArticle(
            run_id=job.id,
            abstract=data['abstract'],
            summary=summary_str,
            url=url
        ))
    db.session.commit()


def extract_clinvar_data(text):
    """
    Get some text, extract clinvar format crap.
    First thing = outcome
    Second thing = fenotype
    :param text: clinvar column text
    :return: a list of matches
    """
    # Left for reference
    # text = 'CLINSIG\\\\x3dprobable-non-pathogenic|non-pathogenic\\\\x3bCLNDBN\\\\x3dCardiomyopathy|' \
    #        'AllHighlyPenetrant\\\\x3bCLNACC\\\\x3dRCV000029674.1|RCV000037982.1'
    # ['CLINSIG', 'x3dpathogenic', 'x3bCLNDBN', 'x3dHypothyroidism', 'x2c_congenital', 'x2c_nongoitrous', 'x2c_5', 'x3bCLNACC', 'x3dRCV000009584.1']

    groups = []
    split_articles = text.split('\\')
    cl_index = -1
    cldb_index = -1
    for article_ind in range(len(split_articles)):
        article = split_articles[article_ind]
        if article.startswith('x'):
            article = article[3:]
        if 'CLINSIG' in article:
            cl_index = article_ind
        if 'CLNDBN' in article:
            cldb_index = article_ind

    outcome = None
    phenotype = None

    if cl_index != -1:
        cl_group = []
        cl_index += 1
        while (not 'CL' in split_articles[cl_index]) and (cl_index < len(split_articles)):
            cl_group.append(split_articles[cl_index][3:])
            cl_index += 1
        outcome = ' '.join(cl_group)

    if cldb_index != -1:
        cl_group = []
        cldb_index += 1
        while (not 'CL' in split_articles[cldb_index]) and (cldb_index < len(split_articles)):
            cl_group.append(split_articles[cldb_index][3:])
            cldb_index += 1
        phenotype = ','.join(cl_group)

    return outcome, phenotype


def populate_variant_data(job, variant_data):
    for data in variant_data['data']:
        clinvar_text = data.get('info').get('clinvar_20140211')
        outcome, phenotype = None, None
        if clinvar_text:
            outcome, phenotype = extract_clinvar_data(clinvar_text)

        locus = None
        if data.get('chromosome') and data.get('position'):
            locus = data.get('chromosome') + ',' + str(data.get('position'))
        db.session.add(
            Variant(
                run_id=job.id,
                rsid=data.get('ID'),
                sift=data.get('info').get('SIFT_score'),
                polyphene=data.get('info').get('Polyphen2_HVAR_score'),
                phenotype=phenotype,
                outcome=outcome,
                locus=locus
            )
        )
    db.session.commit()


if __name__ == '__main__':
    db.create_all()
