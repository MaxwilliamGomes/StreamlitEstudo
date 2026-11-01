"""Visuais clicáveis em HTML. Os dados são escapados no JavaScript antes de exibir."""
import streamlit as st

BASE_JS = """
const esc = (v) => String(v).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
"""

CSS = """
:host, * { box-sizing: border-box; font-family: "Source Sans", "Source Sans Pro", sans-serif; }
.raiz { color: #eef3fb; font-size: 13.5px; }
.barra-anima { transform-origin: left; animation: crescer .35s ease-out; }
@keyframes crescer { from { transform: scaleX(0); } }
.vazio { color: #8fa3c0; padding: 18px 4px; }

/* Fila */
.fila { height: 372px; overflow-y: auto; scrollbar-width: thin; scrollbar-color: #33507a transparent; }
table { width: 100%; border-collapse: collapse; }
th { position: sticky; top: 0; z-index: 2; background: #0c1630; text-align: left; font-weight: 500;
     color: #b9c7dc; padding: 7px 10px; border-bottom: 1px solid rgba(255,255,255,.55); }
th.num, td.num { text-align: right; }
td { padding: 6px 10px; white-space: nowrap; }
tr.grupo td { font-weight: 700; color: #fff; padding-top: 10px; }
tr.grupo .marca { color: #8fb4e8; margin-right: 8px; }
tr.linha { cursor: pointer; transition: background .15s; }
tr.linha:hover { background: rgba(96,165,250,.13); }
tr.linha.ativa { background: rgba(59,130,246,.3); box-shadow: inset 3px 0 #60a5fa; }
tr.linha.sem-foco { opacity: .42; }
.cod { color: #9fb3d1; margin-right: 10px; }
.motivo { color: #b9c7dc; max-width: 260px; overflow: hidden; text-overflow: ellipsis; }
.celula-barra { position: relative; min-width: 128px; height: 23px; }
.celula-barra i { position: absolute; left: 0; top: 0; bottom: 0; border-radius: 3px; }
.celula-barra span { position: relative; display: block; text-align: right; line-height: 23px; padding-right: 6px; font-weight: 600; }
.verde i { background: linear-gradient(90deg, #15803d, #34c04f); }
.topo i { background: linear-gradient(90deg, #22a33a, #63e36f); box-shadow: 0 0 12px rgba(99,227,111,.45); }
.Bom i { background: linear-gradient(90deg, #1d4ed8, #3b9dff); }
.Atenção i { background: linear-gradient(90deg, #b7791f, #fbbf24); }
.Crítico i { background: linear-gradient(90deg, #be123c, #fb7185); }
.pilula { display: inline-block; min-width: 62px; text-align: center; padding: 2px 9px; border-radius: 999px; font-weight: 600; }
.pilula.Bom { color: #9fb3d1; }
.pilula.Atenção { background: rgba(251,191,36,.18); color: #fcd34d; }
.pilula.Crítico { background: rgba(251,113,133,.2); color: #fda4af; }

/* Listas */
.faixas { display: flex; gap: 4px; margin: 2px 0 12px; }
.faixa { cursor: pointer; min-width: 74px; transition: opacity .15s, transform .15s; }
.faixa:hover { transform: translateY(-1px); }
.faixa i { display: block; height: 10px; border-radius: 5px; }
.faixa small { display: block; color: #b9c7dc; margin-top: 5px; font-size: 12px; }
.faixa b { font-size: 15px; }
.apagado { opacity: .3; }
.item { display: grid; grid-template-columns: 18px 172px 1fr 74px; gap: 8px; align-items: center;
        padding: 3px 6px; border-radius: 7px; cursor: pointer; transition: background .15s, opacity .15s; }
.item:hover { background: rgba(96,165,250,.13); }
.item.ativo { background: rgba(59,130,246,.3); }
.rank { color: #8fa3c0; text-align: right; font-size: 12px; }
.nome { overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.pista { display: flex; gap: 2px; height: 9px; }
.pista i { display: block; height: 100%; border-radius: 3px; }
.total { text-align: right; color: #d4deec; }
.lista { height: 352px; overflow-y: auto; scrollbar-width: thin; scrollbar-color: #33507a transparent; }
.produto { padding: 5px 6px; border-radius: 8px; cursor: pointer; transition: background .15s, opacity .15s; }
.produto:hover { background: rgba(96,165,250,.13); }
.produto.ativo { background: rgba(59,130,246,.3); }
.produto header { display: flex; justify-content: space-between; gap: 8px; margin-bottom: 4px; }
.produto em { font-style: normal; color: #b9c7dc; white-space: nowrap; }
.fundo { height: 8px; background: rgba(251,113,133,.28); border-radius: 4px; overflow: hidden; }
.fundo i { display: block; height: 100%; border-radius: 4px; min-width: 3px; }
"""

