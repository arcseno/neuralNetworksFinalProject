# Análise da Olist com autoencoder
# Gera o arquivo resultados_olist.json, que a apresentação em Manim lê.
#
# Pra rodar: python src/analise_olist.py
# Os CSVs da Olist precisam estar na pasta olist_data/ do projeto.

import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore", category=ConvergenceWarning)

PASTA_SCRIPT = Path(__file__).parent
PASTA_DADOS = PASTA_SCRIPT.parent / "olist_data"
if not PASTA_DADOS.exists():
    PASTA_DADOS = PASTA_SCRIPT
SEMENTE = 42


# ---------------------------------------------------------------------
# 1. Ler as tabelas
# ---------------------------------------------------------------------
pedidos = pd.read_csv(PASTA_DADOS / "olist_orders_dataset.csv")
itens = pd.read_csv(PASTA_DADOS / "olist_order_items_dataset.csv")
avaliacoes = pd.read_csv(PASTA_DADOS / "olist_order_reviews_dataset.csv")
pagamentos = pd.read_csv(PASTA_DADOS / "olist_order_payments_dataset.csv")
produtos = pd.read_csv(PASTA_DADOS / "olist_products_dataset.csv")
clientes = pd.read_csv(PASTA_DADOS / "olist_customers_dataset.csv")
vendedores = pd.read_csv(PASTA_DADOS / "olist_sellers_dataset.csv")
geo = pd.read_csv(PASTA_DADOS / "olist_geolocation_dataset.csv")


# ---------------------------------------------------------------------
# 2. Montar uma linha por pedido
# ---------------------------------------------------------------------
# Só pedidos entregues, com data de entrega
pedidos = pedidos[pedidos["order_status"] == "delivered"].copy()
pedidos = pedidos.dropna(subset=["order_delivered_customer_date"])

compra = pd.to_datetime(pedidos["order_purchase_timestamp"])
entrega = pd.to_datetime(pedidos["order_delivered_customer_date"])
estimada = pd.to_datetime(pedidos["order_estimated_delivery_date"])

pedidos["prazo_prometido"] = (estimada - compra).dt.total_seconds() / 86400
pedidos["prazo_real"] = (entrega - compra).dt.total_seconds() / 86400
pedidos["diferenca"] = pedidos["prazo_real"] - pedidos["prazo_prometido"]
pedidos["mes"] = compra.dt.strftime("%Y-%m")

# Peso e volume de cada item vêm da tabela de produtos
produtos["volume"] = produtos["product_length_cm"] * produtos["product_height_cm"] * produtos["product_width_cm"]
itens = itens.merge(produtos[["product_id", "product_weight_g", "volume"]], on="product_id", how="left")

por_pedido = itens.groupby("order_id").agg(
    preco=("price", "sum"),
    frete=("freight_value", "sum"),
    peso=("product_weight_g", "sum"),
    volume=("volume", "sum"),
    seller_id=("seller_id", "first"),
).reset_index()
por_pedido["frete_preco"] = por_pedido["frete"] / por_pedido["preco"]

parcelas = pagamentos.groupby("order_id")["payment_installments"].max().reset_index()
parcelas = parcelas.rename(columns={"payment_installments": "parcelas"})

# Uma nota por pedido (alguns pedidos têm mais de uma avaliação, fica a última)
notas = avaliacoes.drop_duplicates(subset="order_id", keep="last")[["order_id", "review_score"]]
notas = notas.rename(columns={"review_score": "nota"})

# Distância entre cliente e vendedor, usando o centro de cada CEP (5 primeiros dígitos)
geo = geo[(geo["geolocation_lat"] < 6) & (geo["geolocation_lat"] > -34) & (geo["geolocation_lng"] < -34) & (geo["geolocation_lng"] > -74)]
centro_cep = geo.groupby("geolocation_zip_code_prefix")[["geolocation_lat", "geolocation_lng"]].mean()

