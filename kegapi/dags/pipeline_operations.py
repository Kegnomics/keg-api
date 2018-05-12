from kegapi.vcf import VcfApi


def annotate_vcf(file_path):

    vcf = VcfApi()
    results = vcf.upload_file(file_path=file_path)
    return results