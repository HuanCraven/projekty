const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  PageBreak, LevelFormat, convertMillimetersToTwip,
  BorderStyle, ShadingType,
} = require("docx");

const files = ["data/temata_sc4.json", "data/temata_sc1.json", "data/temata_sc5.json", "data/temata_sc8.json"];
let topics = [];
for (const f of files) topics = topics.concat(JSON.parse(fs.readFileSync(f, "utf8")));
const v3 = JSON.parse(fs.readFileSync("data/znalosti_v3.json", "utf8"));
const stripSrc = z => z.replace(/^ŠVP \(Ú[23\/Ú]+\):\s*/, "").replace(/^RVP – /, "");
const stripDid = d => d.replace(/^Didaktika SC\d:\s*/, "");

const GROUPS = [
  { key: "SC4", nazev: "ScioCíl 4: Rozvíjím svou odolnost", color: "B9770E",
    uvod: "Odolnost jako schopnost unést tlak, neúspěch a nejistotu, zotavit se a růst. Témata pokrývají oba pilíře ScioCíle: prevenci (péče o tělo a duši — spánek, strava, pohyb, duševní pohoda) i akci (zvládání stresu a zátěže, práce s neúspěchem, cílené opouštění komfortní zóny).",
    didaktika: [
      "Nejdřív bezpečí, pak výzvy — bez pocitu bezpečí se odolnost nebuduje, ale boří.",
      "Tři zóny (komfort – rozvoj – ohrožení): zátěž dávkovat středně a často, v malých dávkách; nikdy nepracovat v zóně ohrožení.",
      "Regulační techniky (dech, uzemnění) nacvičovat v klidu — v krizi se nové věci nenaučíme.",
      "Postup od vnější regulace přes koregulaci s průvodcem k seberegulaci; oporu odebírat podle kompetence, ne věku (Kotva → Kompas → Kormidlo).",
      "Kolbův cyklus: zážitek bez reflexe a opakovaného vyzkoušení se nepromění v odolnost — reflexe je povinná část programu.",
      "Raději skutečné školní a životní situace než uměle vyrobené zátěže; zvláštní citlivost u dětí s PAS, ADHD a u senzitivních dětí.",
    ] },
  { key: "SC1", nazev: "ScioCíl 1: Umím se učit", color: "1F618D",
    uvod: "Kompetence celoživotního učení: nástroje a zdroje učení (AI, věda, hra, umění, lidé, kritické posouzení zdrojů) a řízení vlastního učení (cíle, plánování, strategie, motivace, reflexe). Řada témat dělá z učení samotného předmět zkoumání.",
    didaktika: [
      "Obsah je nosič, učební vrstva je cíl — „učit se učit“ jde jen na konkrétním obsahu; každé téma projektu je zároveň tréninkem učení.",
      "Postupné předávání řízení: JÁ (průvodce modeluje, přemýšlí nahlas) → MY (spoluřízení) → TY (dítě řídí, průvodce jistí); role Vedený → Spolunavigátor → Kapitán.",
      "Každý projektový den: plánovací čtvrthodina dětí na startu, porovnání plánu se skutečností na konci.",
      "Krátká častá reflexe procesu (Co? A co z toho? Co teď?) je účinnější než dlouhá reflexe jednou za čas.",
      "Učit ověřené strategie (aktivní vybavování, rozložené opakování, prokládání) a vyvracet mýty (učební styly, podtrhávání).",
      "AI: u každého použití si položit otázku „učí mě to, nebo to dělá za mě?“",
    ] },
  { key: "SC5", nazev: "ScioCíl 5: Buduji dobré vztahy", color: "922B21",
    uvod: "Kvalita vztahů určuje kvalitu života. Témata pokrývají sociální gramotnost (skupiny, tlak, konflikty, hranice), budování trvalých vztahů (přátelství, rodina, partnerství) i komunikaci (dialog, asertivita, angličtina, digitální komunikace)." },
  { key: "SC8", nazev: "ScioCíl 8: Mám život ve svých rukou", color: "1E8449",
    uvod: "Aktivní řízení vlastního života: cíle a motivace, praktická samostatnost (peníze, domácnost, výroba, doprava, krize a první pomoc, právo) a vědomé nakládání s časem, vzděláváním a prací." },
];

const P = (text, opts = {}) => new Paragraph({
  children: [new TextRun({ text, ...opts.run })],
  spacing: { after: opts.after ?? 120 },
  ...opts.para,
});

const bullet = (text, bold = false) => new Paragraph({
  children: [new TextRun({ text, bold })],
  numbering: { reference: "bul", level: 0 },
  spacing: { after: 40 },
});

const label = (text) => new Paragraph({
  children: [new TextRun({ text, bold: true, color: "444444", size: 20 })],
  spacing: { before: 120, after: 40 },
});