dados = pedidos.merge(por_pedido, on="order_id")
dados = dados.merge(parcelas, on="order_id")
dados = dados.merge(notas, on="order_id")
dados = dados.merge(clientes[["customer_id", "customer_zip_code_prefix"]], on="customer_id")
dados = dados.merge(vendedores[["seller_id", "seller_zip_code_prefix"]], on="seller_id")
dados = dados.merge(centro_cep, left_on="customer_zip_code_prefix", right_index=True)
dados = dados.rename(columns={"geolocation_lat": "lat_cliente", "geolocation_lng": "lng_cliente"})
dados = dados.merge(centro_cep, left_on="seller_zip_code_prefix", right_index=True)
dados = dados.rename(columns={"geolocation_lat": "lat_vendedor", "geolocation_lng": "lng_vendedor"})

lat1 = np.radians(dados["lat_cliente"])
lat2 = np.radians(dados["lat_vendedor"])
dlat = lat2 - lat1
dlng = np.radians(dados["lng_vendedor"] - dados["lng_cliente"])
a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlng / 2) ** 2
dados["distancia"] = 6371 * 2 * np.arcsin(np.sqrt(a))

COLUNAS = ["prazo_prometido", "prazo_real", "diferenca", "preco", "frete",
           "frete_preco", "peso", "volume", "distancia", "parcelas"]
dados = dados.dropna(subset=COLUNAS + ["nota"]).reset_index(drop=True)
print("Pedidos usados:", len(dados))


# ---------------------------------------------------------------------
# 3. Preparar a entrada da rede
# ---------------------------------------------------------------------
# Preço, frete, peso, volume e distância têm valores muito espalhados,
# então passam por log antes da padronização
entrada = dados[COLUNAS].copy()
entrada["preco"] = np.log1p(entrada["preco"])
entrada["frete"] = np.log1p(entrada["frete"])
entrada["peso"] = np.log1p(entrada["peso"])
entrada["volume"] = np.log1p(entrada["volume"])
entrada["distancia"] = np.log1p(entrada["distancia"])

# Treino só com pedidos bem avaliados (nota 4 ou 5)
normais = entrada[dados["nota"] >= 4]
treino, validacao = train_test_split(normais, test_size=0.2, random_state=SEMENTE)

escala = StandardScaler()
escala.fit(treino)
X_treino = escala.transform(treino)
X_validacao = escala.transform(validacao)
X_todos = escala.transform(entrada)


def erro_por_pedido(modelo, X):
    reconstruido = modelo.predict(X)
    return np.mean((X - reconstruido) ** 2, axis=1)


# ---------------------------------------------------------------------
# 4. Autoencoder principal: 10 -> 8 -> 2 -> 8 -> 10
# (gargalo 2 foi o que melhor separou na varredura da parte 7)
# ---------------------------------------------------------------------
autoencoder = MLPRegressor(hidden_layer_sizes=(8, 2, 8), activation="relu", solver="adam",
                           learning_rate_init=0.001, batch_size=256, random_state=SEMENTE)
EPOCAS = 40
curva_treino = []
curva_validacao = []
for epoca in range(EPOCAS):
    autoencoder.partial_fit(X_treino, X_treino)
    curva_treino.append(float(np.mean(erro_por_pedido(autoencoder, X_treino))))
    curva_validacao.append(float(np.mean(erro_por_pedido(autoencoder, X_validacao))))
print("Erro de treino no fim:", round(curva_treino[-1], 3), "| validação:", round(curva_validacao[-1], 3))

dados["erro"] = erro_por_pedido(autoencoder, X_todos)

# Limite τ: percentil 99 do erro nos pedidos de treino
tau = float(np.percentile(erro_por_pedido(autoencoder, X_treino), 99))
dados["alerta"] = dados["erro"] > tau
print("τ =", round(tau, 3), "| alertas:", int(dados["alerta"].sum()), "de", len(dados))


