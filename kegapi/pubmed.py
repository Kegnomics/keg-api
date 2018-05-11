from urllib.parse import urlencode
import requests
import logging

from kegapi.urlutils import build_uri


def get_json_or_err(response):
    if response.status_code == 200:
        return response.json()
    else:
        logging.error('ERR: ' + response)
        return None


# https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=json&rettype=abstract&id=25081398

class PubMed(object):
    PUBMED_ESUMMARY_API_BASE = build_uri('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi',
                                         is_base=True)
    PUBMED_EFETCH_API_BASE = build_uri('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi',
                                       is_base=True)
    PUBMED_ESEARCH_API_BASE = build_uri('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi',
                                        is_base=True)

    PUBMED_WEB_URL = 'https://www.ncbi.nlm.nih.gov/pubmed/'

    def get_abstract_from_efetch(self, pubmed_id):
        params = {'rettype': 'abstract', 'id': pubmed_id}
        uri = build_uri(self.PUBMED_EFETCH_API_BASE, params)
        response = requests.get(uri)
        return response.text

    def get_summary_from_id(self, pubmed_id):
        params = {'id': pubmed_id}
        uri = build_uri(self.PUBMED_ESUMMARY_API_BASE, params)
        response = requests.get(uri)
        return get_json_or_err(response)['result'][pubmed_id]

    def get_by_keywords(self, keywords, maxres=10):
        """
        Get a list of keywords, search ESEARCH on pubmed, get the articles'

        :param maxres: the number of results to get
        :param keywords: list of keywords
        :return:
        """
        terms_str = ' '.join(keywords)
        uri = build_uri(self.PUBMED_ESEARCH_API_BASE, {
            'retmax': maxres,
            'term': terms_str
        })
        logging.info('Getting: {}'.format(uri))
        json_resp = get_json_or_err(requests.get(uri))
        ids = json_resp['esearchresult']['idlist']
        articles = [{'abstract': self.get_abstract_from_efetch(id), 'summary': self.get_summary_from_id(id)} for id in
                    ids]

        for article in articles:
            article['url'] = build_uri(self.PUBMED_WEB_URL, {'term': article['summary']['uid']}, is_base=True)

        return articles


pubmed_api = PubMed()

#
# if __name__ == '__main__':
#     p = PubMed()
#     import pprint
#     kwds = p.get_by_keywords(['cleft', 'palate'], maxres=2)
#
#     pprint.pprint(kwds)
