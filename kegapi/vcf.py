import requests
import json


class VcfApi(object):

    def __init__(self, base_url='http://35.185.51.127:8080'):
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

    @staticmethod
    def filter(variants):
        for i in range(len(variants["data"]) - 1, -1, -1):
            exonicFunc = variants["data"][i].get("info").get("ExonicFunc.refGene")
            if exonicFunc and str(exonicFunc) == "synonymous_SNV":
                del variants["data"][i]
                continue

            frequency = variants["data"][i].get("info").get("ExAC_ALL")
            if frequency and float(frequency) > 0.01:
                del variants["data"][i]
                continue

            fathmm_score = variants["data"][i].get("info").get("FATHMM_score")
            if fathmm_score and float(fathmm_score) > 1:
                del variants["data"][i]
                continue

            gerp_score = variants["data"][i].get("info").get("GERP++_RS")
            if gerp_score and float(gerp_score) < 0:
                del variants["data"][i]
                continue

        return variants


if __name__ == '__main__':
    from pprint import pprint

    vcf_api = VcfApi()
    results = vcf_api.upload_file('/home/sushii/Desktop/P22_S10.vcf')
    print("Variants before filtering: " + str(len(results["data"])))

    obj = open('/home/sushii/Desktop/unfilteredVariants.json', 'wb')
    obj.write(json.dumps(results))
    obj.close()


    filteredResults = vcf_api.filter(results)
    print("Variants after filtering: " + str(len(filteredResults["data"])))

    obj = open('/home/sushii/Desktop/filteredVariants.json', 'wb')
    obj.write(json.dumps(filteredResults))
    obj.close()