# ---------------------------------------------------------------------
# 5. Conferência com as notas
# ---------------------------------------------------------------------
nota1 = dados["nota"] == 1
pct_nota1_geral = float(100 * nota1.mean())
pct_nota1_alertas = float(100 * nota1[dados["alerta"]].mean())
pct_nota1_sem_alerta = float(100 * nota1[~dados["alerta"]].mean())
auc_nota1 = float(roc_auc_score(nota1, dados["erro"]))

# Quanto dos alertas vem de pedido atrasado
atrasado = dados["diferenca"] > 0
pct_atraso_geral = float(100 * atrasado.mean())
pct_atraso_alertas = float(100 * atrasado[dados["alerta"]].mean())
pct_nota1_alertas_sem_atraso = float(100 * nota1[dados["alerta"] & ~atrasado].mean())
print("% atrasados geral:", round(pct_atraso_geral, 1), "| nos alertas:", round(pct_atraso_alertas, 1),
      "| nota 1 nos alertas sem atraso:", round(pct_nota1_alertas_sem_atraso, 1))
print("% nota 1 geral:", round(pct_nota1_geral, 1), "| nos alertas:", round(pct_nota1_alertas, 1), "| AUC:", round(auc_nota1, 3))


# ---------------------------------------------------------------------
# 6. Alertas por mês (jan/2017 a ago/2018)
# ---------------------------------------------------------------------
periodo = dados[(dados["mes"] >= "2017-01") & (dados["mes"] <= "2018-08")]
por_mes = periodo.groupby("mes")["alerta"].mean() * 100
meses = list(por_mes.index)
pct_alerta_mes = [float(v) for v in por_mes.values]
# Pra comparar, a % de pedidos que chegaram atrasados em cada mês
atraso_mes = periodo.groupby("mes")["diferenca"].apply(lambda d: (d > 0).mean() * 100)
pct_atraso_mes = [float(v) for v in atraso_mes.values]
print("Alertas por mês (%):")
print(por_mes.round(2).to_string())


# ---------------------------------------------------------------------
# 7. Varredura do gargalo: 10 -> k -> 10
# ---------------------------------------------------------------------
gargalos = [1, 2, 3, 5, 8, 12]
erro_normais_por_gargalo = []
erro_nota1_por_gargalo = []
auc_por_gargalo = []
X_nota1 = X_todos[nota1.values]
for k in gargalos:
    modelo = MLPRegressor(hidden_layer_sizes=(k,), activation="relu", solver="adam",
                          learning_rate_init=0.001, batch_size=256, max_iter=40, random_state=SEMENTE)
    modelo.fit(X_treino, X_treino)
    erro_val = erro_por_pedido(modelo, X_validacao)
    erro_n1 = erro_por_pedido(modelo, X_nota1)
    erro_tudo = erro_por_pedido(modelo, X_todos)
    erro_normais_por_gargalo.append(float(np.mean(erro_val)))
    erro_nota1_por_gargalo.append(float(np.mean(erro_n1)))
    auc_por_gargalo.append(float(roc_auc_score(nota1, erro_tudo)))
    print("gargalo", k, "| erro normais", round(erro_normais_por_gargalo[-1], 3),
          "| erro nota 1", round(erro_nota1_por_gargalo[-1], 3), "| AUC", round(auc_por_gargalo[-1], 3))


# ---------------------------------------------------------------------
# 8. Overfitting de verdade: rede grande prevendo o frete com só 80 pedidos
# ---------------------------------------------------------------------
# Entradas: distância, peso, volume e preço (já padronizados). Saída: log do frete.
X_frete = X_todos[:, [8, 6, 7, 3]]
y_frete = np.log1p(dados["frete"].values)
ordem = np.random.RandomState(0).permutation(len(X_frete))
poucos = ordem[:80]
outros = ordem[1000:6000]

grande = MLPRegressor(hidden_layer_sizes=(128, 128), activation="relu", solver="adam",
                      learning_rate_init=0.003, batch_size=16, random_state=0)
