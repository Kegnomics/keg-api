import requests


class VcfApi(object):

    def __init__(self, base_url='http://10.10.1.33:8080'):
        self.upload_url = base_url + '/handleFileUpload'

    def upload_file(self, file_path):
        """
        Upload the file at the path to the VcfApi URL, getting back the annotated data

        :param file_path: the path to the file
        :return: a json object representing annotated variants from the VCF file
        """
        file_payload = {'file': open(file_path, 'rb')}
        r = requests.post(self.upload_url, files=file_payload)
        return r.json()


if __name__ == '__main__':
    from pprint import pprint
    vcf_api = VcfApi()
    pprint(vcf_api.upload_file('/home/cristi/Documents/Desktop/J2_S2.vcf'))
