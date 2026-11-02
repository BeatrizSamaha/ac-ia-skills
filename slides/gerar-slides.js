const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const REPO = "/home/claude/ac-ia-skills";
const IMG = "/home/claude/build/img/";
const C4 = REPO + "/docs/c4/";

const THEME = {
  name: "Farmacia Clinica",
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B2A2F", lt1: "FFFFFF", dk2: "0F4C5C", lt2: "EEF5F5",
    accent1: "0E7C7B", accent2: "E36414", accent3: "5FA8A0", accent4: "F2A541",
    accent5: "8A9A9E", accent6: "2D6A4F", hlink: "0E7C7B", folHlink: "5FA8A0",
  },
};
const HEX = THEME.colors;

async function icone(Comp, cor = "FFFFFF") {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: "#" + cor, size: 256 }));
  const buf = await sharp(Buffer.from(svg)).resize(256, 256).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
  pres.author = "Beatriz Samaha de Faria Garcia";
  pres.title = "Controle de Medicamentos Hospitalares — Engenharia de Software + IA orientada por Skills";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = pres.SchemeColor;

  // ---------- layouts ----------
  pres.defineSlideMaster({
    title: "CAPA",
    background: { color: C.text2 },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.2, w: 11.7, h: 1.6, fontSize: 44, bold: true, color: C.background1, valign: "bottom", align: "left" }, text: "" } },
      { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 3.9, w: 11.7, h: 2.4, fontSize: 18, color: C.background2, valign: "top" }, text: "" } },
    ],
  });
  pres.defineSlideMaster({
    title: "CONTEUDO",
    background: { color: C.background1 },
    margin: [0.5, 0.6, 0.6, 0.6],
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.1, h: 0.85, fontSize: 32, bold: true, color: C.text2, valign: "middle", margin: 0 }, text: "" } },
      { text: { text: "Controle de Medicamentos · AC Métodos e Aplicações de IA", options: { x: 0.6, y: 7.05, w: 8, h: 0.3, fontSize: 10, color: C.accent5, margin: 0 } } },
    ],
    slideNumber: { x: 12.2, y: 7.05, w: 0.5, h: 0.3, fontSize: 10, color: C.accent5, align: "right" },
  });

  const I = {
    pills: await icone(fa.FaPills), shield: await icone(fa.FaUserShield), boxes: await icone(fa.FaBoxes),
    exchange: await icone(fa.FaExchangeAlt), bell: await icone(fa.FaBell), comments: await icone(fa.FaComments),
    file: await icone(fa.FaFileAlt), ticket: await icone(fa.FaTicketAlt), vial: await icone(fa.FaVial),
    search: await icone(fa.FaSearch), redo: await icone(fa.FaRedo), check: await icone(fa.FaCheckCircle),
    warn: await icone(fa.FaExclamationTriangle), bulb: await icone(fa.FaLightbulb), sitemap: await icone(fa.FaSitemap),
    cog: await icone(fa.FaCog), trophy: await icone(fa.FaTrophy), route: await icone(fa.FaRoute),
  };

  function iconeCirculo(slide, img, x, y, d = 0.6, cor = C.accent1, nome = "icone") {
    slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: cor }, line: { color: cor }, objectName: nome + "-fundo" });
    const p = d * 0.25;
    slide.addImage({ data: img, x: x + p, y: y + p, w: d - 2 * p, h: d - 2 * p, objectName: nome, altText: nome });
  }
  function cartao(slide, x, y, w, h, nome, cor = C.background2) {
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: cor }, line: { color: cor }, objectName: nome });
  }
  const etiqueta = (slide, rotulo) => slide.addText(rotulo, { isTextBox: true, margin: 0, x: 9.7, y: 0.08, w: 3.0, h: 0.28, fontSize: 11, bold: true, color: C.accent2, align: "right", objectName: "etiqueta-roteiro" });
  const P = "/home/claude/build/prints/";
  function print(slide, f, x, y, w, pw, ph, nome) { slide.addImage({ path: P + f, x, y, w, h: w * ph / pw, objectName: nome, altText: nome }); return y + w * ph / pw; }
  const txt = (slide, text, o) => slide.addText(text, { isTextBox: true, margin: 0, valign: "top", fontSize: 14, color: C.text1, ...o });

  // ===== 1. Capa =====
  pres.addSection({ title: "Abertura" });
  let s = pres.addSlide({ masterName: "CAPA", sectionTitle: "Abertura" });
  s.addText("Controle de Medicamentos Hospitalares", { placeholder: "title" });
  s.addText([
    { text: "Engenharia de Software + IA orientada por Skills", options: { bold: true, breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Beatriz Samaha de Faria Garcia", options: { breakLine: true } },
    { text: "Métodos e Aplicações de IA · Prof. Pedro Calais · Ibmec BH · 2026/2" },
  ], { placeholder: "body" });
  iconeCirculo(s, I.pills, 0.8, 1.0, 0.9, C.accent1, "icone-capa");
  s.addNotes("Abertura. Projeto feito com o conjunto Matt Pocock Skills, com o agente de IA executando o fluxo completo.");

  // ===== Roteiro =====
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Abertura" });
  s.addText("Roteiro: os itens pedidos no enunciado", { placeholder: "title" });
  const roteiro = [
    ["1", "O problema e a aplicação", "3–4"], ["2", "Conjunto de skills: justificativa e princípios", "5–6"],
    ["3", "Skills usadas e o processo, com prints", "7–11"], ["4", "Modelos C4: antes e depois do código", "12–13"],
    ["5", "Apontamentos que mudaram a rota", "14"], ["6", "Evidências de qualidade e resultados", "15–17"],
    ["7", "A skill mais útil (e as 7 perguntas da seção 5)", "18–19"], ["8", "Três aprendizados e o que faríamos diferente", "20"],
  ];
  roteiro.forEach(([n, t2, sl], i) => {
    const x = 0.6 + (i % 2) * 6.15, y = 1.45 + Math.floor(i / 2) * 1.2;
    cartao(s, x, y, 5.95, 1.0, "roteiro-" + i);
    s.addShape(pres.shapes.OVAL, { x: x + 0.2, y: y + 0.2, w: 0.6, h: 0.6, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: "roteiro-num-" + i });
    txt(s, n, { x: x + 0.2, y: y + 0.2, w: 0.6, h: 0.6, fontSize: 20, bold: true, color: C.background1, align: "center", valign: "middle" });
    txt(s, t2, { x: x + 1.0, y: y + 0.15, w: 3.9, h: 0.7, fontSize: 16, bold: true, color: C.text2, valign: "middle" });
    txt(s, (sl.includes("–") ? "slides " : "slide ") + sl, { x: x + 4.8, y: y + 0.15, w: 1.0, h: 0.7, fontSize: 12, color: C.accent5, align: "right", valign: "middle" });
  });
  cartao(s, 0.6, 6.3, 12.1, 0.6, "roteiro-central", C.text2);
  txt(s, "Fecho (slide 21): resposta à pergunta central, ou seja, como e em que condições as skills mudam o desenvolvimento, e com que evidências", { x: 0.85, y: 6.38, w: 11.6, h: 0.45, fontSize: 14, color: C.background1, valign: "middle" });
  s.addNotes("Cada slide traz no canto superior direito o item do roteiro do enunciado que ele atende.");

  // ===== 2. Problema =====
  pres.addSection({ title: "Problema e skills" });
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Problema e skills" });
  etiqueta(s, "Roteiro · item 1");
  s.addText("O problema: medicamento sem rastreio é risco ao paciente", { placeholder: "title" });
  txt(s, [
    { text: "Hoje, na farmácia central", options: { bold: true, fontSize: 18, color: C.text2, breakLine: true } },
    { text: "Não se sabe quanto há de cada medicamento nem o que vence primeiro", options: { bullet: true, breakLine: true } },
    { text: "Controlados podem sair sem farmacêutico e sem paciente", options: { bullet: true, breakLine: true } },
    { text: "Reposição só quando o item acaba", options: { bullet: true, breakLine: true } },
    { text: "Ninguém sabe quem retirou o quê, nem para qual setor", options: { bullet: true, breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "A aplicação", options: { bold: true, fontSize: 18, color: C.text2, breakLine: true } },
    { text: "API FastAPI + SQLite + interface web; 3 perfis (Administrador, Farmacêutico, Enfermeiro); estoque por lote com retirada FEFO; auditoria imutável.", options: {} },
  ], { x: 0.6, y: 1.45, w: 5.6, h: 5.3, fontSize: 15, paraSpaceAfter: 6 });
  const modulos = [
    [I.shield, "Acesso", "Login JWT, funcionários e autorização por perfil"],
    [I.boxes, "Estoque", "Medicamentos, lotes, validade e estoque disponível"],
    [I.exchange, "Movimentações", "Entrada, retirada FEFO, devolução, descarte e ajuste"],
    [I.bell, "Monitoramento", "Alertas de reposição e de validade; trilha de auditoria"],
  ];
  modulos.forEach(([ic, t, d], i) => {
    const y = 1.45 + i * 1.32;
    cartao(s, 6.7, y, 6.0, 1.12, "modulo-" + i);
    iconeCirculo(s, ic, 6.95, y + 0.26, 0.6, C.accent1, "icone-modulo-" + i);
    txt(s, [{ text: t, options: { bold: true, fontSize: 17, color: C.text2, breakLine: true } }, { text: d, options: { fontSize: 14 } }],
      { x: 7.8, y: y + 0.17, w: 4.7, h: 0.85 });
  });
  s.addNotes("Quatro módulos com responsabilidades distintas, banco, regras de negócio não triviais, autenticação e autorização: cobre todos os critérios de complexidade. Escolhido entre três ideias (GlowCheck, FitCheck e este) por não depender de OCR ou visão computacional.");

  // ===== Critérios de complexidade =====
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Problema e skills" });
  etiqueta(s, "Roteiro · item 1 · seção 3");
  s.addText("Os critérios de complexidade, um a um", { placeholder: "title" });
  const criterios = [
    ["Três ou mais módulos", "4: Acesso, Estoque, Movimentações, Monitoramento"],
    ["Persistência", "SQLite via SQLAlchemy: 5 tabelas, transação única por movimentação"],
    ["Regras não triviais e erros", "FEFO multi-lote, validade, limite de devolução, controlados; erros 401/403/404/409/422 em português"],
    ["API ou interface", "API REST com documentação OpenAPI (/docs) e interface web por perfil"],
    ["Segurança", "JWT, bcrypt, autorização por perfil, login em tempo constante"],
    ["Testes automatizados", "71 testes das regras e dos fluxos, pela API"],
    ["Documentação", "README, glossário, 6 ADRs, spec, 10 tickets e 4 diagramas C4"],
    ["Ambiguidade de requisitos", "16 decisões tornadas explícitas no /grill-with-docs"],
  ];
  criterios.forEach(([c, d], i) => {
    const x = 0.6 + (i % 2) * 6.15, y = 1.45 + Math.floor(i / 2) * 1.35;
    cartao(s, x, y, 5.95, 1.18, "criterio-" + i);
    iconeCirculo(s, I.check, x + 0.2, y + 0.29, 0.6, C.accent6, "icone-criterio-" + i);
    txt(s, [{ text: c, options: { bold: true, fontSize: 16, color: C.text2, breakLine: true } }, { text: d, options: { fontSize: 13 } }], { x: x + 1.0, y: y + 0.14, w: 4.8, h: 0.95 });
  });
  s.addNotes("Os sete critérios do enunciado mais a ambiguidade de requisitos, que o enunciado cita como outra fonte de complexidade.");

  // ===== 3. Por que Matt Pocock =====
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Problema e skills" });
  etiqueta(s, "Roteiro · item 2");
  s.addText("Por que Matt Pocock Skills", { placeholder: "title" });
  const razoes = [
    [I.comments, "Muita ambiguidade no domínio", "Validade, controlados, devolução, perfis: o grill-with-docs entrevista até resolver e já escreve glossário e ADRs"],
    [I.file, "Modelagem de domínio explícita", "GLOSSARY.md e ADRs criados no momento da decisão alimentam o critério de especificação"],
    [I.vial, "TDD em fatias verticais", "to-tickets gera tracer bullets e o implement chama tdd em cada um"],
    [I.search, "Revisão em dois eixos", "code-review separa padrões (glossário, ADRs, smells) de aderência à spec"],
  ];
  razoes.forEach(([ic, t, d], i) => {
    const y = 1.45 + i * 1.3;
    iconeCirculo(s, ic, 0.6, y + 0.05, 0.6, C.accent1, "icone-razao-" + i);
    txt(s, [{ text: t, options: { bold: true, fontSize: 16, color: C.text2, breakLine: true } }, { text: d, options: { fontSize: 14 } }],
      { x: 1.4, y, w: 5.3, h: 1.15 });
  });
  s.addTable([
    [{ text: "Alternativa", options: { bold: true, color: C.background1, fill: { color: C.text2 } } },
     { text: "Por que não", options: { bold: true, color: C.background1, fill: { color: C.text2 } } }],
    ["Superpowers", "Forte em plano e execução; pouco foco em glossário e domínio"],
    ["Addy Osmani", "25 skills; muitas de front-end, performance e deploy, sem uso aqui"],
    ["pstack", "Jovem (18 commits), voltado a TypeScript, delega ao Grok"],
    ["GSD Core", "Fases, ondas e subagentes: pesado para o porte do sistema"],
  ], { x: 7.2, y: 1.55, w: 5.5, colW: [1.6, 3.9], fontSize: 13, color: C.text1, border: { type: "solid", pt: 0.75, color: "D5E3E3" }, fill: { color: C.background1 }, valign: "middle", rowH: 0.75, objectName: "tabela-alternativas" });
  txt(s, "Registrado no ADR 0001", { x: 7.2, y: 5.55, w: 5.5, h: 0.3, fontSize: 12, italic: true, color: C.accent5 });
  s.addNotes("A escolha partiu da característica principal do problema: regras de negócio ambíguas. Os 5 conjuntos foram analisados nos repositórios oficiais.");

  // ===== 4. Como funciona =====
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Problema e skills" });
  etiqueta(s, "Roteiro · item 2");
  s.addText("Como o conjunto funciona", { placeholder: "title" });
  const etapas = [
    ["Alinhar", "/grill-with-docs", "Glossário + ADRs", I.comments],
    ["Especificar", "/to-spec  /to-tickets", "Spec + tickets", I.ticket],
    ["Construir", "/implement + /tdd", "Testes + código", I.vial],
    ["Revisar", "/code-review", "2 relatórios", I.search],
    ["Manter", "/retro", "Guardrails", I.redo],
  ];
  etapas.forEach(([t, sk, art, ic], i) => {
    const x = 0.6 + i * 2.5;
    cartao(s, x, 1.55, 2.1, 2.55, "etapa-" + i, C.text2);
    iconeCirculo(s, ic, x + 0.75, 1.75, 0.6, C.accent1, "icone-etapa-" + i);
    txt(s, t, { x: x + 0.1, y: 2.5, w: 1.9, h: 0.45, fontSize: 19, bold: true, color: C.background1, align: "center" });
    txt(s, sk, { x: x + 0.1, y: 2.95, w: 1.9, h: 0.5, fontSize: 13, color: C.background2, align: "center", fontFace: "Courier New" });
    txt(s, art, { x: x + 0.1, y: 3.5, w: 1.9, h: 0.4, fontSize: 13, italic: true, color: C.accent4, align: "center" });
    if (i < etapas.length - 1) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + 2.15, y: 2.6, w: 0.3, h: 0.4, fill: { color: C.accent2 }, line: { color: C.accent2 }, objectName: "seta-" + i });
  });
  const principios = [
    ["As decisões são do humano", "o agente busca os fatos e pergunta o resto, com uma recomendação"],
    ["Uma linguagem só", "GLOSSARY.md define cada termo e lista os sinônimos a evitar"],
    ["Tracer bullets", "cada ticket atravessa todas as camadas e é demonstrável"],
    ["Revisão separada da implementação", "subagentes com contexto limpo"],
  ];
  principios.forEach(([t, d], i) => {
    const x = 0.6 + (i % 2) * 6.15, y = 4.45 + Math.floor(i / 2) * 1.15;
    cartao(s, x, y, 5.95, 0.95, "principio-" + i);
    txt(s, [{ text: t, options: { bold: true, color: C.text2, breakLine: true } }, { text: d }], { x: x + 0.25, y: y + 0.13, w: 5.5, h: 0.75, fontSize: 14 });
  });
  s.addNotes("Princípio central do conjunto: alinhar antes de construir. Cada etapa produz um artefato versionado no repositório, e esses artefatos são as evidências deste trabalho.");

  // ===== 5. Processo =====
  pres.addSection({ title: "Processo" });
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Processo" });
  etiqueta(s, "Roteiro · item 3");
  s.addText("O processo que seguimos, skill por skill", { placeholder: "title" });
  const passos = [
    ["setup-matt-pocock-skills", "Tracker local (.scratch/), labels, layout de domínio", "adaptado"],
    ["grill-with-docs", "2 rodadas, 16 decisões, 6 cenários de borda, 22 termos, ADRs 0002–0005", ""],
    ["C4 Contexto + Container", "Antes do código, em Mermaid", "manual"],
    ["to-spec", "36 user stories, 1 seam de teste (API HTTP)", ""],
    ["to-tickets", "10 tickets com dependências", ""],
    ["implement + tdd", "10 ciclos red → green, 71 testes", ""],
    ["code-review", "2 subagentes paralelos: Standards × Spec", ""],
    ["C4 Componentes + Código", "Gerados do código final", "manual"],
    ["retro", "CI no GitHub + checagem automática do glossário", ""],
  ];
  passos.forEach(([sk, r, tag], i) => {
    const y = 1.45 + i * 0.6;
    s.addShape(pres.shapes.OVAL, { x: 0.6, y: y + 0.08, w: 0.36, h: 0.36, fill: { color: tag ? C.accent2 : C.accent1 }, line: { color: tag ? C.accent2 : C.accent1 }, objectName: "passo-" + i });
    txt(s, String(i + 1), { x: 0.6, y: y + 0.08, w: 0.36, h: 0.36, fontSize: 13, bold: true, color: C.background1, align: "center", valign: "middle" });
    txt(s, sk, { x: 1.15, y: y + 0.1, w: 3.6, h: 0.35, fontSize: 15, bold: true, color: C.text2, fontFace: "Courier New" });
    txt(s, r, { x: 4.85, y: y + 0.1, w: 6.5, h: 0.35, fontSize: 14 });
    if (tag) txt(s, tag, { x: 11.4, y: y + 0.1, w: 1.3, h: 0.35, fontSize: 12, italic: true, color: C.accent2, align: "right" });
  });
  s.addNotes("Em laranja, as etapas adaptadas ou sem skill. O C4 não é coberto por nenhuma skill do conjunto. O tracker padrão (GitHub Issues) não funcionava no ambiente do agente, então usamos o tracker local que a própria skill oferece.");

  // ===== 6. Interação =====
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Processo" });
  etiqueta(s, "Roteiro · item 3 · exemplo 1");
  s.addText("Exemplo 1 · /grill-with-docs: perguntas antes do código", { placeholder: "title" });
  cartao(s, 0.6, 1.45, 6.3, 5.35, "cartao-grill");
  txt(s, [
    { text: "Rodada 1 · pergunta da skill", options: { fontSize: 12, color: C.accent5, breakLine: true } },
    { text: "❓ Q2 · Unidade do estoque", options: { bold: true, fontSize: 16, color: C.text2, breakLine: true } },
    { text: "O estoque é por medicamento (\"Dipirona: 300\") ou por lote (medicamento + lote + validade + quantidade)?", options: { breakLine: true } },
    { text: "➡️ Recomendação: por lote, com retirada FEFO.", options: { bold: true, color: C.accent1, breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Rodada 2 · nasceu da resposta acima", options: { fontSize: 12, color: C.accent5, breakLine: true } },
    { text: "❓ Q8 · A retirada pode consumir vários lotes?", options: { bold: true, fontSize: 16, color: C.text2, breakLine: true } },
    { text: "Sim: senão, um lote quase vazio bloquearia retiradas comuns.", options: { breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Cenário de borda que virou teste", options: { fontSize: 12, color: C.accent5, breakLine: true } },
    { text: "Pedido de 10; lote A (vence antes) tem 4 e B tem 20 → sai 4 de A e 6 de B", options: { italic: true } },
  ], { x: 0.9, y: 1.7, w: 5.8, h: 4.95, fontSize: 14, paraSpaceAfter: 4 });
  txt(s, "O que a skill escreveu durante a conversa", { x: 7.3, y: 1.45, w: 5.4, h: 0.4, fontSize: 16, bold: true, color: C.text2 });
  const glos = [
    ["Lote", "Quantidade de um medicamento recebida junto, com código e validade próprios.", "remessa, pacote"],
    ["FEFO", "A retirada sai primeiro do lote válido que vence primeiro.", "FIFO"],
    ["Retirada", "Movimentação que tira unidades de um ou mais lotes para um setor.", "saída, baixa"],
  ];
  glos.forEach(([t, d, a], i) => {
    const y = 2.0 + i * 1.25;
    cartao(s, 7.3, y, 5.4, 1.1, "glossario-" + i);
    txt(s, [{ text: t + ": ", options: { bold: true, color: C.text2 } }, { text: d, options: { breakLine: true } },
      { text: "Evitar: " + a, options: { italic: true, color: C.accent2, fontSize: 12 } }], { x: 7.5, y: y + 0.12, w: 5.0, h: 0.9, fontSize: 13 });
  });
  txt(s, "GLOSSARY.md · ADR 0002 (estoque por lote, FEFO)", { x: 7.3, y: 5.85, w: 5.4, h: 0.3, fontSize: 12, italic: true, color: C.accent5 });
  s.addNotes("Formato real da skill: perguntas numeradas, cada uma com recomendação, em rodadas. A rodada 2 só existe porque a resposta da Q2 abriu novas perguntas. O registro completo está em evidencias/grill-rodadas.md.");

  // ===== Exemplo 2: spec e tickets =====
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Processo" });
  etiqueta(s, "Roteiro · item 3 · exemplo 2");
  s.addText("Exemplo 2 · /to-spec → /to-tickets: da conversa ao ticket", { placeholder: "title" });
  print(s, "p-spec.png", 0.6, 1.4, 6.2, 2204, 700, "print-spec");
  txt(s, [{ text: "/to-spec", options: { bold: true, color: C.text2, fontSize: 16, breakLine: true } },
    { text: "Sintetiza a conversa do grill numa spec sem entrevistar de novo: 36 user stories, decisões de implementação e a seam de teste (a API HTTP)." }],
    { x: 0.6, y: 3.55, w: 6.2, h: 1.3, fontSize: 14 });
  print(s, "p-ticket.png", 7.1, 1.4, 5.6, 2204, 838, "print-ticket");
  txt(s, [{ text: "/to-tickets", options: { bold: true, color: C.text2, fontSize: 16, breakLine: true } },
    { text: "Quebra a spec em 10 fatias verticais com dependências (\"Blocked by\") e critérios de aceite. O ticket 04 é o coração das regras: FEFO, estoque insuficiente, controlados." }],
    { x: 7.1, y: 3.75, w: 5.6, h: 1.5, fontSize: 14 });
  cartao(s, 0.6, 5.45, 12.1, 1.3, "cartao-exemplo2", C.text2);
  txt(s, [{ text: "Por que importa: ", options: { bold: true, color: C.accent4 } },
    { text: "cada critério de aceite do ticket virou um teste no slide seguinte. A user story 17 (\"retirada recusada quando o estoque é menor que o pedido\") é o teste test_quantidade_maior_que_o_disponivel_e_recusada_sem_alterar_nada." }],
    { x: 0.85, y: 5.6, w: 11.6, h: 1.05, fontSize: 14, color: C.background1, valign: "middle" });
  s.addNotes("Prints reais dos arquivos gerados pelas skills, em .scratch/controle-medicamentos/.");

  // ===== Exemplo 3: TDD =====
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Processo" });
  etiqueta(s, "Roteiro · item 3 · exemplo 3");
  s.addText("Exemplo 3 · /tdd: o teste nasce antes do código", { placeholder: "title" });
  print(s, "p-teste.png", 0.6, 1.4, 6.6, 2204, 746, "print-teste");
  txt(s, [{ text: "1. Red", options: { bold: true, color: C.accent2, fontSize: 16, breakLine: true } },
    { text: "O cenário de borda do grill (pedido de 10; lote A tem 4, lote B tem 20) escrito como teste, antes de existir a retirada." }],
    { x: 0.6, y: 3.8, w: 6.6, h: 1.0, fontSize: 14 });
  print(s, "p-redgreen.png", 0.6, 4.95, 6.6, 2204, 606, "print-red-green");
  cartao(s, 7.55, 1.4, 5.15, 5.4, "cartao-tdd");
  txt(s, [
    { text: "O que o terminal mostra", options: { bold: true, color: C.text2, fontSize: 17, breakLine: true } },
    { text: "11 falhas antes do código (red).", options: { bullet: true, breakLine: true } },
    { text: "Depois da implementação, 1 falha restante: o teste avançava o relógio 31 dias e o login expirava. Era um defeito do teste, não da regra.", options: { bullet: true, breakLine: true } },
    { text: "Corrigido o teste: 11 passam (green).", options: { bullet: true, breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Ganho de produtividade", options: { bold: true, color: C.text2, fontSize: 17, breakLine: true } },
    { text: "A suíte levava 77 s. Com bcrypt de 4 rounds só nos testes, passou a levar 4 s, o que viabilizou rodar o ciclo a cada ticket.", options: { bullet: true } },
  ], { x: 7.8, y: 1.65, w: 4.7, h: 5.0, fontSize: 14, paraSpaceAfter: 6 });
  s.addNotes("Logs reais em evidencias/logs/tdd-04-red.txt e tdd-04-green.txt. Os 10 tickets têm logs red e green.");

  // ===== Exemplo 4: code review =====
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Processo" });
  etiqueta(s, "Roteiro · item 3 · exemplo 4");
  s.addText("Exemplo 4 · /code-review: achado → teste → correção", { placeholder: "title" });
  print(s, "p-review.png", 0.6, 1.4, 6.0, 2204, 654, "print-review");
  txt(s, [{ text: "Achado", options: { bold: true, color: C.accent2, fontSize: 16, breakLine: true } },
    { text: "Um subagente sem o contexto da implementação leu o diff e apontou: o login só roda o bcrypt quando o e-mail existe, então o tempo de resposta revela quem está cadastrado. E o admin podia desativar a si mesmo." }],
    { x: 0.6, y: 3.3, w: 6.0, h: 1.5, fontSize: 14 });
  txt(s, [{ text: "Teste primeiro", options: { bold: true, color: C.accent2, fontSize: 16, breakLine: true } },
    { text: "3 testes novos falhando (red) antes da correção: autodesativação, mensagens em português, segredo JWT obrigatório." }],
    { x: 0.6, y: 5.0, w: 6.0, h: 1.2, fontSize: 14 });
  print(s, "p-diff.png", 6.95, 1.4, 5.75, 2204, 1164, "print-diff");
  txt(s, "Correção real (commit 64f9e58)", { x: 6.95, y: 4.5, w: 5.75, h: 0.3, fontSize: 12, italic: true, color: C.accent5 });
  s.addNotes("Relatório completo em evidencias/code-review-1.md, com a decisão tomada para cada achado: corrigido, mantido e documentado, ou deixado como trabalho futuro.");

  // ===== 7. C4 antes =====
  pres.addSection({ title: "Arquitetura" });
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Arquitetura" });
  etiqueta(s, "Roteiro · item 4");
  s.addText("C4 antes do código: Contexto e Container", { placeholder: "title" });
  s.addImage({ path: C4 + "c1-contexto.png", x: 0.6, y: 1.35, w: 5.3, h: 5.3 * 534 / 861, objectName: "c4-contexto", altText: "Diagrama C4 de contexto" });
  txt(s, [
    { text: "Nível 1 · Contexto", options: { bold: true, fontSize: 17, color: C.text2, breakLine: true } },
    { text: "Três perfis usam um único sistema; não há integrações externas (ADR 0005: só a farmácia central).", options: { breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Nível 2 · Container", options: { bold: true, fontSize: 17, color: C.text2, breakLine: true } },
    { text: "Web estática → API FastAPI → SQLite. Monólito modular, para a demo rodar com um comando (ADR 0004).", options: {} },
  ], { x: 6.4, y: 1.5, w: 6.3, h: 2.8, fontSize: 14 });
  s.addImage({ path: C4 + "c2-container.png", x: 0.9, y: 4.7, w: 11.5, h: 11.5 * 284 / 1484, objectName: "c4-container", altText: "Diagrama C4 de container" });
  s.addNotes("Gerados logo após o grill, antes de qualquer linha de código, como pede o enunciado.");

  // ===== 8. C4 depois =====
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Arquitetura" });
  etiqueta(s, "Roteiro · item 4");
  s.addText("C4 depois do código: Componentes e Código", { placeholder: "title" });
  s.addImage({ path: C4 + "c3-componentes.png", x: 0.6, y: 1.3, h: 5.6, w: 5.6 * 936 / 1662, objectName: "c4-componentes", altText: "Diagrama C4 de componentes" });
  s.addImage({ path: C4 + "c4-codigo.png", x: 4.5, y: 1.35, w: 8.1, h: 8.1 * 1117 / 1784, objectName: "c4-codigo", altText: "Diagrama de classes (C4 nível código)" });
  txt(s, "Só Movimentações altera a quantidade de um lote, sempre na mesma transação que grava a movimentação (ADRs 0003 e 0006)", { x: 4.5, y: 6.55, w: 8.1, h: 0.45, fontSize: 13, italic: true, color: C.text2 });
  s.addNotes("Os quatro componentes de domínio sobre um modelo compartilhado. A regra 'só Movimentações escreve em lotes' veio de um apontamento do code-review (ADR 0006).");

  // ===== 9. Mudanças de rota =====
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Arquitetura" });
  etiqueta(s, "Roteiro · item 5");
  s.addText("Apontamentos das skills que mudaram a rota", { placeholder: "title" });
  const rotas = [
    ["grill · Q8", "\"Retirar de um lote só\" bloquearia retiradas comuns", "Retirada multi-lote FEFO (ADR 0002)"],
    ["grill · Q13", "Como corrigir um lançamento errado sem perder auditoria?", "Movimentações imutáveis; correção por ajuste (ADR 0003)"],
    ["code-review · Standards", "Monitoramento importava as rotas de Movimentações, violando o ADR 0004", "Modelo compartilhado; escrita só em Movimentações (ADR 0006)"],
    ["code-review · Standards", "Segredo JWT padrão no código; e-mails descobríveis pelo tempo de login", "Segredo obrigatório; login em tempo constante"],
    ["code-review · Spec", "Erros em inglês, README vazio, admin podia se autodesativar", "3 testes novos e correções"],
    ["retro", "Nenhum guardrail; termos proibidos do glossário voltavam ao código", "CI + checagem automática do glossário"],
  ];
  txt(s, "Origem", { x: 0.6, y: 1.35, w: 2.6, h: 0.3, fontSize: 12, bold: true, color: C.accent5 });
  txt(s, "O que a skill apontou", { x: 3.35, y: 1.35, w: 5.0, h: 0.3, fontSize: 12, bold: true, color: C.accent5 });
  txt(s, "Decisão resultante", { x: 8.65, y: 1.35, w: 4.0, h: 0.3, fontSize: 12, bold: true, color: C.accent5 });
  rotas.forEach(([o, a, d], i) => {
    const y = 1.75 + i * 0.86;
    cartao(s, 0.6, y, 12.1, 0.74, "rota-" + i, i % 2 ? C.background1 : C.background2);
    txt(s, o, { x: 0.8, y: y + 0.12, w: 2.5, h: 0.5, fontSize: 13, bold: true, color: C.accent1, valign: "middle" });
    txt(s, a, { x: 3.35, y: y + 0.08, w: 4.7, h: 0.58, fontSize: 13, valign: "middle" });
    s.addShape(pres.shapes.RIGHT_ARROW, { x: 8.2, y: y + 0.24, w: 0.3, h: 0.26, fill: { color: C.accent2 }, line: { color: C.accent2 }, objectName: "seta-rota-" + i });
    txt(s, d, { x: 8.65, y: y + 0.08, w: 3.95, h: 0.58, fontSize: 13, bold: true, color: C.text2, valign: "middle" });
  });
  s.addNotes("Todas as decisões estão versionadas em docs/adr e evidencias/. O ADR 0006 nasceu de um conflito entre dois ADRs anteriores, que só apareceu na revisão.");

  // ===== 10. Qualidade =====
  pres.addSection({ title: "Resultados" });
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Resultados" });
  etiqueta(s, "Roteiro · item 6");
  s.addText("Evidências de qualidade", { placeholder: "title" });
  const stats = [["71", "testes automatizados"], ["96%", "cobertura do código"], ["10/10", "tickets em red → green"], ["✓", "CI verde no GitHub"]];
  stats.forEach(([n, l], i) => {
    const x = 0.6 + i * 1.6, y = 1.45;
    // grid 2x2 on the left
    const gx = 0.6 + (i % 2) * 2.85, gy = 1.45 + Math.floor(i / 2) * 2.0;
    cartao(s, gx, gy, 2.65, 1.8, "stat-" + i);
    txt(s, n, { x: gx, y: gy + 0.2, w: 2.65, h: 0.95, fontSize: 48, bold: true, color: C.accent1, align: "center", valign: "middle" });
    txt(s, l, { x: gx + 0.15, y: gy + 1.2, w: 2.35, h: 0.45, fontSize: 14, align: "center", color: C.text1 });
  });
  txt(s, "Suíte em 4 s (era 77 s): bcrypt com 4 rounds só nos testes", { x: 0.6, y: 5.6, w: 5.5, h: 0.6, fontSize: 13, italic: true, color: C.accent5 });
  s.addChart(pres.charts.BAR, [{ name: "Testes", labels: ["01 Acesso", "02 Medicam.", "03 Entrada", "04 Retirada", "05 Devolução", "06 Descarte", "07 Alertas", "08 Auditoria", "09 Interface", "10 Seed"], values: [17, 8, 7, 11, 8, 5, 5, 5, 3, 2] }], {
    x: 6.5, y: 1.35, w: 6.2, h: 5.4, barDir: "bar", showTitle: true, title: "Testes por ticket", titleFontSize: 15, titleColor: HEX.dk2, titleFontFace: "+mn-lt",
    chartColors: [HEX.accent1], showValue: true, dataLabelPosition: "outEnd", dataLabelColor: HEX.dk1, dataLabelFontSize: 12, dataLabelFontFace: "+mn-lt",
    catAxisLabelColor: HEX.dk1, catAxisLabelFontSize: 12, catAxisLabelFontFace: "+mn-lt", catAxisOrientation: "maxMin",
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, showLegend: false, barGapWidthPct: 60,
  });
  s.addNotes("Os testes exercitam o sistema pela API, a seam combinada na spec, com relógio controlável para testar validade. Logs red/green de cada ticket em evidencias/logs.");

  // ===== 11. Defeitos =====
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Resultados" });
  etiqueta(s, "Roteiro · item 6");
  s.addText("Quem achou cada defeito", { placeholder: "title" });
  const H = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text2 } } });
  const defeitos = [
    [H("Defeito"), H("Encontrado por"), H("Corrigido")],
    ["Expiração do token comparava fusos diferentes", "tdd (red)", "✓"],
    ["Teste de validade expirava o próprio token", "tdd (red)", "✓"],
    ["Segredo JWT padrão no código", "code-review · Standards", "✓"],
    ["Enumeração de e-mails pelo tempo de login", "code-review · Standards", "✓"],
    ["Administrador podia se autodesativar", "code-review · ambos", "✓"],
    ["Mensagens de validação em inglês", "code-review · Spec", "✓"],
    ["README sem instruções de execução", "code-review · Spec", "✓"],
    ["Login visível após entrar; campos desalinhados", "verificação visual (sem skill)", "✓"],
  ];
  s.addTable(defeitos, { x: 0.6, y: 1.45, w: 8.4, colW: [4.6, 2.65, 1.15], fontSize: 14, color: C.text1, rowH: 0.52, valign: "middle", border: { type: "solid", pt: 0.75, color: "D5E3E3" }, objectName: "tabela-defeitos" });
  cartao(s, 9.4, 1.45, 3.3, 4.68, "cartao-leitura");
  iconeCirculo(s, I.bulb, 9.65, 1.7, 0.6, C.accent2, "icone-leitura");
  txt(s, [
    { text: "Leitura", options: { bold: true, fontSize: 17, color: C.text2, breakLine: true } },
    { text: "5 de 8 defeitos vieram do code-review, 3 deles de segurança.", options: { breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Os defeitos visuais só apareceram ao abrir a interface: nenhum teste de API os pegaria.", options: {} },
  ], { x: 9.65, y: 2.45, w: 2.85, h: 3.5, fontSize: 14 });
  s.addNotes("Relatório completo da revisão em evidencias/code-review-1.md, com a decisão tomada para cada achado, inclusive os que não corrigimos.");

  // ===== 12. Demo =====
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Resultados" });
  etiqueta(s, "Roteiro · item 6");
  s.addText("Demonstração", { placeholder: "title" });
  const demos = [
    ["ui-04-retirada-fefo-multilote.png", "Retirada de 40: o sistema tira 30 do lote que vence antes e 10 do seguinte"],
    ["ui-03-enfermeiro-controlado-negado.png", "Enfermeiro tenta retirar Diazepam (controlado): bloqueado"],
    ["ui-06-alertas.png", "Farmacêutico: alertas de reposição e de validade"],
  ];
  demos.forEach(([f, l], i) => {
    const y = i < 2 ? 1.4 + i * 2.75 : 1.4, x = i < 2 ? 0.6 : 6.95;
    const w = i < 2 ? 5.95 : 5.75, hImg = i < 2 ? w * 340 / 1280 : w * 450 / 1280;
    s.addImage({ path: IMG + f, x, y, w, h: hImg, objectName: "demo-" + i, altText: l });
    txt(s, l, { x, y: y + hImg + 0.1, w, h: 0.55, fontSize: 13, color: C.text1 });
  });
  cartao(s, 6.95, 4.25, 5.75, 2.35, "cartao-rodar", C.text2);
  txt(s, [
    { text: "Para rodar", options: { bold: true, fontSize: 16, color: C.background1, breakLine: true } },
    { text: "pip install -r requirements.txt", options: { fontFace: "Courier New", color: C.background2, breakLine: true } },
    { text: "python -m app", options: { fontFace: "Courier New", color: C.background2, breakLine: true } },
    { text: "→ http://localhost:8000 · senha demo12345", options: { color: C.accent4 } },
  ], { x: 7.2, y: 4.45, w: 5.3, h: 2.0, fontSize: 14, paraSpaceAfter: 4 });
  s.addNotes("Roteiro da demo ao vivo: 1) entrar como enfermeiro e retirar 40 dipironas, mostrando os dois lotes; 2) tentar Diazepam (bloqueado); 3) entrar como farmacêutico e mostrar alertas e auditoria. Plano B: estes prints.");

  // ===== 13. Skill mais útil =====
  pres.addSection({ title: "Análise" });
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Análise" });
  etiqueta(s, "Roteiro · item 7 · seção 5");
  s.addText("A skill mais útil: /code-review", { placeholder: "title" });
  cartao(s, 0.6, 1.45, 3.6, 5.3, "cartao-trofeu", C.text2);
  iconeCirculo(s, I.trophy, 1.95, 1.75, 0.9, C.accent2, "icone-trofeu");
  txt(s, [
    { text: "Mais usada", options: { fontSize: 13, color: C.background2, breakLine: true } },
    { text: "/tdd", options: { fontSize: 22, bold: true, color: C.background1, breakLine: true } },
    { text: "10 ciclos red → green", options: { fontSize: 13, italic: true, color: C.accent4, breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Mais valiosa", options: { fontSize: 13, color: C.background2, breakLine: true } },
    { text: "/code-review", options: { fontSize: 22, bold: true, color: C.background1, breakLine: true } },
    { text: "8 correções, 3 de segurança, 1 ADR novo", options: { fontSize: 13, italic: true, color: C.accent4 } },
  ], { x: 0.8, y: 2.9, w: 3.2, h: 3.6, align: "center" });
  const qs = [
    ["Qual foi a mais usada? E a mais valiosa?", "/tdd (todo ticket); /code-review, pelo que mudou no produto"],
    ["Em que fase contribuiu mais?", "Na revisão, quando os 68 testes já passavam e \"parecia pronto\""],
    ["O que fez melhor que uma instrução genérica?", "Dois subagentes de contexto limpo, com eixos separados; cobrou glossário e ADRs e leu o README"],
    ["Reduziu ambiguidade, defeitos, retrabalho?", "Defeitos: 8 corrigidos antes da entrega. Retrabalho: o conflito entre ADRs virou o ADR 0006 cedo"],
    ["Foi inadequada ou excessiva?", "Smells de baixo valor num projeto acadêmico (nomes curtos, Data Clumps)"],
    ["O que foi manual apesar dela?", "Decidir quais achados corrigir; a verificação visual da interface"],
    ["O que precisaria ser adaptado?", "Rodar a cada ticket, não só no fim; incluir checagem visual; ajustar a lista de smells ao porte"],
  ];
  qs.forEach(([q, a2], i) => {
    const y = 1.45 + i * 0.76;
    s.addShape(pres.shapes.OVAL, { x: 4.55, y: y + 0.05, w: 0.4, h: 0.4, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: "q-num-" + i });
    txt(s, String(i + 1), { x: 4.55, y: y + 0.05, w: 0.4, h: 0.4, fontSize: 13, bold: true, color: C.background1, align: "center", valign: "middle" });
    txt(s, [{ text: q, options: { bold: true, color: C.text2, breakLine: true } }, { text: a2 }], { x: 5.15, y, w: 7.55, h: 0.72, fontSize: 13 });
  });
  s.addNotes("O grill-with-docs foi o segundo mais valioso: moldou o domínio. Mas, sem a usuária respondendo (delegação), ele perdeu parte da função de tirar ambiguidade do humano. O code-review entregou valor independente de quem decidia.");

  // ===== 14. Funcionou / não =====
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Análise" });
  etiqueta(s, "Roteiro · item 7 · seção 5");
  s.addText("O que funcionou e o que precisou ser adaptado", { placeholder: "title" });
  cartao(s, 0.6, 1.45, 5.95, 5.3, "cartao-funcionou");
  iconeCirculo(s, I.check, 0.85, 1.65, 0.6, C.accent6, "icone-funcionou");
  txt(s, "Funcionou", { x: 1.6, y: 1.75, w: 4.5, h: 0.45, fontSize: 19, bold: true, color: C.text2 });
  txt(s, [
    { text: "Glossário único: os mesmos termos na spec, nos testes e no código", options: { bullet: true, breakLine: true } },
    { text: "ADRs escritos no momento da decisão, não depois", options: { bullet: true, breakLine: true } },
    { text: "Uma seam de teste (API) e relógio injetável: testes estáveis", options: { bullet: true, breakLine: true } },
    { text: "Revisão por subagentes, sem o viés de quem implementou", options: { bullet: true, breakLine: true } },
    { text: "retro transformou regra de texto em checagem automática", options: { bullet: true } },
  ], { x: 0.85, y: 2.45, w: 5.5, h: 4.1, fontSize: 16, paraSpaceAfter: 12 });
  cartao(s, 6.75, 1.45, 5.95, 5.3, "cartao-adaptado");
  iconeCirculo(s, I.warn, 7.0, 1.65, 0.6, C.accent2, "icone-adaptado");
  txt(s, "Adaptado ou não funcionou", { x: 7.75, y: 1.75, w: 4.8, h: 0.45, fontSize: 19, bold: true, color: C.text2 });
  txt(s, [
    { text: "Grill sem humano: delegamos as decisões ao agente, e a skill perdeu parte do sentido", options: { bullet: true, breakLine: true } },
    { text: "TDD por ticket (5–17 testes), não um teste por vez", options: { bullet: true, breakLine: true } },
    { text: "Interface como fatia horizontal, contra a regra de tracer bullets", options: { bullet: true, breakLine: true } },
    { text: "GitHub Issues indisponível para o agente: tracker local", options: { bullet: true, breakLine: true } },
    { text: "C4 e verificação visual feitos sem skill", options: { bullet: true } },
  ], { x: 7.0, y: 2.45, w: 5.5, h: 4.1, fontSize: 16, paraSpaceAfter: 12 });
  s.addNotes("Não comparamos com e sem skill de forma controlada: não temos evidência suficiente, e qualquer diferença poderia vir do modelo ou da tarefa. Registramos os desvios para não atribuir à skill o que foi escolha nossa.");

  // ===== 15. Aprendizados =====
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Análise" });
  etiqueta(s, "Roteiro · item 8");
  s.addText("Três aprendizados e o que faríamos diferente", { placeholder: "title" });
  const aprend = [
    [I.comments, "Skill de alinhamento precisa de humano", "O grill gera valor quando quem conhece o domínio responde. Delegar transforma pergunta em suposição.", "Responder as rodadas do grill nós mesmas, com um farmacêutico do Mário Penna"],
    [I.search, "Revisão independente pega o que o autor não vê", "Os 3 problemas de segurança passaram por 71 testes verdes.", "Rodar o code-review a cada ticket, não só no fim"],
    [I.cog, "Regra boa vira checagem, não instrução", "Termos do glossário voltavam ao código até virar script na CI.", "Criar CI e guardrails no ticket 01"],
  ];
  aprend.forEach(([ic, t, d, f], i) => {
    const x = 0.6 + i * 4.1;
    cartao(s, x, 1.45, 3.9, 5.3, "aprendizado-" + i);
    iconeCirculo(s, ic, x + 0.25, 1.7, 0.6, C.accent1, "icone-aprendizado-" + i);
    txt(s, t, { x: x + 0.25, y: 2.45, w: 3.4, h: 0.85, fontSize: 17, bold: true, color: C.text2 });
    txt(s, d, { x: x + 0.25, y: 3.35, w: 3.4, h: 1.5, fontSize: 14 });
    txt(s, [{ text: "Faríamos diferente", options: { bold: true, color: C.accent2, fontSize: 12, breakLine: true } }, { text: f }], { x: x + 0.25, y: 5.0, w: 3.4, h: 1.5, fontSize: 14 });
  });
  s.addNotes("Esses três aprendizados respondem diretamente ao item 8 da apresentação.");

  // ===== 16. Conclusão =====
  s = pres.addSlide({ masterName: "CAPA", sectionTitle: "Análise" });
  s.addText("Pergunta central: quando as skills mudam o desenvolvimento", { placeholder: "title" });
  s.addText([
    { text: "Mudam quando transformam etapas implícitas em artefatos verificáveis: glossário, ADRs, spec, tickets, testes e relatórios de revisão.", options: { breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Evidência: 6 mudanças de rota rastreáveis, 8 defeitos achados antes da entrega (5 pela revisão) e 71 testes com 96% de cobertura.", options: { breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Condição: um humano decidindo. Sem ele, a skill estrutura o trabalho, mas não reduz a ambiguidade real.", options: { bold: true } },
  ], { placeholder: "body" });
  s.addNotes("Resposta à pergunta central do enunciado. Repositório: github.com/BeatrizSamaha/ac-ia-skills");

  await pres.writeFile({ fileName: "/home/claude/build/apresentacao.pptx" });
  await applyTheme("/home/claude/build/apresentacao.pptx", THEME);
  console.log("ok");
})();
