from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from sklearn.model_selection import train_test_split
import pickle
import pandas as pd
import pickle
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from sklearn.model_selection import train_test_split

from kegapi.vcf import VcfApi

ALL_COLS = {'ExAC_ALL', 'integrated_fitCons_score', 'PROVEAN_score', 'SiPhy_29way_logOdds', 'AC', 'AF', 'FATHMM_score',
            'ExAC_SAS', 'MQRankSum', 'MutationTaster_score', 'HRun', 'GQ', 'ExAC_FIN', 'MetaLR_score', 'GQX',
            'phastCons7way_vertebrate', 'FS', 'phyloP20way_mammalian', 'GERP++_RS',
            'CADD_raw', 'CADD_phred', 'AN', 'MutationAssessor_score', 'ExAC_OTH', 'DP', 'VF', 'ExAC_AFR',
            'phyloP7way_vertebrate', 'ExAC_AMR', 'ExAC_EAS', 'BaseQRankSum', 'Polyphen2_HVAR_score', 'ReadPosRankSum',
            'fathmm-MKL_coding_score', 'MetaSVM_score', 'ExAC_NFE', 'HaplotypeScore', 'SIFT_score',
            'phastCons20way_mammalian', 'MQ', 'VEST3_score', 'QD', 'Polyphen2_HDIV_score', 'LRT_score', 'DANN_score',
            'SB'}


def _get_col_value_or_0(d, col):
    num = 0
    try:
        value = d.get(col)
        num = float(value)
    except Exception:
        pass
    return num


def extract_numeric_fields(vcf_data):
    final_rows = []
    row_info = [row['info'] for row in vcf_data['data']]
    for inf in row_info:
        final_rows.append({col: _get_col_value_or_0(inf, col) for col in ALL_COLS})

    return final_rows


def flat_parse(itemset):
    """
    Flattens a list of lists
    """
    return [item for sublist in itemset for item in sublist]


def load_pickle(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot as  plt
import numpy as np


def plot_pca_graph(merged_df, emb_col='emb_sentence', label_col='label', samples=15, figsize=(10, 10), fontsize=15,
                   colors={0: 'blue', 1: 'red', 99: 'blue', 2: 'black'}, output_path='out.jpg'):
    """
    Get the PCA plot for a dataframe with averaged or summed embeddings of each sentence
        :param df: The dataframe to parse
        :param emb_col: The column that holds the embedding representation
        :param label_col: The column holding the label of the class
        :param samples: How many random samples to take from the dataset
        :param figsize: The size of the figure to plot
        :param fontsize: The size of the font for the graph
        :param colors (dict): The colors to use when plotting the classes
    """

    df = merged_df.as_matrix()[:, :-1]
    labels = merged_df.as_matrix()[:, -1]
    pca = PCA(n_components=2)
    pca_comp = pca.fit(df.T).components_
    idxs = np.random.choice(len(df), samples, replace=False)
    x = pca_comp[0][idxs]
    y = pca_comp[1][idxs]
    plt.figure(figsize=figsize)
    plt.scatter(x, y)
    for i, x, y in zip(idxs, x, y):
        text = str(labels[i])
        if labels[i] == '1':
            text = 'malign!'
        plt.text(x, y, text, color=colors[int(labels[i])], fontsize=fontsize)
    plt.savefig(output_path)


def build_dataframes(files, out_path):
    vcf_api = VcfApi()
    parsed_vcfs = [vcf_api.upload_file(file) for file in files]

    import copy
    parsed_vcfs_backup = copy.deepcopy(parsed_vcfs)
    filtered_vcfs = [VcfApi.filter(vcf_file) for vcf_file in parsed_vcfs]

    extracted_parsed_vcfs = [extract_numeric_fields(vcf) for vcf in parsed_vcfs_backup]
    extracted_filtered_vcfs = [extract_numeric_fields(vcf) for vcf in filtered_vcfs]

    print('Extracted: ')

    # with open('parsed_vcfs_ml.p', 'wb') as f:
    #     pickle.dump(extracted_parsed_vcfs, f)
    # with open('filtered_parsed_vcfs_ml.p', 'wb') as f:
    #     pickle.dump(extracted_filtered_vcfs, f)

    filtered_flat_parsed = flat_parse(extracted_filtered_vcfs)
    flat_parsed = flat_parse(extracted_parsed_vcfs)
    filtered_df = pd.DataFrame.from_dict(filtered_flat_parsed)
    normal_df = pd.DataFrame.from_dict(flat_parsed)

    normal_df.set_value(normal_df.index, 'label', '0')
    filtered_df.set_value(filtered_df.index, 'label', '1')

    merged_df = pd.concat([normal_df, filtered_df])
    with open('/home/cristi/Documents/hacktm/df.p', 'wb') as f:
        pickle.dump(merged_df, f)

    plot_pca_graph(merged_df, samples=len(merged_df), output_path=out_path)
    return merged_df


if __name__ == '__main__':
    build_dataframes(
        [
            # '/home/cristi/Documents/hacktm/J2_S2.vcf',
            '/home/cristi/Documents/hacktm/J3_S3.vcf',
            # '/home/cristi/Documents/hacktm/J4_S4.vcf'
        ],
        out_path='/home/cristi/Documents/hacktm/pca_graph.png'
    )
