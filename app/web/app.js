// Interface web: chama a API e mostra só o que o perfil do funcionário permite.
const $ = (s) => document.querySelector(s);
const NOMES_ABAS = { estoque: "Estoque", retirada: "Retirada", devolucao: "Devolução", entrada: "Entrada e descarte",
  alertas: "Alertas", auditoria: "Auditoria", cadastros: "Cadastros" };
let token = sessionStorage.getItem("token");
let eu = null;

const TIPOS = { entrada: "Entrada", retirada: "Retirada", devolucao: "Devolução", descarte: "Descarte", ajuste: "Ajuste" };
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const data = (iso) => new Date(iso + (iso.length === 10 ? "T00:00" : "")).toLocaleDateString("pt-BR");
const dataHora = (iso) => new Date(iso).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });

async function api(caminho, { method = "GET", body } = {}) {
  const r = await fetch("/api" + caminho, {
    method,
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: "Bearer " + token } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (r.status === 401 && caminho !== "/login") { sair(); throw new Error("Sessão expirada. Entre novamente."); }
  const dados = r.status === 204 ? null : await r.json();
  if (!r.ok) {
    const d = dados?.detail;
    throw new Error(Array.isArray(d) ? d.map((e) => e.msg).join("; ") : d || "Erro " + r.status);
  }
  return dados;
}

function aviso(texto, tipo = "ok") {
  const m = $("#mensagem");
  m.textContent = texto; m.className = tipo; m.hidden = false;
  clearTimeout(aviso.t); aviso.t = setTimeout(() => (m.hidden = true), 6000);
}

const formDados = (f) => Object.fromEntries([...new FormData(f)].filter(([, v]) => v !== ""));

function aoEnviar(seletor, acao) {
  $(seletor).addEventListener("submit", async (ev) => {
    ev.preventDefault();
    try { await acao(formDados(ev.target), ev.target); } catch (e) { aviso(e.message, "erro"); }
  });
}

// ---------- sessão ----------
aoEnviar("#form-login", async (d) => {
  token = (await api("/login", { method: "POST", body: d })).access_token;
  sessionStorage.setItem("token", token);
  await iniciar();
});
$("#sair").onclick = sair;
function sair() {
  token = null; eu = null; sessionStorage.removeItem("token");
  $("#tela-app").hidden = true; $("#usuario").hidden = true; $("#tela-login").hidden = false;
}

async function iniciar() {
  eu = await api("/eu");
  $("#quem").textContent = `${eu.nome} · ${eu.perfil}`;
  $("#tela-login").hidden = true; $("#tela-app").hidden = false; $("#usuario").hidden = false;
  const abas = [...document.querySelectorAll(".aba")].filter((a) => a.dataset.perfis.split(" ").includes(eu.perfil));
  $("#abas").innerHTML = "";
  for (const a of abas) {
    const b = document.createElement("button");
    b.textContent = NOMES_ABAS[a.dataset.aba]; b.onclick = () => abrir(a.dataset.aba);
    b.dataset.aba = a.dataset.aba; $("#abas").append(b);
  }
  abrir(abas[0].dataset.aba);
}

async function abrir(nome) {
  document.querySelectorAll(".aba").forEach((a) => (a.hidden = a.dataset.aba !== nome));
  document.querySelectorAll("#abas button").forEach((b) => b.classList.toggle("ativa", b.dataset.aba === nome));
  try { await (CARREGAR[nome] || (() => {}))(); } catch (e) { aviso(e.message, "erro"); }
}

// ---------- telas ----------
let medicamentos = [];
async function carregarMedicamentos() {
  medicamentos = await api("/medicamentos");
  const opcoes = medicamentos.map((m) => `<option value="${m.id}">${esc(m.nome)} ${esc(m.apresentacao)}${m.classe === "controlado" ? " (controlado)" : ""} — disp. ${m.estoque_disponivel}</option>`).join("");
  document.querySelectorAll(".sel-medicamento").forEach((s) => (s.innerHTML = opcoes));
  $("#sel-lote").innerHTML = medicamentos.flatMap((m) => m.lotes.map((l) =>
    `<option value="${l.id}">${esc(m.nome)} · ${esc(l.codigo)} · val. ${data(l.validade)} · qtd ${l.quantidade}</option>`)).join("");
}

const CARREGAR = {
  async estoque() {
    await carregarMedicamentos();
    $("#tabela-estoque").innerHTML = medicamentos.map((m) => `<tr>
      <td>${esc(m.nome)} <small>${esc(m.apresentacao)}</small></td>
      <td><span class="etiqueta ${m.classe}">${m.classe}</span></td>
      <td class="${m.estoque_disponivel < m.estoque_minimo ? "abaixo" : ""}">${m.estoque_disponivel}</td>
      <td>${m.estoque_minimo}</td>
      <td>${m.lotes.map((l) => `${esc(l.codigo)}: ${data(l.validade)} · ${l.quantidade}${l.vencido ? ' <span class="etiqueta vencido">vencido</span>' : ""}`).join("<br>") || "—"}</td></tr>`).join("");
  },
  retirada: carregarMedicamentos,
  entrada: carregarMedicamentos,
  async devolucao() {
    const rets = await api("/movimentacoes/retiradas");
    $("#tabela-retiradas").innerHTML = rets.map((r) => `<tr>
      <td>${r.id}</td><td>${dataHora(r.data_hora)}</td><td>${esc(r.medicamento)}</td><td>${esc(r.setor)}</td>
      <td>${esc(r.funcionario)}</td><td>${r.quantidade}</td><td>${r.devolvivel}</td>
      <td>${r.devolvivel > 0 ? `<button class="pequeno" data-devolver="${r.id}" data-max="${r.devolvivel}">Devolver</button>` : ""}</td></tr>`).join("")
      || '<tr><td colspan="8">Nenhuma retirada.</td></tr>';
  },
  async alertas() {
    const rep = await api("/alertas/reposicao");
    $("#tabela-reposicao").innerHTML = rep.map((a) => `<tr><td>${esc(a.medicamento)}</td><td class="abaixo">${a.estoque_disponivel}</td><td>${a.estoque_minimo}</td><td>${a.faltam}</td></tr>`).join("")
      || '<tr><td colspan="4">Nenhum medicamento abaixo do mínimo.</td></tr>';
    const val = await api("/alertas/validade");
    $("#tabela-validade").innerHTML = val.map((a) => `<tr><td>${esc(a.medicamento)}</td><td>${esc(a.codigo_lote)}</td><td>${data(a.validade)}</td><td>${a.quantidade}</td>
      <td>${a.vencido ? '<span class="etiqueta vencido">vencido — descartar</span>' : `vence em ${a.dias_para_vencer} dia(s)`}</td></tr>`).join("")
      || '<tr><td colspan="5">Nenhum lote perto de vencer.</td></tr>';
  },
  async auditoria(filtros = {}) {
    const q = new URLSearchParams(filtros).toString();
    const movs = await api("/auditoria" + (q ? "?" + q : ""));
    $("#tabela-auditoria").innerHTML = movs.map((m) => `<tr><td>${m.id}</td><td>${dataHora(m.data_hora)}</td><td>${TIPOS[m.tipo]}</td>
      <td>${esc(m.medicamento)}</td><td>${m.itens.map((i) => `${esc(i.codigo_lote)}: ${i.variacao > 0 ? "+" : ""}${i.variacao}`).join("<br>")}</td>
      <td>${esc(m.funcionario)}</td><td>${[m.setor, m.paciente, m.motivo, m.retirada_origem_id ? "ref. retirada #" + m.retirada_origem_id : ""].filter(Boolean).map(esc).join(" · ")}</td></tr>`).join("")
      || '<tr><td colspan="7">Nenhuma movimentação.</td></tr>';
  },
  async cadastros() {
    const fs = await api("/funcionarios");
    $("#tabela-funcionarios").innerHTML = fs.map((f) => `<tr><td>${esc(f.nome)}</td><td>${esc(f.email)}</td><td>${f.perfil}</td>
      <td>${f.ativo ? "ativo" : "inativo"}</td><td>${f.ativo && f.id !== eu.id ? `<button class="pequeno" data-desativar="${f.id}">Desativar</button>` : ""}</td></tr>`).join("");
  },
};

// ---------- ações ----------
aoEnviar("#form-retirada", async (d, f) => {
  const m = await api("/movimentacoes/retiradas", { method: "POST", body: { ...d, medicamento_id: +d.medicamento_id, quantidade: +d.quantidade } });
  aviso(`Retirada #${m.id} registrada: ${m.itens.map((i) => `${i.quantidade} do lote ${i.codigo_lote}`).join(", ")}.`);
  f.reset(); await carregarMedicamentos();
});
aoEnviar("#form-entrada", async (d, f) => {
  const m = await api("/movimentacoes/entradas", { method: "POST", body: { ...d, medicamento_id: +d.medicamento_id, quantidade: +d.quantidade } });
  aviso(`Entrada #${m.id} registrada (lote ${m.itens[0].codigo_lote}).`); f.reset(); await carregarMedicamentos();
});
aoEnviar("#form-descarte", async (d, f) => {
  const ajuste = d.operacao === "ajuste";
  const corpo = ajuste ? { lote_id: +d.lote_id, nova_quantidade: +d.quantidade, motivo: d.motivo }
                       : { lote_id: +d.lote_id, quantidade: +d.quantidade, motivo: d.motivo };
  const m = await api(`/movimentacoes/${ajuste ? "ajustes" : "descartes"}`, { method: "POST", body: corpo });
  aviso(`${ajuste ? "Ajuste" : "Descarte"} #${m.id} registrado.`); f.reset(); await carregarMedicamentos();
});
aoEnviar("#form-auditoria", (d) => CARREGAR.auditoria(d));
aoEnviar("#form-funcionario", async (d, f) => {
  await api("/funcionarios", { method: "POST", body: d }); aviso("Funcionário cadastrado."); f.reset(); await CARREGAR.cadastros();
});
aoEnviar("#form-medicamento", async (d, f) => {
  await api("/medicamentos", { method: "POST", body: { ...d, estoque_minimo: +d.estoque_minimo } }); aviso("Medicamento cadastrado."); f.reset();
});
document.addEventListener("click", async (ev) => {
  const b = ev.target.closest("button[data-devolver], button[data-desativar]");
  if (!b) return;
  try {
    if (b.dataset.devolver) {
      const qtd = prompt(`Quantas unidades devolver? (máx. ${b.dataset.max})`);
      if (!qtd) return;
      await api("/movimentacoes/devolucoes", { method: "POST", body: { retirada_id: +b.dataset.devolver, quantidade: +qtd } });
      aviso("Devolução registrada."); await CARREGAR.devolucao();
    } else if (confirm("Desativar este funcionário? O histórico dele é mantido.")) {
      await api(`/funcionarios/${b.dataset.desativar}/desativar`, { method: "POST" });
      aviso("Funcionário desativado."); await CARREGAR.cadastros();
    }
  } catch (e) { aviso(e.message, "erro"); }
});

if (token) iniciar().catch(sair);