over_treino = []
over_validacao = []
for epoca in range(300):
    grande.partial_fit(X_frete[poucos], y_frete[poucos])
    over_treino.append(float(np.mean((grande.predict(X_frete[poucos]) - y_frete[poucos]) ** 2)))
    over_validacao.append(float(np.mean((grande.predict(X_frete[outros]) - y_frete[outros]) ** 2)))
melhor_epoca = int(np.argmin(over_validacao)) + 1
print("Overfitting: melhor época", melhor_epoca, "| validação mínima", round(min(over_validacao), 3),
      "| validação no fim", round(over_validacao[-1], 3), "| treino no fim", round(over_treino[-1], 3))


# ---------------------------------------------------------------------
# 9. Pedido típico e pedidos mais estranhos
# ---------------------------------------------------------------------
def resumo_pedido(linha):
    return {
        "prazo_prometido": round(float(linha["prazo_prometido"])),
        "prazo_real": round(float(linha["prazo_real"])),
        "diferenca": round(float(linha["diferenca"])),
        "preco": round(float(linha["preco"]), 2),
        "frete": round(float(linha["frete"]), 2),
        "frete_preco": round(float(linha["frete_preco"]), 2),
        "peso": round(float(linha["peso"])),
        "volume": round(float(linha["volume"])),
        "distancia": round(float(linha["distancia"])),
        "parcelas": int(linha["parcelas"]),
        "nota": int(linha["nota"]),
        "erro": round(float(linha["erro"]), 2),
    }


# Típico: o pedido bem avaliado com erro mais perto da mediana
bons = dados[dados["nota"] >= 4]
mediana = bons["erro"].median()
tipico = bons.loc[(bons["erro"] - mediana).abs().idxmin()]

mais_estranhos = dados.sort_values("erro", ascending=False).head(3)
lista_estranhos = []
for _, linha in mais_estranhos.iterrows():
    lista_estranhos.append(resumo_pedido(linha))



# ---------------------------------------------------------------------
# 10. Salvar tudo
# ---------------------------------------------------------------------
resultados = {
    "n_pedidos": int(len(dados)),
    "n_treino": int(len(treino)),
    "curva_treino": curva_treino,
    "curva_validacao": curva_validacao,
    "tau": tau,
    "n_alertas": int(dados["alerta"].sum()),
    "pct_nota1_geral": pct_nota1_geral,
    "pct_nota1_alertas": pct_nota1_alertas,
    "pct_nota1_sem_alerta": pct_nota1_sem_alerta,
    "auc_nota1": auc_nota1,
    "pct_atraso_geral": pct_atraso_geral,
    "pct_atraso_alertas": pct_atraso_alertas,
    "pct_nota1_alertas_sem_atraso": pct_nota1_alertas_sem_atraso,
    "meses": meses,
    "pct_alerta_mes": pct_alerta_mes,
    "pct_atraso_mes": pct_atraso_mes,
    "gargalos": gargalos,
    "erro_normais_por_gargalo": erro_normais_por_gargalo,
    "erro_nota1_por_gargalo": erro_nota1_por_gargalo,
    "auc_por_gargalo": auc_por_gargalo,
    "over_treino": over_treino,
    "over_validacao": over_validacao,
    "over_melhor_epoca": melhor_epoca,
    "pedido_tipico": resumo_pedido(tipico),
    "mais_estranhos": lista_estranhos,
}
with open(PASTA_SCRIPT / "resultados_olist.json", "w", encoding="utf-8") as arquivo:
    json.dump(resultados, arquivo, ensure_ascii=False, indent=1)
print("Salvo em resultados_olist.json")

# Salva a rede treinada pra usar na demo ao vivo (demo_enganar_rede.ipynb)
joblib.dump({"modelo": autoencoder, "escala": escala, "tau": tau, "colunas": COLUNAS},
            PASTA_SCRIPT / "modelo_olist.joblib")
print("Salvo em modelo_olist.joblib")
