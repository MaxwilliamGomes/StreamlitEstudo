"""Amplia a base com histórico sintético (seed fixa). Sempre parte de dados/originais/.
Regras: linhas originais ficam intactas; C001-C012 não recebem pedidos/títulos sintéticos
a partir de 01/07/2026 e têm histórico sem pendências; pedidos em aberto sintéticos não usam
P001-P020. Assim as divergências e rupturas do período original continuam iguais.
Pendências de pagamento antigas só ficam em clientes crônicos; as demais são recentes."""
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
INICIO, FIM_PEDIDOS, FIM_EXTRATO = pd.Timestamp("2025-01-02"), pd.Timestamp("2026-08-23"), pd.Timestamp("2026-09-17")
CORTE_ORIGINAIS = pd.Timestamp("2026-07-01")
INICIO_PENDENCIAS = pd.Timestamp("2026-07-01")
RAIZ = Path(__file__).resolve().parents[1] / "dados"
ORIG = RAIZ / "originais"
r = np.random.default_rng(SEED)


def pick(x):
    return x[int(r.integers(len(x)))]


def sem_acento(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper()


def ler(n):
    return pd.read_csv(ORIG / f"{n}.csv", dtype=str, keep_default_na=False, encoding="utf-8")


cli0, prod0, ped0, tit0, ext0 = (ler(n) for n in ["clientes", "produtos", "pedidos_orcamento", "titulos_receber", "extrato_bancario"])

# ---------- clientes ----------
SEG = {
    "Indústria": (["Metalúrgica", "Usinagem", "Fundição", "Laticínios", "Cerâmica", "Têxtil", "Alimentos"], [28, 30, 45], [5, 5, 10]),
    "Oficina": (["Oficina", "Mecânica", "Retífica"], [0, 7, 14], [0, 0, 3]),
    "Revenda": (["Ferragens", "Autopeças", "Casa do Parafuso", "Distribuidora"], [21, 30], [5, 8]),
    "Construtora": (["Construtora", "Engenharia", "Empreiteira"], [30], [3, 5]),
    "Transporte": (["Transportadora", "Logística", "Expresso"], [14, 21], [3]),
    "Setor público": (["Prefeitura de", "Hospital Municipal de", "Consórcio Intermunicipal de"], [30], [0]),
    "Agronegócio": (["Fazenda", "Cooperativa", "Agropecuária"], [28, 45], [3, 5]),
}
PESO_SEG = [.34, .16, .16, .12, .08, .06, .08]
SOBRE = ("Santa Clara,Vale Verde,Ouro Branco,Nova Aurora,Três Marias,Serra Azul,Pampulha,Bom Jesus,Primavera,Alvorada,"
         "Itatiaia,Rio Doce,Paraopeba,Mantiqueira,São Geraldo,Boa Vista,Cristal,Horizonte Novo,Dois Irmãos,Lagoa Dourada,"
         "Campo Belo,Monte Alto,Pedra Branca,São Lucas,Santa Rita,Vista Alegre,Morro Grande,Jequitibá,Ipê Amarelo,Sol Nascente").split(",")
CID = ("Belo Horizonte,Contagem,Betim,Nova Lima,Sete Lagoas,Ipatinga,Divinópolis,Juiz de Fora,Uberlândia,Montes Claros,"
       "Itabira,Pará de Minas,Sabará,Governador Valadares,Varginha,Poços de Caldas").split(",")
CID_PESO = np.array([9, 8, 8, 3, 4, 3, 4, 3, 3, 2, 2, 2, 2, 2, 2, 2.])
CID_PESO /= CID_PESO.sum()

linhas, usados = [], set(cli0.nome)
for i in range(13, 61):
    seg = str(r.choice(list(SEG), p=PESO_SEG))
    pref, prazos, descs = SEG[seg]
    while True:
        cidade = str(r.choice(CID, p=CID_PESO))
        p_ = pick(pref)
        nome = f"{p_} {cidade}" if seg == "Setor público" else f"{p_} {pick(SOBRE)}"
        if nome not in usados:
            usados.add(nome)
            break
    desde = pd.Timestamp("2009-01-01") + pd.Timedelta(days=int(r.integers(0, 5700)))
    if r.random() < .22:  # clientes conquistados durante o período
        desde = pd.Timestamp("2025-02-01") + pd.Timedelta(days=int(r.integers(0, 480)))
    linhas.append([f"C{i:03d}", nome, cidade, seg, str(pick(prazos)), str(pick(descs)), desde.strftime("%Y-%m-%d")])
clientes = pd.concat([cli0, pd.DataFrame(linhas, columns=cli0.columns)], ignore_index=True)

# ---------- produtos ----------
CAT = {
    "Fixadores": [("Parafuso sextavado", ["1/4 x 1 pol", "5/16 x 1 pol", "5/8 x 3 pol", "3/4 x 4 pol"], 1.4), ("Parafuso francês", ["3/8 x 2 pol", "1/2 x 3 pol", "5/8 x 4 pol"], 2.2), ("Porca sextavada", ["1/4", "1/2", "5/8"], .35), ("Arruela de pressão", ["1/4", "3/8", "1/2"], .18), ("Chumbador", ["1/4 x 2 pol", "1/2 x 4 pol"], 3.1), ("Barra roscada 1 m", ["3/8", "1/2"], 12)],
    "Vedações": [("Anel o-ring NBR", ["20 mm", "30 mm", "80 mm"], 2.5), ("Retentor", ["25x40x7", "30x52x10", "50x72x10", "60x80x8"], 17), ("Fita veda-rosca", ["18 mm x 25 m", "12 mm x 10 m"], 5.5), ("Gaxeta trançada", ["1/4 pol (m)", "3/8 pol (m)"], 16)],
    "Correias": [("Correia em V", ["A-30", "A-55", "B-42", "B-75", "C-90"], 36), ("Correia dentada", ["3M-300", "5M-600", "8M-800"], 68), ("Correia poli-V", ["6PK-1200", "8PK-1500"], 55)],
    "Lubrificantes": [("Óleo hidráulico ISO", ["32 (balde 20 L)", "46 (balde 20 L)"], 175), ("Óleo de engrenagem ISO", ["150 (balde 20 L)", "220 (balde 20 L)"], 215), ("Graxa grafitada", ["1 kg", "5 kg"], 48), ("Spray de silicone", ["300 ml"], 19), ("Fluido de corte", ["5 L", "20 L"], 110)],
    "EPIs": [("Luva nitrílica", ["P", "M", "G"], 12), ("Máscara PFF2", ["sem válvula", "com válvula"], 5), ("Protetor facial", ["incolor"], 34), ("Protetor auricular concha", ["padrão"], 42), ("Cinto de segurança", ["paraquedista"], 240), ("Botina de segurança", ["bico composite", "bico aço"], 118)],
    "Rolamentos": [("Rolamento", ["6201 2RS", "6203 2RS", "6206 2RS", "6305 2RS", "6308 ZZ", "NU 205"], 34), ("Mancal", ["UCP 205", "UCP 208"], 88)],
    "Abrasivos": [("Disco de corte", ["4.1/2 pol", "7 pol", "9 pol"], 9), ("Disco flap", ["4.1/2 pol G60", "4.1/2 pol G80"], 13), ("Lixa ferro", ["G80", "G120"], 3.2)],
    "Ferramentas": [("Chave combinada", ["13 mm", "17 mm", "19 mm"], 22), ("Broca aço rápido", ["6 mm", "8 mm", "10 mm"], 15), ("Alicate universal", ["8 pol"], 49), ("Trena", ["5 m", "8 m"], 28)],
}
linhas, i = [], 21
for cat, fam in CAT.items():
    for nome, vars_, base in fam:
        for v in vars_:
            preco = max(.1, round(base * r.uniform(.8, 1.25), 2))
            est = 0 if r.random() < .05 else int(r.lognormal(np.log(7200 / (preco ** .75 + 1)), .8))
            linhas.append([f"P{i:03d}", f"{nome} {v}", cat, "un", f"{preco}", f"{round(preco * r.uniform(.86, .93), 2)}", str(est), str(pick([3, 5, 7, 10, 15]))])
            i += 1
produtos = pd.concat([prod0, pd.DataFrame(linhas, columns=prod0.columns)], ignore_index=True)
P = produtos.assign(p1=produtos.preco_unitario.astype(float), p2=produtos.preco_acima_100_un.astype(float))
assert P.descricao.is_unique
preco_de = P.set_index("cod_produto")


def preco(c, q):
    return float(preco_de.at[c, "p2"] if q > 100 else preco_de.at[c, "p1"])


# ---------- itens dos pedidos originais (leitura manual das mensagens) ----------
ITENS0 = {"PED001": [("P001", 200), ("P002", 50)], "PED002": [("P003", 500), ("P002", 500)], "PED003": [("P007", 10)], "PED004": [("P015", 30), ("P016", 30)], "PED005": [("P010", 2), ("P011", 1)], "PED006": [("P012", 5), ("P013", 10)], "PED007": [("P020", 60)], "PED008": [("P004", 150), ("P003", 150)], "PED009": [("P005", 300)], "PED010": [("P006", 20), ("P008", 5)], "PED011": [("P017", 40), ("P018", 40), ("P019", 200)], "PED013": [("P003", 100)], "PED014": [("P014", 24)], "PED015": [("P015", 100), ("P016", 100), ("P018", 50)], "PED017": [("P009", 25), ("P010", 10)], "PED019": [("P015", 100), ("P016", 100), ("P017", 20)], "PED020": [("P001", 1000)], "PED021": [("P002", 50)], "PED022": [("P011", 12)], "PED023": [("P012", 2), ("P013", 20), ("P014", 50)], "PED024": [("P020", 15), ("P007", 5)], "PED025": [("P019", 300), ("P016", 100)], "PED026": [("P004", 80), ("P003", 80)], "PED028": [("P018", 10), ("P019", 10)], "PED029": [("P012", 60)], "PED030": [("P008", 30), ("P006", 40)]}
itens = [[k, c, q, preco(c, q), 0] for k, v in ITENS0.items() for c, q in v]

# ---------- pedidos, itens e títulos ----------
AFIN = {"Indústria": ["Rolamentos", "Correias", "Lubrificantes", "Vedações", "EPIs", "Fixadores", "Abrasivos"], "Oficina": ["Lubrificantes", "Vedações", "Rolamentos", "Ferramentas"], "Revenda": ["Fixadores", "Ferramentas", "Abrasivos", "Lubrificantes", "EPIs"], "Construtora": ["Fixadores", "EPIs", "Abrasivos", "Ferramentas"], "Transporte": ["Lubrificantes", "Rolamentos", "Correias", "EPIs"], "Setor público": ["EPIs", "Ferramentas", "Lubrificantes"], "Agronegócio": ["Correias", "Rolamentos", "Lubrificantes", "EPIs"]}
CANAL = {"Indústria": [.8, .15, .05], "Oficina": [.1, .55, .35], "Revenda": [.6, .35, .05], "Construtora": [.7, .25, .05], "Transporte": [.25, .65, .1], "Setor público": [1, 0, 0], "Agronegócio": [.3, .5, .2]}
CANAIS = ["e-mail", "whatsapp", "telefone"]
SAZ = {1: .8, 2: .85, 3: 1.05, 4: 1, 5: 1.05, 6: 1.1, 7: 1, 8: 1.15, 9: 1.1, 10: 1.1, 11: 1, 12: .65}
PERFIS = ["pontual", "pontual", "pontual", "atrasa_pouco", "atrasa_pouco", "atrasa_muito"]

C = clientes.copy()
C["peso"] = r.pareto(1.3, len(C)) + .2
C["perfil"] = [pick(PERFIS) for _ in range(len(C))]
C["desde"] = pd.to_datetime(C.cliente_desde)
C["orig"] = C.cod_cliente.le("C012")
P["peso"] = r.pareto(1.1, len(P)) + .1
P["qbase"] = np.clip(420 / (P.p1 ** .75), 3, 900)

MSG = {
    "e-mail": ["Bom dia, favor cotar {i}.", "Solicitamos cotação de {i}.", "Precisamos de {i}. Qual o prazo de entrega?", "Prezados, enviar proposta para {i}, condição habitual."],
    "whatsapp": ["Tem {i}? Manda o preço.", "Boa tarde. Preciso de {i}.", "{i}. Faturar no prazo de sempre.", "Consegue {i} pra essa semana?"],
    "telefone": ["Ligou pedindo {i}. Vai retirar no balcão.", "Pediu por telefone: {i}. Retorna depois pelo preço."],
}
EXTRA = [" Urgente.", " Sem urgência.", " Entrega normal.", "", "", "", " Tem desconto?"]
FORA = ["Vocês vendem pneu de empilhadeira?", "Tem compressor de ar 100 litros?", "Trabalham com solda MIG? Preciso de arame 0,8.", "Vende tinta epóxi em galão?", "Tem motor elétrico trifásico de 5 cv?"]
RECLA = ["O pedido anterior veio com quantidade errada. Preciso da correção.", "A entrega atrasou dois dias e parou a nossa manutenção.", "Item veio com embalagem danificada. Quero a troca.", "Boleto veio com valor diferente da cotação, favor corrigir."]
SPAM = ["OFERTA: certificado digital com 50% de desconto. Clique aqui.", "Aumente suas vendas com disparo em massa no WhatsApp. Fale conosco.", "Empréstimo para empresas aprovado na hora, sem burocracia."]

ped, tits, nped, ntit, nf_h, nf_r = [], [], 31, 36, 1001, 4836
for d in pd.bdate_range(INICIO, FIM_PEDIDOS):
    cresc = 1 + .25 * (d - INICIO).days / 600
    for _ in range(r.poisson(5.4 * SAZ[d.month] * cresc)):
        cod = f"PED{nped:04d}"
        nped += 1
        u = r.random()
        if u < .025:
            ped.append([cod, d, "", "e-mail", pick(SPAM), "descartado"])
            continue
        base = C[(C.desde <= d) & (~C.orig | (d + pd.Timedelta(days=3) < CORTE_ORIGINAIS))]
        cl = base.sample(1, weights=base.peso, random_state=int(r.integers(1 << 31))).iloc[0]
        canal = str(r.choice(CANAIS, p=CANAL[cl.segmento]))
        if u < .06:
            ped.append([cod, d, cl.cod_cliente, canal, pick(RECLA), "reclamacao"])
            continue
        if u < .09:
            ped.append([cod, d, cl.cod_cliente, canal, pick(FORA), "descartado"])
            continue
        pool = P[P.categoria.isin(AFIN[cl.segmento])]
        if d >= pd.Timestamp("2026-08-10"):
            pool = pool[pool.cod_produto > "P020"]
        esc = pool.sample(int(r.choice([1, 2, 3, 4], p=[.3, .34, .23, .13])), weights=pool.peso, random_state=int(r.integers(1 << 31)))
        desc = int(cl.desconto_maximo_pct)
        d_pct = 0 if desc == 0 else int(r.choice([0, desc // 2, desc], p=[.5, .25, .25]))
        trechos, total = [], 0.0
        for _, pr in esc.iterrows():
            q = max(1, int(round(r.lognormal(np.log(pr.qbase), .75) / 5) * 5))
            pu = float(pr.p2 if q > 100 else pr.p1)
            itens.append([cod, pr.cod_produto, q, pu, d_pct])
            total += q * pu * (1 - d_pct / 100)
            trechos.append(f"{q} {pr.descricao[0].lower()}{pr.descricao[1:]}")
        txt = ", ".join(trechos[:-1]) + (" e " if len(trechos) > 1 else "") + trechos[-1]
        msg = pick(MSG[canal]).format(i=txt) + pick(EXTRA)
        st = "cotado" if d >= pd.Timestamp("2026-08-10") else ("faturado" if r.random() < .68 else "perdido")
        ped.append([cod, d, cl.cod_cliente, canal, msg, st])
        if st == "faturado":
            em = d + pd.Timedelta(days=int(r.integers(1, 4)))
            prazo = int(cl.prazo_pagamento_dias) or 3
            if em < CORTE_ORIGINAIS:
                nf, nf_h = nf_h, nf_h + 1
            else:
                nf, nf_r = nf_r, nf_r + 1
            tits.append(dict(cod_titulo=f"T{ntit:04d}", cod_cliente=cl.cod_cliente, nota_fiscal=f"NF-{nf}", valor=round(total, 2), emissao=em, vencimento=em + pd.Timedelta(days=prazo), cod_pedido=cod, nome=cl.nome, perfil=cl.perfil))
            ntit += 1
assert nf_h < 4801
ped_df = pd.DataFrame(ped, columns=ped0.columns)
ped_df["data"] = ped_df.data.dt.strftime("%Y-%m-%d")
pedidos = pd.concat([ped0, ped_df], ignore_index=True)
pedido_itens = pd.DataFrame(itens, columns=["cod_pedido", "cod_produto", "quantidade", "preco_unitario", "desconto_pct"])

# ---------- extrato ----------
ext, status = [], {}
ATRASO = {"pontual": (.92, 3), "atrasa_pouco": (.6, 12), "atrasa_muito": (.3, 35)}


def lanc(dt, desc, val):
    if dt > FIM_EXTRATO:
        return False
    ext.append(["", dt, desc, round(val, 2), "credito" if val > 0 else "debito"])
    return True


for t in tits:
    nome, v, nf = sem_acento(t["nome"]), t["valor"], t["nota_fiscal"]
    pz, cauda = ATRASO[t["perfil"]]
    atraso = int(r.integers(-3, 2)) if r.random() < pz else int(r.integers(1, cauda + 1))
    dt = t["vencimento"] + pd.Timedelta(days=atraso)
    u = r.random()
    pago = False
    original = t["cod_cliente"] <= "C012"
    cronico = t["perfil"] == "atrasa_muito" and u < .02 and not original
    recente = t["vencimento"] >= INICIO_PENDENCIAS
    if (u < .04 or .07 <= u < .11) and not cronico and (original or not recente):
        u = .5  # sem pendência
    if cronico or u < .012:
        pass  # inadimplência
    elif u < .04:
        lanc(dt, f"PIX RECEBIDO {nome} {nf}", round(v * r.uniform(.6, .95), 2))  # parcial
    elif u < .055:
        pago = lanc(dt, f"PIX RECEBIDO {nome} {nf}", v)  # duplicado
        lanc(dt + pd.Timedelta(days=int(r.integers(1, 5))), f"PIX RECEBIDO {nome} {nf}", v)
    elif u < .07:
        pago = lanc(dt, f"PIX RECEBIDO {nome} {nf}", round(v * r.uniform(1.02, 1.2), 2))  # a maior
    elif u < .095:
        lanc(dt, f"PIX RECEBIDO {nome}", v)  # sem NF
    elif u < .11:
        lanc(dt, "DEPOSITO EM DINHEIRO", v)  # sem identificação
    else:
        pago = lanc(dt, f"{'BOLETO LIQUIDADO' if r.random() < .3 else 'PIX RECEBIDO'} {nome} {nf}", v)
    status[t["cod_titulo"]] = "pago" if pago else "aberto"

FORN = ["ACO MINAS", "PARAFUSOS UNIAO", "LUBRIFICA BRASIL", "EPI SUDESTE", "BORRACHAS TRIANGULO", "ROLAMENTOS CENTRO OESTE"]
for m in pd.date_range("2025-01-01", "2026-09-01", freq="MS"):
    if m == pd.Timestamp("2026-08-01"):
        continue  # agosto/26 já está no extrato original
    fat = sum(t["valor"] for t in tits if t["emissao"].to_period("M") == m.to_period("M"))
    lanc(m + pd.Timedelta(days=2), "TARIFA MANUTENCAO CONTA", -45.90)
    for _ in range(int(r.integers(2, 6))):
        lanc(m + pd.Timedelta(days=int(r.integers(1, 27))), "TARIFA PIX", -1.20)
    lanc(m + pd.Timedelta(days=19), "PAGAMENTO FOLHA", -round(float(r.normal(42300, 900)), 2))
    k = int(r.integers(3, 6))
    parte = r.dirichlet(np.ones(k)) * fat * r.uniform(.45, .6)
    for j in range(k):
        lanc(m + pd.Timedelta(days=int(r.integers(3, 27))), f"PIX ENVIADO FORNECEDOR {FORN[j]}", -float(parte[j]))

ext_df = pd.DataFrame(ext, columns=ext0.columns).sort_values("data", kind="stable").reset_index(drop=True)
ext_df["cod_lancamento"] = [f"L{i:04d}" for i in range(39, 39 + len(ext_df))]
ext_df["data"] = ext_df.data.dt.strftime("%Y-%m-%d")
ext_df["valor"] = ext_df.valor.map("{:.2f}".format)
extrato = pd.concat([ext0, ext_df], ignore_index=True)

tit_df = pd.DataFrame(tits)
tit_df["status"] = tit_df.cod_titulo.map(status)
tit_df["valor"] = tit_df.valor.map("{:.2f}".format)
tit_df["emissao"] = tit_df.emissao.dt.strftime("%Y-%m-%d")
tit_df["vencimento"] = tit_df.vencimento.dt.strftime("%Y-%m-%d")
titulos = pd.concat([tit0.assign(cod_pedido=""), tit_df[list(tit0.columns) + ["cod_pedido"]]], ignore_index=True)

saida = dict(clientes=clientes, produtos=produtos, pedidos_orcamento=pedidos, pedido_itens=pedido_itens, titulos_receber=titulos, extrato_bancario=extrato)
for nome, df in saida.items():
    df.to_csv(RAIZ / f"{nome}.csv", index=False, encoding="utf-8", lineterminator="\n")
    print(f"{nome}: {len(df)} linhas")