JS_FILA = BASE_JS + """
export default function ({ parentElement, data, setTriggerValue }) {
  const raiz = parentElement.querySelector('.raiz');
  const antes = raiz.querySelector('.fila');
  const rolagem = antes ? antes.scrollTop : 0;
  if (!data.grupos.length) { raiz.innerHTML = '<div class="vazio">Nenhum orçamento nesta seleção.</div>'; return; }
  const linhas = data.grupos.map((g) => {
    const corpo = g.linhas.map((l) => {
      const classe = data.selecionado ? (l.cod === data.selecionado ? 'ativa' : 'sem-foco') : '';
      const valor = l.topo ? 'topo' : 'verde';
      return `<tr class="linha ${classe}" data-cod="${esc(l.cod)}">
        <td><span class="cod">${esc(l.cod)}</span>${esc(l.cliente)}</td>
        <td class="num"><div class="celula-barra ${valor}"><i class="barra-anima" style="width:${l.peso}%"></i><span>${esc(l.valor)}</span></div></td>
        <td class="num"><div class="celula-barra ${esc(l.nivel_cobertura)}"><i class="barra-anima" style="width:${l.cobertura}%"></i><span>${l.cobertura}%</span></div></td>
        <td class="num"><span class="pilula ${esc(l.nivel_atraso)}">${l.atraso ? l.atraso + ' dias' : '–'}</span></td>
        <td class="motivo" title="${esc(l.motivo)}">${esc(l.motivo)}</td></tr>`;
    }).join('');
    return `<tr class="grupo"><td><span class="marca">▾</span>${esc(g.nome)}</td>
      <td class="num">${esc(g.valor)}</td><td class="num"></td><td class="num">${esc(g.quantidade)}</td><td></td></tr>${corpo}`;
  }).join('');
  raiz.innerHTML = `<div class="fila"><table><thead><tr><th>Orçamento e cliente</th><th class="num">Valor</th>
    <th class="num">Cobertura</th><th class="num">Atraso</th><th>Motivo</th></tr></thead><tbody>${linhas}</tbody></table></div>`;
  const fila = raiz.querySelector('.fila');
  fila.scrollTop = rolagem;
  fila.onclick = (e) => {
    const linha = e.target.closest('[data-cod]');
    if (linha) setTriggerValue('linha', linha.dataset.cod);
  };
}
"""

JS_VENCIDOS = BASE_JS + """
export default function ({ parentElement, data, setTriggerValue }) {
  const raiz = parentElement.querySelector('.raiz');
  const faixas = data.faixas.map((f) => `<div class="faixa ${f.ativa ? '' : 'apagado'}" data-faixa="${esc(f.nome)}" style="flex:${f.peso}">
    <i class="barra-anima" style="background:${f.cor}"></i><small>${esc(f.nome)} dias</small><b>${esc(f.valor)}</b></div>`).join('');
  const clientes = data.clientes.map((c) => `<div class="item ${c.selecionado ? 'ativo' : ''} ${c.ativo ? '' : 'apagado'}" data-cliente="${esc(c.cod)}">
    <span class="rank">${c.posicao}</span><span class="nome" title="${esc(c.nome)}">${esc(c.nome)}</span>
    <div class="pista">${c.partes.map((p) => `<i class="barra-anima" style="width:${p.peso}%;background:${p.cor}"></i>`).join('')}</div>
    <span class="total">${esc(c.total)}</span></div>`).join('');
  raiz.innerHTML = `<div class="faixas">${faixas}</div>${clientes || '<div class="vazio">Nenhum título vencido nesta seleção.</div>'}`;
  raiz.onclick = (e) => {
    const faixa = e.target.closest('[data-faixa]');
    const cliente = e.target.closest('[data-cliente]');
    if (faixa) setTriggerValue('faixa', faixa.dataset.faixa);
    if (cliente) setTriggerValue('cliente', cliente.dataset.cliente);
  };
}
"""

JS_RUPTURAS = BASE_JS + """
export default function ({ parentElement, data, setTriggerValue }) {
  const raiz = parentElement.querySelector('.raiz');
  const antes = raiz.querySelector('.lista');
  const rolagem = antes ? antes.scrollTop : 0;
  const itens = data.produtos.map((p) => `<div class="produto ${p.selecionado ? 'ativo' : ''} ${p.ativo ? '' : 'apagado'}" data-produto="${esc(p.cod)}">
    <header><span class="nome">${esc(p.nome)}</span><em>${esc(p.detalhe)}</em></header>
    <div class="fundo"><i class="barra-anima" style="width:${p.coberto}%;background:${p.cor}"></i></div></div>`).join('');
  raiz.innerHTML = `<div class="lista">${itens || '<div class="vazio">Nenhum produto em ruptura nesta seleção.</div>'}</div>`;
  const lista = raiz.querySelector('.lista');
  lista.scrollTop = rolagem;
  lista.onclick = (e) => {
    const produto = e.target.closest('[data-produto]');
    if (produto) setTriggerValue('produto', produto.dataset.produto);
  };
}
"""

_HTML = '<div class="raiz"></div>'
fila = st.components.v2.component("fila_orcamentos", html=_HTML, css=CSS, js=JS_FILA)
vencidos = st.components.v2.component("vencidos_clientes", html=_HTML, css=CSS, js=JS_VENCIDOS)
rupturas = st.components.v2.component("rupturas_produtos", html=_HTML, css=CSS, js=JS_RUPTURAS)