// urovne = seznam trojročí, ve kterých je téma použitelné (např. "1,2,3" nebo "3")
function urovText(u) {
  const t = String(u).split(",").map(x => x.trim()).filter(Boolean).sort();
  if (!t.length) return "";
  if (t.length === 1) return `primárně ${t[0]}. trojročí`;
  if (t.length === 3) return "1.–3. trojročí";
  return t.map(x => x + ".").join(" i ") + " trojročí";
}

const children = [];

// ---------- titul ----------
children.push(
  new Paragraph({ spacing: { before: 2400 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "PROJEKTY 2026/27", bold: true, size: 64 })], spacing: { after: 200 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Katalog témat pro 1. pololetí podle ScioCílů", size: 36, color: "555555" })], spacing: { after: 200 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: `${topics.length} námětů pro 1.–3. trojročí — ScioCíle 4, 1, 5 a 8`, size: 24, color: "888888" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "pracovní verze k rozebrání témat průvodci", italics: true, size: 20, color: "888888" })], spacing: { before: 200 } }),
  new Paragraph({ children: [new PageBreak()] }),
);

// ---------- úvod ----------
children.push(
  new Paragraph({ text: "Jak s katalogem pracovat", heading: HeadingLevel.HEADING_1 }),
  P("Od školního roku 2026/27 řídíme program Projektů pomocí ScioCílů namísto dosavadních okruhů RVP (člověk a společnost, příroda a svět, věda a technika, umění a kultura). Je to v souladu s Východisky a principy ScioŠkol 2026 („obsahem vzdělávání ve ScioŠkolách jsou ScioCíle“) i s naším ŠVP, kde jsou Projekty jednou z vyučovacích forem předmětu Galaktika a dvakrát ročně vrcholí konferencí projektů. První pololetí pokrývá čtyři nejlépe připravené ScioCíle: SC4 Rozvíjím svou odolnost, SC1 Umím se učit, SC5 Buduji dobré vztahy a SC8 Mám život ve svých rukou."),
  P(`Tento katalog nabízí ${topics.length} témat, z nichž si dvojice průvodců vybírají a rozpracovávají je do konkrétních Projektů (celodenní předmět, cca 220 minut včetně přestávek, obvykle 4 týdny). Témata jsou náměty, ne osnovy — volnost průvodců i dětí zůstává zachována; projekt může téma uchopit i jinak, pokud rozvíjí uvedené kameny.`),
  P("Každé téma má:", { after: 40 }),
  bullet("Stěžejní kameny — jádro projektu; to, co se děti mají skutečně posunout (obvykle 1–3 kameny)."),
  bullet("Vedlejší kameny — přirozené přesahy rozvíjené v menší míře; často propojují více ScioCílů."),
  bullet("Anotaci a náměty aktivit — inspiraci pro stavbu programu (přednáška, praktická a hravá výuka, výlety, exkurze, videa, hraní rolí…)."),
  bullet("Tvrdé znalosti — příklady učiva, které se v projektu přirozeně nabízí učit. Čerpají ze dvou zdrojů: z učiva úrovní 2 a 3 našeho ŠVP (položky „ŠVP“; úroveň 2 ≈ 6. ročník, úroveň 3 ≈ 9. ročník) a z revidovaného RVP ZV schváleného v prosinci 2024 (položky „RVP“ podle nových vzdělávacích oblastí a očekávaných výsledků učení). Jsou to náměty, ne povinný výčet. Pozn.: ŠVP položky jsou zatím jen u témat SC1 a SC4 — část ŠVP s cíli 5–8 nebyla v podkladu čitelná."),
  bullet("Z didaktiky ScioCíle — vybraná doporučení z didaktik SC1 a SC4 (u kapitol shrnutí pro průvodce, u některých témat konkrétní tipy a ověřené formáty z praxe ScioŠkol)."),
  bullet("Diferenciaci — jak téma uchopit v 1. trojročí (úroveň 1), ve 2. trojročí (úroveň 2) a ve 3. trojročí (úroveň 3). Většina témat je společná všem třem; u témat omezených na jedno trojročí je uvedeno „jen N. trojročí“ a vypsaná je jen příslušná úroveň."),
  bullet("Návaznost na projekty 2025/26 — kde lze čerpat z loňských příprav a zkušeností kolegů."),
  P("", { after: 40 }),
  P("Doporučený postup: každý blok pololetí může mít doporučený vedoucí ScioCíl (např. blok 1 = SC4, blok 2 = SC1…), přiřazení ale není pevné — skupiny podle SC slouží především k orientaci a k hlídání vyváženosti nabídky v každém trojročí. Souhrnná tabulka pro rozebírání témat a přehled pokrytí všech kamenů jsou v souboru Projektova_temata.xlsx."),
  P("Úrovně kamenů: ScioCíle popisují u každého kamene úrovně 0–5. Pro 1. trojročí cílíme zpravidla na úroveň 1 (≈ 3. ročník), pro 2. trojročí na úroveň 2 (≈ 6. ročník) a pro 3. trojročí na úroveň 3 (≈ 9. ročník) — stejně to má nastavené naše ŠVP; diferenciace u témat z toho vychází."),
  P("Zdroje: upgrady ScioCílů 1, 4, 5, 8 (2025/26); ŠVP „Cesty k rozkvětu“ (ScioŠkola Dejvice); Východiska a principy ScioŠkol 2026; didaktiky SC1 a SC4; revidované RVP ZV (schváleno 30. 12. 2024, náběh od 2025/26); harmonogram a zásobník projektů 2025/26.", { run: { italics: true, color: "777777" } }),
  new Paragraph({ children: [new PageBreak()] }),
  new Paragraph({ text: "Přehled témat", heading: HeadingLevel.HEADING_1 }),
);
for (const g of GROUPS) {
  children.push(new Paragraph({
    children: [new TextRun({ text: g.nazev, bold: true, color: g.color, size: 24 })],
    spacing: { before: 160, after: 60 },
  }));
  for (const t of topics.filter(x => x.skupina === g.key)) {
    const extra = String(t.urovne).split(",").length === 1 ? `  (jen ${String(t.urovne).trim()}. trojročí)` : "";
    children.push(new Paragraph({
      children: [
        new TextRun({ text: `${t.id}. ${t.nazev}`, size: 21 }),
        new TextRun({ text: extra, italics: true, color: "888888", size: 19 }),
        new TextRun({ text: `  —  ${t.vedouci.map(k => k.split(" ")[0]).join(", ")}`, color: "666666", size: 19 }),
      ],
      indent: { left: 300 },
      spacing: { after: 30 },
    }));
  }
}
children.push(new Paragraph({ children: [new PageBreak()] }));

// ---------- kapitoly ----------
for (const g of GROUPS) {
  children.push(
    new Paragraph({ text: g.nazev, heading: HeadingLevel.HEADING_1, pageBreakBefore: true }),
    P(g.uvod, { after: 240, run: { italics: true, color: "555555" } }),
  );
  if (g.didaktika) {
    children.push(label("Jak na to podle didaktiky ScioCíle (shrnutí pro průvodce)"));
    for (const d of g.didaktika) children.push(bullet(d));
    children.push(new Paragraph({ spacing: { after: 200 } }));
  }
  for (const t of topics.filter(x => x.skupina === g.key)) {
    children.push(new Paragraph({
      text: `${t.id}. ${t.nazev}`, heading: HeadingLevel.HEADING_2,
    }));
    children.push(new Paragraph({
      children: [new TextRun({ text: urovText(t.urovne), bold: true, size: 20, color: g.color })],
      shading: { type: ShadingType.CLEAR, fill: "F4F4F4" },
      spacing: { after: 120 },
    }));
    children.push(P(t.anotace));
    children.push(label("Stěžejní kameny"));
    for (const k of t.vedouci) children.push(bullet(k, true));
    children.push(label("Vedlejší kameny"));
    for (const k of t.vedlejsi) children.push(bullet(k));
    children.push(label("Náměty aktivit"));
    for (const a of t.aktivity) children.push(bullet(a));
    const ext = v3[String(t.id)] || {};
    if (ext.znalosti) {
      children.push(label("Tvrdé znalosti — příklady učiva"));
      for (const z of ext.znalosti) children.push(bullet(stripSrc(z)));
    }
    if (ext.didaktika) {
      children.push(label("Z didaktiky ScioCíle"));
      for (const d of ext.didaktika) children.push(bullet(stripDid(d)));
    }
    children.push(label("Diferenciace"));
    if (t.dif1 && t.dif1 !== "—") children.push(bullet("1. trojročí: " + t.dif1));
    if (t.dif2 && t.dif2 !== "—") children.push(bullet("2. trojročí: " + t.dif2));
    if (t.dif3 && t.dif3 !== "—") children.push(bullet("3. trojročí: " + t.dif3));
    if (t.loni) {
      children.push(label("Návaznost na projekty 2025/26"));
      children.push(P(t.loni, { run: { italics: true, color: "555555" } }));
    }
    children.push(new Paragraph({
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC" } },
      spacing: { after: 240 },
    }));
  }
}

const doc = new Document({
  styles: {
    default: {
      document: { run: { font: "Arial", size: 21 }, paragraph: { spacing: { line: 276 } } },
      heading1: { run: { font: "Arial", size: 32, bold: true, color: "1F4E5F" }, paragraph: { spacing: { before: 240, after: 160 } } },
      heading2: { run: { font: "Arial", size: 26, bold: true, color: "222222" }, paragraph: { spacing: { before: 280, after: 100 } } },
    },
  },
  numbering: {
    config: [{
      reference: "bul",
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 360, hanging: 200 } } },
      }],
    }],
  },
  features: { updateFields: true },
  sections: [{
    properties: {
      page: { margin: {
        top: convertMillimetersToTwip(20), bottom: convertMillimetersToTwip(20),
        left: convertMillimetersToTwip(22), right: convertMillimetersToTwip(20),
      } },
    },
    children,
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("vystupy/Katalog_projektovych_temat.docx", buf);
  console.log("OK docx, témat:", topics.length);
});
