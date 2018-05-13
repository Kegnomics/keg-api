import json

from matplotlib import pyplot as  plt
import numpy as np

def trigger_airflow_job(conf, dag_name='annotation_job'):
    import subprocess
    json_conf = json.dumps(conf)
    subprocess.call(['airflow', 'trigger_dag', '-c', json_conf, dag_name])
    return 'done'


def plot_pca_graph(merged_df, emb_col='emb_sentence', label_col='label', samples=15, figsize=(30, 30), fontsize=25,
                   colors={0: 'blue', 1: 'red', 99: 'blue', 2: 'black'}):
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
    plt.show()

