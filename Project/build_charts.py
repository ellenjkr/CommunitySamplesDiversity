import pandas as pd
import matplotlib.pyplot as plt



def phylum_chart(file):
    df = pd.read_csv(file, sep='\t')
    df = df.groupby('Filo').sum().reset_index()
    for col in df.columns:
        if col != "Filo":
            soma = df[col].sum()
            df[col] = (df[col] / soma) * 100

    amostras = df.iloc[:, 1:]
    amostras = amostras.T


    #plt.style.use('ggplot')

    ax = amostras.plot.bar(stacked=True)

    plt.xlabel('Amostras')
    plt.ylabel('%')
    plt.title('Filo')

    plt.xticks(range(len(amostras)), amostras.index)

    handles, labels = ax.get_legend_handles_labels()


    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    ax.legend(handles, df['Filo'], title='Filo', loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xticks(rotation=45, ha='right')

    plt.subplots_adjust(bottom=0.25, right=0.8, top=0.8)
    plt.show()


def meta_charts(file, meta_file):
    samples_df = pd.read_csv(file, sep='\t')
    samples_df = samples_df.groupby('Filo').sum().reset_index()

    meta = pd.read_csv('meta_v5.tsv', sep='\t')

    for category in meta[meta.columns[1:]]:
        df_values_melted = samples_df.melt(id_vars='Filo', var_name='sample', value_name='valor')
        df_merged = pd.merge(df_values_melted, meta, on='sample')
        df = df_merged.pivot_table(index='Filo', columns=category, values='valor', aggfunc='sum').reset_index()
        print(df)
        for col in df.columns:
            if col != "Filo":
                soma = df[col].sum()
                df[col] = (df[col] / soma) * 100




        amostras = df.iloc[:, 1:]
        amostras = amostras.T


        #plt.style.use('ggplot')

        ax = amostras.plot.bar(stacked=True)

        plt.xlabel(category.capitalize())
        plt.ylabel('%')
        plt.title('Filo')

        plt.xticks(range(len(amostras)), amostras.index)

        handles, labels = ax.get_legend_handles_labels()


        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        ax.legend(handles, df['Filo'], title='Filo', loc='center left', bbox_to_anchor=(1, 0.5))
        plt.xticks(rotation=45, ha='right')

        plt.subplots_adjust(bottom=0.25, right=0.8, top=0.8)
        plt.show()


phylum_chart('lib3_stamp.tsv')
meta_charts('lib3_stamp.tsv', 'meta_v5.tsv')
