import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sns
import glob, os

pasta = "csv_convertidos"
arquivos = glob.glob(os.path.join(pasta, "*.csv"))
resultados = []

for arquivo in arquivos:
    df = pd.read_csv(arquivo)
    df.columns = df.columns.str.strip().str.lower()
    nome = os.path.basename(arquivo).replace(".csv", "")
    tamanho = os.path.getsize(arquivo)

    algoritmo, processos, execucao = nome.split("_")
    processos = int(processos)

    cpu_df = df[df["tipo"] == "CPU"]
    media_cpu = cpu_df["valor"].mean()

    resultados.append({
        "Algoritmo": algoritmo,
        "Processos": processos,
        "Media_CPU": media_cpu,
        "Tamanho": tamanho,
    })

df_resultados = pd.DataFrame(resultados)

df_media = (
    df_resultados
    .groupby(["Algoritmo", "Processos"])["Media_CPU"]
    .mean()
    .reset_index()
)

def ref_group(g):
    menor = g["Media_CPU"].min()
    maior = g["Media_CPU"].max()

    return pd.Series({
        "media_menor": menor,
        "media_maior": maior
    })

df_refs = (
    df_resultados
    .groupby(["Algoritmo", "Processos"])
    .apply(ref_group)
    .reset_index()
)

df_plot = df_media.merge(df_refs, on=["Algoritmo", "Processos"])

algoritmos = sorted(df_plot["Algoritmo"].unique())
processos_vals = sorted(df_plot["Processos"].unique())

n_alg = len(algoritmos)
n_proc = len(processos_vals)
x = np.arange(n_proc)
width = 0.8 / n_alg  

colors = sns.color_palette("muted", n_alg)

fig, ax = plt.subplots(figsize=(12, 6))

for i, alg in enumerate(algoritmos):
    sub = df_plot[df_plot["Algoritmo"] == alg].set_index("Processos")
    offsets = x + (i - n_alg / 2 + 0.5) * width

    heights = [sub.loc[p, "Media_CPU"] if p in sub.index else 0 for p in processos_vals]
    menores = [sub.loc[p, "media_menor"] if p in sub.index else None for p in processos_vals]
    maiores = [sub.loc[p, "media_maior"] if p in sub.index else None for p in processos_vals]

    bars = ax.bar(offsets, heights, width=width * 0.9, color=colors[i], label=alg, edgecolor="black", 
    linewidth=1.2)

    for offset, menor, maior in zip(offsets, menores, maiores):

        if menor is not None and maior is not None:
            ax.vlines(
                x=offset,
                ymin=menor,
                ymax=maior,
                color="black",
                linewidth=2,
                zorder=4
            )

            ax.scatter(
                offset,
                menor,
                color="steelblue",
                s=40,
                zorder=5
            )

            ax.scatter(
                offset,
                maior,
                color="tomato",
                s=40,
                zorder=5
            )

ax.set_xticks(x)
ax.set_xticklabels(processos_vals)
ax.set_xlabel("Número de Processos")
ax.set_ylabel("Tempo Médio CPU")
ax.set_title("Processo CPU-bound")

handles, labels = ax.get_legend_handles_labels()
handles += [
    mpatches.Patch(color="steelblue", label="Média menor arquivo"),
    mpatches.Patch(color="tomato",    label="Média maior arquivo"),
]
ax.legend(handles=handles)

plt.tight_layout()
plt.savefig("grafico_CPU.png", dpi=150)