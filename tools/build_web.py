#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vygeneruje projekty.html – jednostránkový katalog témat s vloženými daty."""
import json, re

VERSION = "2026.08.09-01"  # při každém buildu zvyš (RRRR.MM.DD-NN)

topics = []
for f in ["data/temata_sc4.json", "data/temata_sc1.json", "data/temata_sc5.json", "data/temata_sc8.json"]:
    topics += json.load(open(f, encoding="utf-8"))
topics.sort(key=lambda t: t["id"])
v3 = json.load(open("data/znalosti_v3.json", encoding="utf-8"))

def strip_source(s):
    s = re.sub(r"^ŠVP \(Ú[23/Ú]+\):\s*", "", s)
    s = re.sub(r"^RVP – ", "", s)
    return s

def strip_didaktika(s):
    return re.sub(r"^Didaktika SC\d:\s*", "", s)

for t in topics:
    ext = v3.get(str(t["id"]), {})
    t["znalosti"] = [strip_source(z) for z in ext.get("znalosti", []) if not z.startswith("—")] + \
                    [z for z in ext.get("znalosti", []) if z.startswith("—")]
    t["didaktika"] = [strip_didaktika(d) for d in ext.get("didaktika", [])]

DATA = json.dumps(topics, ensure_ascii=False)
import os
_kam_path = "kameny.json" if os.path.exists("kameny.json") else "data/kameny.json"
KAM = json.dumps(json.load(open(_kam_path, encoding="utf-8")), ensure_ascii=False)

# nastavení hlasování: jména se nezadávají dopředu, jen kapacity (kdo vede víc témat)
_uc_path = "data/ucitele.json"
_uc = json.load(open(_uc_path, encoding="utf-8")) if os.path.exists(_uc_path) else {}
VYCHOZI_POCET = str(int(_uc.get("vychozi_pocet", 1)))
KAPACITY = json.dumps({k: int(v) for k, v in _uc.get("kapacity", {}).items()}, ensure_ascii=False)

HTML = """<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Projekty 2026/27 – katalog témat</title>
<style>
  :root{
    --bg:#f6f5f2; --card:#ffffff; --ink:#1f2933; --muted:#6b7280; --line:#e5e2dc;
    --sc4:#b9770e; --sc1:#1f618d; --sc5:#922b21; --sc8:#1e8449;
    --sc4bg:#fdf3e3; --sc1bg:#e8f1f8; --sc5bg:#faeceb; --sc8bg:#e9f7ee;
  }
  *{box-sizing:border-box; margin:0; padding:0;}
  body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif; background:var(--bg); color:var(--ink); line-height:1.5;}
  header{background:#1f4e5f; color:#fff; padding:22px 16px 18px; text-align:center;}
  header h1{font-size:1.35rem; letter-spacing:.02em;}
  header p{opacity:.75; font-size:.85rem; margin-top:4px;}
  .toolbar{position:sticky; top:0; z-index:20; background:#fff; border-bottom:1px solid var(--line); box-shadow:0 3px 12px rgba(0,0,0,.07); padding:10px 12px 12px; display:flex; flex-direction:column; gap:8px;}
  .seg{display:flex; justify-content:center;}
  .seg .inner{display:inline-flex; border:1px solid var(--line); border-radius:10px; overflow:hidden;}
  .seg .chip{border:none; border-radius:0; padding:7px 18px; font-weight:600; background:#fff;}
  .seg .chip.active{background:#1f4e5f; color:#fff;}
  .tooldiv{border:none; border-top:1px solid var(--line); margin:2px 24px;}
  .filtry .chip{font-size:.76rem; padding:4px 10px; background:var(--bg);}
  .chips{display:flex; gap:6px; flex-wrap:wrap; justify-content:center;}
  .chip{border:1px solid var(--line); background:#fff; border-radius:999px; padding:5px 12px; font-size:.82rem; cursor:pointer; user-select:none; white-space:nowrap;}
  .chip.active{color:#fff; border-color:transparent;}
  .chip[data-sc="vse"].active{background:#1f4e5f;}
  .chip[data-sc="SC4"].active{background:var(--sc4);}
  .chip[data-sc="SC1"].active{background:var(--sc1);}
  .chip[data-sc="SC5"].active{background:var(--sc5);}
  .chip[data-sc="SC8"].active{background:var(--sc8);}
  .chip[data-tr].active{background:#374151;}
  
  .searchwrap{display:flex; justify-content:center;}
  #search{width:100%; max-width:420px; padding:8px 14px; border:1px solid var(--line); border-radius:999px; font-size:.9rem; background:#fff;}
  #count{text-align:center; font-size:.75rem; color:var(--muted);}
  main{max-width:1060px; margin:0 auto; padding:16px 12px 60px;}
  .grid{display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); grid-auto-rows:1fr; gap:12px;}
  .card{background:var(--card); border:1px solid var(--line); border-left:5px solid var(--accent); border-radius:12px; padding:14px 16px; cursor:pointer; transition:box-shadow .15s, transform .15s; display:flex; flex-direction:column;}
  .card:hover{box-shadow:0 4px 14px rgba(0,0,0,.08); transform:translateY(-1px);}
  .card .num{font-size:.72rem; color:var(--muted);}
  .card h3{font-size:1.02rem; margin:2px 0 6px;}
  .tagrow{display:flex; gap:6px; flex-wrap:wrap; margin-bottom:8px;}
  .tag{font-size:.68rem; padding:2px 8px; border-radius:999px; background:var(--accentbg); color:var(--accent); font-weight:600;}
  .tag.tr{background:#eef0f3; color:#4b5563; font-weight:500;}
  .card p{font-size:.83rem; color:#374151; flex:1;}
  .kam{margin-top:8px; font-size:.72rem; color:var(--muted);}
  /* detail */
  #overlay{position:fixed; inset:0; background:rgba(15,23,32,.55); z-index:50; display:none; align-items:flex-end; justify-content:center;}
  #overlay.open{display:flex;}
  #detail{background:#fff; width:100%; max-width:760px; max-height:92vh; overflow-y:auto; border-radius:18px 18px 0 0; padding:20px 20px 40px; -webkit-overflow-scrolling:touch;}
  @media(min-width:780px){ #overlay{align-items:center;} #detail{border-radius:18px; max-height:88vh;} }
  #detail .num{color:var(--muted); font-size:.8rem;}
  #detail h2{font-size:1.3rem; margin:2px 0 10px; color:var(--accent);}
  #detail .anot{font-size:.95rem; margin-bottom:14px;}
  #detail ul{padding-left:18px; font-size:.88rem; margin-top:6px;}
  #detail li{margin-bottom:4px;}
  #detail li.lead{font-weight:600;}
  /* kámen s úrovněmi */
  .kd{border:none !important; background:transparent !important; margin:0 0 2px 0 !important; padding:0 !important;}
  .kd>summary{padding:5px 0 !important; justify-content:flex-start !important; font-size:.88rem !important; text-transform:none !important; letter-spacing:0 !important; font-weight:400 !important; color:var(--ink) !important;}
  .kd>summary.lead{font-weight:600 !important;}
  .kd>summary::before{content:"▸"; color:var(--accent); margin-right:6px; transition:transform .15s; display:inline-block;}
  .kd[open]>summary::before{transform:rotate(90deg);}
  .kd>summary::after{content:"" !important;}
  .kdb{background:#f6f8f9; border-left:3px solid var(--accent); border-radius:0 8px 8px 0; padding:8px 12px 10px; margin:2px 0 8px 14px; font-size:.83rem;}
  .kdb b{color:var(--accent);}
  .kdb .urov{margin-bottom:6px;}
  .chipsmini{display:flex; gap:5px; flex-wrap:wrap; margin-top:6px;}
  .chipsmini button{border:1px solid var(--line); background:#fff; border-radius:999px; padding:2px 9px; font-size:.68rem; cursor:pointer; color:#4b5563;}
  .chipsmini button:hover{border-color:var(--accent); color:var(--accent);}
  #bubble{position:fixed; z-index:99; max-width:min(480px, calc(100vw - 32px)); background:#1f2933; color:#f3f4f6; border-radius:12px; padding:12px 14px; font-size:.82rem; line-height:1.45; box-shadow:0 8px 30px rgba(0,0,0,.35); display:none;}
  #bubble b{display:block; margin-bottom:4px; color:#93c5fd;}
  #detail details{border:1px solid var(--line); border-radius:10px; margin-top:8px; padding:0 12px; background:#fbfbfa;}
  #detail details[open]{padding-bottom:10px; background:#fff;}
  #detail summary{cursor:pointer; padding:10px 0; font-size:.8rem; text-transform:uppercase; letter-spacing:.05em; color:#374151; font-weight:600; list-style:none; display:flex; justify-content:space-between; align-items:center;}
  #detail summary::-webkit-details-marker{display:none;}
  #detail summary::after{content:"▾"; color:var(--muted); transition:transform .15s;}
  #detail details[open] summary::after{transform:rotate(180deg);}
  .closebtn{position:sticky; top:0; float:right; background:#eef0f3; border:none; border-radius:999px; width:34px; height:34px; font-size:1rem; cursor:pointer;}
  .difbox{background:#f7f7f5; border-radius:10px; padding:10px 12px; margin-top:6px; font-size:.85rem;}
  .difbox b{font-size:.8rem;}
  .loni{font-style:italic; color:var(--muted); font-size:.85rem;}
  footer{ text-align:center; font-size:.75rem; color:var(--muted); padding:20px;}
  .printbtn{position:sticky; top:0; float:right; background:#eef0f3; border:none; border-radius:999px; height:34px; padding:0 12px; font-size:.8rem; cursor:pointer; margin-right:8px;}
  /* rejstřík kamenů */
  #kamlist summary{list-style:none;}
  #kamlist summary::-webkit-details-marker{display:none;}
  #kamlist{max-width:760px; margin:0 auto;}
  #kamlist h3{margin:18px 0 6px; font-size:1rem;}
  #kamlist .kd{background:#fff !important; border:1px solid var(--line) !important; border-radius:10px !important; padding:2px 12px !important; margin-bottom:6px !important;}
  .temlink{color:var(--accent); cursor:pointer; text-decoration:underline;}
  .temrow{margin-top:8px; font-size:.83rem;}
  /* hlasování a rezervace */
  #hlas{max-width:600px; margin:0 auto;}
  #hlas h3{max-width:560px; margin:16px auto 8px; font-size:.95rem;}
  #hlas p.muted{max-width:560px; margin:0 auto 8px; font-size:.8rem;}
  .muted{color:var(--muted);}
  .hlasbox{max-width:480px; margin:0 auto 14px;}
  .hlasbox input, #hlasSearch{width:100%; padding:8px 12px; border:1px solid var(--line); border-radius:8px; font-size:.9rem; background:#fff;}
  .hlascol{max-width:560px; margin:0 auto 10px;}
  .hlaslist{max-height:320px; overflow-y:auto;}
  .hlasrow{display:flex; align-items:center; justify-content:space-between; gap:8px; padding:7px 10px; border:1px solid var(--line); border-radius:8px; margin-bottom:6px; background:#fff; font-size:.85rem; cursor:pointer;}
  .hlasrow.picked{border-color:#1f4e5f; background:#eef4f6;}
  .hlasnum{font-weight:700; min-width:22px; text-align:center; color:#1f4e5f;}
  #hlasMine{list-style:none; max-width:560px; margin:0 auto 10px; padding:0;}
  #hlasMine li{display:flex; align-items:center; gap:8px; padding:6px 8px; border-bottom:1px solid var(--line); font-size:.85rem;}
  #hlasMine button{border:1px solid var(--line); background:#fff; border-radius:6px; padding:2px 8px; font-size:.75rem; cursor:pointer;}
  #hlasSubmit{display:block; margin:10px auto; background:#1f4e5f; color:#fff; border:none; border-radius:999px; padding:9px 22px; font-size:.9rem; cursor:pointer;}
  #hlasMsg{text-align:center; font-size:.82rem; color:var(--muted); margin-top:4px;}
  #toggleResults{display:block; margin:14px auto; border:1px solid var(--line); background:#fff; border-radius:999px; padding:7px 16px; font-size:.85rem; cursor:pointer;}
  #hlasJmenoMsg{font-size:.78rem; margin-top:5px; min-height:1.1em;}
  #hlasJmenoMsg .varovani{color:#92400e; background:#fef6e7; border:1px solid #f3d9a4; border-radius:8px; padding:5px 9px; display:inline-block;}
  #hlasJmenoMsg button{border:1px solid var(--line); background:#fff; border-radius:999px; padding:2px 9px; font-size:.74rem; cursor:pointer; margin:0 4px;}
  #toggleNavrh{display:block; margin:14px auto; border:1px solid var(--line); background:#fff; border-radius:999px; padding:7px 16px; font-size:.85rem; cursor:pointer;}
  #navrhBox{max-width:600px; margin:0 auto;}
  #navrhBox table{width:100%; border-collapse:collapse; font-size:.82rem; margin-top:8px;}
  #navrhBox th, #navrhBox td{text-align:left; padding:6px 8px; border-bottom:1px solid var(--line); vertical-align:top;}
  #navrhBox th{font-size:.72rem; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); font-weight:600;}
  #navrhBox td.volba{white-space:nowrap; font-weight:600;}
  #navrhBox tr.fix td.volba{color:#1f4e5f;}
  #navrhBox tr.nic td{color:var(--muted); font-style:italic;}
  .navrhSouhrn{background:#eef4f6; border-radius:10px; padding:10px 12px; font-size:.83rem; margin-top:10px;}
  .navrhSouhrn b{color:#1f4e5f;}
  #rezList{max-width:560px; margin:0 auto;}
  #rezList .hlasrow{cursor:default;}
  #rezList button{border:1px solid var(--line); background:#fff; border-radius:999px; padding:4px 12px; font-size:.78rem; cursor:pointer;}
  /* tisk karty */
  @media print{
    body.print-card header, body.print-card .toolbar, body.print-card main,
    body.print-card footer, body.print-card #bubble, body.print-card .closebtn,
    body.print-card .printbtn{display:none !important;}
    body.print-card #overlay{position:static; display:block !important; background:none;}
    body.print-card #detail{max-height:none; overflow:visible; width:100%; max-width:100%; border-radius:0; padding:0;}
    body.print-card .chipsmini{display:none !important;}
    body.print-card #detail details{break-inside:avoid;}
  }
</style>
</head>
<body>
<header>
  <h1>Projekty 2026/27 — katalog témat</h1>
  <p>1. pololetí · ScioCíle 4, 1, 5 a 8 · 2. a 3. trojročí · klepni na kartu pro detail</p>
</header>

<div class="toolbar">
  <div class="seg"><div class="inner" id="viewChips">
    <span class="chip active" data-view="temata">Témata</span>
    <span class="chip" data-view="kameny">Rejstřík kamenů</span>
    <span class="chip" data-view="hlas">Hlasování</span>
  </div></div>
  <hr class="tooldiv">
  <div class="chips filtry" id="scChips">
    <span class="chip active" data-sc="vse">Vše</span>
    <span class="chip" data-sc="SC4">SC4 Odolnost</span>
    <span class="chip" data-sc="SC1">SC1 Umím se učit</span>
    <span class="chip" data-sc="SC5">SC5 Vztahy</span>
    <span class="chip" data-sc="SC8">SC8 Život v rukou</span>
  </div>
  <div class="chips filtry" id="trChips">
    <span class="chip active" data-tr="vse">Obě trojročí</span>
    <span class="chip" data-tr="2">Pro 2. trojročí</span>
    <span class="chip" data-tr="3">Pro 3. trojročí</span>
  </div>
  <div class="searchwrap"><input id="search" type="search" placeholder="Hledat v tématech, kamenech, aktivitách…"></div>
  <div id="count"></div>
</div>

<main><div class="grid" id="grid"></div><div id="kamlist" style="display:none"></div>
<div id="hlas" style="display:none">
  <p class="muted" id="hlasWarn" style="display:none; text-align:center; font-size:.8rem;">⚠ Modul hlasování se nenačetl — zkontroluj připojení k internetu a obnov stránku.</p>
  <div class="hlasbox"><label>Přihlaš se pod svým příjmením<br>
    <input id="hlasName" type="text" list="hlasZnami" autocomplete="off" placeholder="např. Nováková">
    <datalist id="hlasZnami"></datalist></label>
    <div id="hlasJmenoMsg"></div></div>

  <h3>Vyber a seřaď až 8 témat — první volba má nejvyšší váhu</h3>
  <div class="hlascol"><input id="hlasSearch" type="search" placeholder="Hledat téma…">
    <div class="hlaslist" id="hlasPickList"></div></div>

  <h3>Moje pořadí</h3>
  <ol id="hlasMine"></ol>
  <button id="hlasSubmit">Uložit hlasy</button>
  <div id="hlasMsg"></div>

  <hr class="tooldiv">
  <h3>Rezervace tématu</h3>
  <p class="muted">Jedno téma = jeden učitel. Klepnutím vyplň jméno výše, pak rezervuj nebo uvolni.</p>
  <div id="rezList"></div>

  <hr class="tooldiv">
  <button id="toggleResults">Zobrazit výsledky hlasování</button>
  <div id="hlasResults" style="display:none"></div>

  <hr class="tooldiv">
  <h3>Návrh rozdělení témat</h3>
  <p class="muted">Rozdělí témata tak, aby byl součet preferencí co největší.
  Už zarezervovaná témata bere jako dané. Nic nikam nezapíše — je to jen podklad.</p>
  <button id="toggleNavrh">Spočítat návrh</button>
  <div id="navrhBox" style="display:none"></div>
</div>
</main>

<div id="overlay"><div id="detail"></div></div>
<div id="bubble"></div>

<footer>ScioŠkola · katalog projektových témat · verze __VERSION__</footer>

<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<script>
const DATA = __DATA__;
const KAM = __KAM__;
const KAPACITY = __KAPACITY__, VYCHOZI_POCET = __VYCHOZI_POCET__;
let znamiUcitele = [];   // příjmení těch, kdo už hlasovali nebo mají rezervaci
const SCN = {SC4:"SC4 Rozvíjím svou odolnost", SC1:"SC1 Umím se učit", SC5:"SC5 Buduji dobré vztahy", SC8:"SC8 Mám život ve svých rukou"};
const COL = {SC4:["var(--sc4)","var(--sc4bg)"], SC1:["var(--sc1)","var(--sc1bg)"], SC5:["var(--sc5)","var(--sc5bg)"], SC8:["var(--sc8)","var(--sc8bg)"]};
const TRT = {"obě":"2. i 3. trojročí","2":"jen 2. trojročí","3":"jen 3. trojročí"};
let fSC="vse", fTR="vse", q="", view="temata";
// index: kámen -> témata
const KIDX = {};
for(const t of DATA){
  for(const k of t.vedouci){ const c=k.split(" ")[0].replace(/\\.$/,""); (KIDX[c]=KIDX[c]||{lead:[],side:[]}).lead.push(t); }
  for(const k of t.vedlejsi){ const c=k.split(" ")[0].replace(/\\.$/,""); (KIDX[c]=KIDX[c]||{lead:[],side:[]}).side.push(t); }
}

const sb = window.supabase ? window.supabase.createClient("https://iluznnvfvlpstipylhgg.supabase.co", "sb_publishable_brVec8GeC-v5GiiPuIHmoA_Kmp1zPLo") : null;
let myPicks = [], hlasInit = false, resultsShown = false;

const grid=document.getElementById("grid"), count=document.getElementById("count");
const overlay=document.getElementById("overlay"), detail=document.getElementById("detail");

function norm(s){return s.toLowerCase().normalize("NFD").replace(/[\\u0300-\\u036f]/g,"");}
function hay(t){return norm([t.nazev,t.anotace,t.vedouci.join(" "),t.vedlejsi.join(" "),t.aktivity.join(" "),(t.znalosti||[]).join(" ")].join(" "));}

function renderKam(){
  const nq=norm(q);
  const grpName = {"1":"ScioCíl 1: Umím se učit","4":"ScioCíl 4: Rozvíjím svou odolnost","5":"ScioCíl 5: Buduji dobré vztahy","8":"ScioCíl 8: Mám život ve svých rukou"};
  const codes = Object.keys(KAM).sort((a,b)=>a.localeCompare(b,undefined,{numeric:true}));
  let html="", cnt=0, lastG="";
  for(const c of codes){
    const sc = "SC"+c.split(".")[0];
    if(fSC!=="vse" && sc!==fSC) continue;
    const info = KAM[c];
    if(nq && !norm(c+" "+info.n+" "+info.u2+" "+info.u3).includes(nq)) continue;
    cnt++;
    const g = c.split(".")[0];
    if(g!==lastG){ html+=`<h3 style="color:var(--${sc.toLowerCase()})">${grpName[g]}</h3>`; lastG=g; }
    const idx = KIDX[c]||{lead:[],side:[]};
    let body="";
    if(info.u2) body+=`<div class="urov"><b>Úroveň 2 (2. trojročí):</b> ${info.u2}</div>`;
    if(info.u3) body+=`<div class="urov"><b>Úroveň 3 (3. trojročí):</b> ${info.u3}</div>`;
    const chips=["p","z","s","d"].filter(x=>info[x]).map(x=>`<button onclick="bub(event,'${c}','${x}')">${MTIT[x]}</button>`).join("");
    if(chips) body+=`<div class="chipsmini">${chips}</div>`;
    const lk = ts=>ts.map(t=>`<span class="temlink" onclick="openD(${t.id})">${t.id}. ${t.nazev}</span>`).join(", ");
    if(idx.lead.length) body+=`<div class="temrow"><b>Stěžejní v:</b> ${lk(idx.lead)}</div>`;
    if(idx.side.length) body+=`<div class="temrow"><b>Vedlejší v:</b> ${lk(idx.side)}</div>`;
    if(!idx.lead.length && !idx.side.length) body+=`<div class="temrow" style="color:var(--muted)">Zatím bez tématu.</div>`;
    html+=`<details class="kd" style="--accent:var(--${sc.toLowerCase()});--accentbg:var(--${sc.toLowerCase()}bg)"><summary>${c} ${info.n}</summary><div class="kdb">${body}</div></details>`;
  }
  document.getElementById("kamlist").innerHTML=html;
  count.textContent=`Zobrazeno ${cnt} ze ${Object.keys(KAM).length} kamenů`;
}
function render(){
  document.getElementById("grid").style.display = view==="temata" ? "" : "none";
  document.getElementById("kamlist").style.display = view==="kameny" ? "" : "none";
  document.getElementById("hlas").style.display = view==="hlas" ? "" : "none";
  document.getElementById("trChips").style.display = view==="temata" ? "" : "none";
  document.getElementById("scChips").style.display = view==="hlas" ? "none" : "";
  document.querySelector(".searchwrap").style.display = view==="hlas" ? "none" : "";
  count.style.display = view==="hlas" ? "none" : "";
  if(view==="kameny"){ renderKam(); return; }
  if(view==="hlas"){
    if(!hlasInit){ hlasInit=true; initHlas(); } else { loadMyVotes(); renderRez(); }
    return;
  }
  const nq=norm(q);
  const items=DATA.filter(t=>
    (fSC==="vse"||t.skupina===fSC) &&
    (fTR==="vse"||t.urovne==="obě"||t.urovne===fTR) &&
    (!nq||hay(t).includes(nq)));
  grid.innerHTML=items.map(t=>{
    const [c,cb]=COL[t.skupina];
    return `<div class="card" style="--accent:${c};--accentbg:${cb}" onclick="openD(${t.id})">
      <div class="num">Téma ${t.id}</div>
      <h3>${t.nazev}</h3>
      <div class="tagrow"><span class="tag">${SCN[t.skupina]}</span><span class="tag tr">${TRT[t.urovne]}</span></div>
      <p>${t.anotace}</p>
      <div class="kam">Kameny: ${t.vedouci.map(k=>k.split(" ")[0]).join(", ")}${t.vedlejsi.length?" + "+t.vedlejsi.map(k=>k.split(" ")[0]).join(", "):""}</div>
    </div>`;}).join("");
  count.textContent=`Zobrazeno ${items.length} z ${DATA.length} témat`;
}

const MTIT = {p:"Postoje", z:"Znalosti", s:"Sebeznalosti", d:"Dovednosti"};
function kamHtml(k, lead){
  const code = k.split(" ")[0].replace(/\\.$/,"");
  const info = KAM[code];
  if(!info || (!info.u2 && !info.u3 && !info.p && !info.z && !info.s && !info.d))
    return `<div style="padding:5px 0; font-size:.88rem; ${lead?"font-weight:600;":""}">${k}</div>`;
  let body = "";
  if(info.u2) body += `<div class="urov"><b>Úroveň 2 (2. trojročí):</b> ${info.u2}</div>`;
  if(info.u3) body += `<div class="urov"><b>Úroveň 3 (3. trojročí):</b> ${info.u3}</div>`;
  if(!info.u2 && !info.u3) body += `<div class="urov" style="color:var(--muted)">Úrovně u tohoto kamene zatím nejsou ve zdroji rozpracované.</div>`;
  const chips = ["p","z","s","d"].filter(x=>info[x]).map(x=>
    `<button onclick="bub(event,'${code}','${x}')">${MTIT[x]}</button>`).join("");
  if(chips) body += `<div class="chipsmini">${chips}</div>`;
  return `<details class="kd"><summary class="${lead?"lead":""}">${k}</summary><div class="kdb">${body}</div></details>`;
}
const bubble = document.getElementById("bubble");
function bub(e, code, cat){
  e.stopPropagation();
  const info = KAM[code]; if(!info) return;
  bubble.innerHTML = `<b>${MTIT[cat]} — ${code} ${info.n}</b>${info[cat]}`;
  bubble.style.display = "block";
  const r = e.target.getBoundingClientRect();
  bubble.style.left = Math.min(r.left, window.innerWidth - bubble.offsetWidth - 16) + "px";
  const above = r.top > window.innerHeight/2;
  bubble.style.top = above ? Math.max(8, r.top - bubble.offsetHeight - 8) + "px" : (r.bottom + 8) + "px";
}
document.addEventListener("click", e=>{ if(!bubble.contains(e.target) && !e.target.closest(".chipsmini")) bubble.style.display="none"; });
function openD(id){
  const t=DATA.find(x=>x.id===id); if(!t) return;
  const [c,cb]=COL[t.skupina];
  detail.style.setProperty("--accent",c);
  const sec=(title,body,open=false)=>`<details${open?" open":""}><summary>${title}</summary>${body}</details>`;
  let h=`<button class="closebtn" onclick="closeD()">✕</button>
    <button class="printbtn" onclick="printD()">🖨 Tisk</button>
    <div class="num">Téma ${t.id} · ${SCN[t.skupina]} · ${TRT[t.urovne]}</div>
    <h2>${t.nazev}</h2>
    <div class="anot">${t.anotace}</div>`;
  h+=sec("Stěžejní kameny",t.vedouci.map(k=>kamHtml(k,true)).join(""),true);
  h+=sec("Vedlejší kameny",t.vedlejsi.map(k=>kamHtml(k,false)).join(""));
  h+=sec("Náměty aktivit",`<ul>${t.aktivity.map(a=>`<li>${a}</li>`).join("")}</ul>`);
  if(t.znalosti&&t.znalosti.length) h+=sec("Tvrdé znalosti — příklady učiva",`<ul>${t.znalosti.map(z=>`<li>${z}</li>`).join("")}</ul>`);
  if(t.didaktika&&t.didaktika.length) h+=sec("Z didaktiky ScioCíle",`<ul>${t.didaktika.map(d=>`<li>${d}</li>`).join("")}</ul>`);
  let dif=`<div class="difbox">`;
  if(t.dif2!=="—") dif+=`<b>2. trojročí:</b> ${t.dif2}<br>`;
  dif+=`<b>3. trojročí:</b> ${t.dif3}</div>`;
  h+=sec("Diferenciace podle trojročí",dif);
  if(t.loni) h+=sec("Návaznost na projekty 2025/26",`<div class="loni">${t.loni}</div>`);
  detail.innerHTML=h;
  overlay.classList.add("open");
  document.body.style.overflow="hidden";
  detail.scrollTop=0;
  history.replaceState(null,"","#"+t.id);
}
function closeD(){overlay.classList.remove("open"); document.body.style.overflow=""; bubble.style.display="none"; history.replaceState(null,"",location.pathname+location.search);}
function printD(){
  detail.querySelectorAll("details").forEach(d=>d.open=true);
  document.body.classList.add("print-card");
  window.print();
}
window.addEventListener("afterprint",()=>document.body.classList.remove("print-card"));
function openFromHash(){
  const m=location.hash.match(/^#(\\d+)$/);
  if(m){ const id=parseInt(m[1]); if(DATA.some(t=>t.id===id)) openD(id); }
}
window.addEventListener("hashchange",openFromHash);
overlay.addEventListener("click",e=>{if(e.target===overlay) closeD();});
document.addEventListener("keydown",e=>{if(e.key==="Escape") closeD();});

/* Jména se nezadávají dopředu — každý se zapíše sám. Aby z překlepů nevznikali
   „noví“ lidé, appka napovídá z už zapsaných a na podobné jméno upozorní. */
function bezDiakritiky(s){ return s.toLowerCase().normalize("NFD").replace(/[\\u0300-\\u036f]/g,"").replace(/\\s+/g," ").trim(); }
function vzdalenost(a,b){            // Levenshtein, na hlídání překlepů
  const m=a.length, n=b.length;
  if(!m||!n) return m||n;
  let pred=[...Array(n+1).keys()];
  for(let i=1;i<=m;i++){
    const cur=[i];
    for(let j=1;j<=n;j++)
      cur[j]=Math.min(pred[j]+1, cur[j-1]+1, pred[j-1]+(a[i-1]===b[j-1]?0:1));
    pred=cur;
  }
  return pred[n];
}
function podobneJmeno(jm){
  const n=bezDiakritiky(jm);
  if(!n) return null;
  const shoda = znamiUcitele.find(u=>bezDiakritiky(u)===n && u!==jm);
  if(shoda) return {jmeno:shoda, stejne:true};        // liší se jen diakritikou/velikostí
  const blizko = znamiUcitele.filter(u=>{
    const d=vzdalenost(n,bezDiakritiky(u));
    return d>0 && d<=(n.length<=5?1:2);
  });
  return blizko.length ? {jmeno:blizko[0], stejne:false} : null;
}
async function nactiZname(){
  if(!sb) return;
  const [{data:v},{data:a}] = await Promise.all([
    sb.from("votes").select("teacher"), sb.from("assignments").select("teacher")
  ]);
  znamiUcitele = [...new Set([...(v||[]),...(a||[])].map(r=>r.teacher))].sort((x,y)=>x.localeCompare(y,"cs"));
  document.getElementById("hlasZnami").innerHTML = znamiUcitele.map(u=>`<option value="${u}">`).join("");
}
function zkontrolujJmeno(){
  const el=document.getElementById("hlasName"), box=document.getElementById("hlasJmenoMsg");
  const jm=el.value.trim();
  box.innerHTML="";
  if(!jm) return;
  const p=podobneJmeno(jm);
  if(!p){
    if(!znamiUcitele.includes(jm)) box.innerHTML=`<span class="muted">Zapisuješ se poprvé jako <b>${jm}</b>.</span>`;
    return;
  }
  box.innerHTML = p.stejne
    ? `<span class="varovani">Už tu hlasuje <b>${p.jmeno}</b> — použij stejný zápis.
       <button onclick="pouzijJmeno('${p.jmeno.replace(/'/g,"\\\\'")}')">Použít ${p.jmeno}</button></span>`
    : `<span class="varovani">Nemyslíš <b>${p.jmeno}</b>?
       <button onclick="pouzijJmeno('${p.jmeno.replace(/'/g,"\\\\'")}')">Ano, jsem ${p.jmeno}</button>
       <span class="muted">Jinak pokračuj, zapíšu tě jako ${jm}.</span></span>`;
}
function pouzijJmeno(jm){
  const el=document.getElementById("hlasName");
  el.value=jm; localStorage.setItem("hlasName",jm);
  zkontrolujJmeno(); loadMyVotes(); renderRez();
}
function initHlas(){
  if(!sb) document.getElementById("hlasWarn").style.display="";
  const nameEl = document.getElementById("hlasName");
  nameEl.value = localStorage.getItem("hlasName") || "";
  nactiZname().then(zkontrolujJmeno);
  nameEl.addEventListener("change", e=>{
    const jm=e.target.value.trim(); e.target.value=jm;
    localStorage.setItem("hlasName", jm);
    zkontrolujJmeno(); loadMyVotes(); renderRez();
  });
  document.getElementById("hlasSearch").addEventListener("input", renderPickList);
  document.getElementById("hlasSubmit").addEventListener("click", submitVotes);
  document.getElementById("toggleResults").addEventListener("click", toggleResults);
  document.getElementById("toggleNavrh").addEventListener("click", toggleNavrh);
  renderPickList();
  renderMine();
  loadMyVotes();
  renderRez();
}
function renderPickList(){
  const nq = norm(document.getElementById("hlasSearch").value);
  const items = DATA.filter(t=> !nq || hay(t).includes(nq));
  document.getElementById("hlasPickList").innerHTML = items.map(t=>{
    const i = myPicks.indexOf(t.id);
    return `<div class="hlasrow ${i>=0?"picked":""}" onclick="togglePick(${t.id})">
      <span>${t.id}. ${t.nazev}</span><span class="hlasnum">${i>=0?(i+1)+".":"+"}</span></div>`;
  }).join("");
}
function togglePick(id){
  const i = myPicks.indexOf(id);
  if(i>=0) myPicks.splice(i,1);
  else{
    if(myPicks.length>=8){ alert("Max. 8 témat — nejdřív nějaké odeber."); return; }
    myPicks.push(id);
  }
  renderPickList(); renderMine();
}
function movePick(i,d){
  const j=i+d; if(j<0||j>=myPicks.length) return;
  [myPicks[i],myPicks[j]]=[myPicks[j],myPicks[i]];
  renderPickList(); renderMine();
}
function renderMine(){
  const ol = document.getElementById("hlasMine");
  ol.innerHTML = myPicks.map((id,i)=>{
    const t = DATA.find(x=>x.id===id);
    return `<li><b>${i+1}.</b> ${t?t.nazev:id}
      <button onclick="movePick(${i},-1)" ${i===0?"disabled":""}>↑</button>
      <button onclick="movePick(${i},1)" ${i===myPicks.length-1?"disabled":""}>↓</button>
      <button onclick="togglePick(${id})">✕</button></li>`;
  }).join("") || `<li style="color:var(--muted); border-bottom:none;">Zatím nic nevybráno — klepni na téma v seznamu nahoře.</li>`;
}
async function loadMyVotes(){
  if(!sb) return;
  const name = document.getElementById("hlasName").value.trim();
  if(!name){ myPicks=[]; renderPickList(); renderMine(); return; }
  const {data,error} = await sb.from("votes").select("topic_id,rank").eq("teacher",name).order("rank");
  if(!error && data) myPicks = data.map(r=>r.topic_id);
  renderPickList(); renderMine();
}
async function submitVotes(){
  const msg = document.getElementById("hlasMsg");
  if(!sb){ msg.textContent="Hlasování není momentálně dostupné."; return; }
  const name = document.getElementById("hlasName").value.trim();
  if(!name){ msg.textContent="Nejdřív napiš své příjmení."; return; }
  if(!myPicks.length){ msg.textContent="Vyber aspoň jedno téma."; return; }
  localStorage.setItem("hlasName", name);
  msg.textContent = "Ukládám…";
  await sb.from("votes").delete().eq("teacher",name);
  const rows = myPicks.map((id,i)=>({teacher:name, topic_id:id, rank:i+1}));
  const {error} = await sb.from("votes").insert(rows);
  msg.textContent = error ? "Chyba: "+error.message : "Uloženo ✓ ("+rows.length+" hlasů)";
  if(!error) nactiZname();
}
async function renderRez(){
  const el = document.getElementById("rezList");
  if(!sb){ el.innerHTML = `<p class="muted">Rezervace nejsou momentálně dostupné.</p>`; return; }
  const {data} = await sb.from("assignments").select("topic_id,teacher");
  const map = {}; (data||[]).forEach(r=>map[r.topic_id]=r.teacher);
  const name = document.getElementById("hlasName").value.trim();
  el.innerHTML = DATA.map(t=>{
    const who = map[t.id];
    let action;
    if(!who) action = `<button onclick="reserve(${t.id})">Rezervovat</button>`;
    else if(name && who===name) action = `<button onclick="unreserve(${t.id})">Uvolnit</button>`;
    else action = `<span class="muted">obsazeno: ${who}</span>`;
    return `<div class="hlasrow"><span>${t.id}. ${t.nazev}</span>${action}</div>`;
  }).join("");
}
async function reserve(id){
  if(!sb) return;
  const name = document.getElementById("hlasName").value.trim();
  if(!name){ alert("Nejdřív napiš své příjmení nahoře."); return; }
  localStorage.setItem("hlasName", name);
  const {error} = await sb.from("assignments").insert({topic_id:id, teacher:name});
  if(error) alert("Téma už má někdo rezervované.");
  renderRez();
}
async function unreserve(id){
  if(!sb) return;
  const name = document.getElementById("hlasName").value.trim();
  await sb.from("assignments").delete().eq("topic_id",id).eq("teacher",name);
  renderRez();
}
async function toggleResults(){
  resultsShown = !resultsShown;
  const box = document.getElementById("hlasResults");
  box.style.display = resultsShown ? "" : "none";
  document.getElementById("toggleResults").textContent = resultsShown ? "Skrýt výsledky" : "Zobrazit výsledky hlasování";
  if(!resultsShown) return;
  if(!sb){ box.innerHTML = `<p class="muted">Výsledky nejsou momentálně dostupné.</p>`; return; }
  const {data} = await sb.from("vote_results").select("*");
  box.innerHTML = (data||[]).map(r=>{
    const t = DATA.find(x=>x.id===r.topic_id);
    return `<div class="hlasrow" style="cursor:default"><span>${t?t.id+". "+t.nazev:r.topic_id}</span><span>${r.skore} b. (${r.pocet_hlasu} hlasů)</span></div>`;
  }).join("") || `<p class="muted">Zatím žádné hlasy.</p>`;
}

/* --- návrh rozdělení témat -------------------------------------------------
   Maďarský algoritmus (Kuhn–Munkres) — najde rozdělení s největším součtem
   preferencí, ne jen slušný odhad. Ověřeno proti hrubé síle. */
function hungarian(a, n, m){
  const u=new Array(n+1).fill(0), v=new Array(m+1).fill(0);
  const p=new Array(m+1).fill(0), way=new Array(m+1).fill(0);
  for(let i=1;i<=n;i++){
    p[0]=i; let j0=0;
    const minv=new Array(m+1).fill(Infinity), used=new Array(m+1).fill(false);
    do{
      used[j0]=true;
      const i0=p[j0]; let delta=Infinity, j1=0;
      for(let j=1;j<=m;j++) if(!used[j]){
        const cur=a[i0][j]-u[i0]-v[j];
        if(cur<minv[j]){ minv[j]=cur; way[j]=j0; }
        if(minv[j]<delta){ delta=minv[j]; j1=j; }
      }
      for(let j=0;j<=m;j++){
        if(used[j]){ u[p[j]]+=delta; v[j]-=delta; }
        else minv[j]-=delta;
      }
      j0=j1;
    } while(p[j0]!==0);
    do{ const j1=way[j0]; p[j0]=p[j1]; j0=j1; } while(j0);
  }
  const res=new Array(n+1).fill(0);
  for(let j=1;j<=m;j++) if(p[j]) res[p[j]]=j;
  return res;
}
function rozdel(slots, topics, score){
  const n=slots.length, m=topics.length;
  if(!n||!m) return [];
  const flip = n>m;                       // algoritmus vyžaduje řádků <= sloupců
  const R=flip?m:n, C=flip?n:m;
  const a=Array.from({length:R+1},()=>new Array(C+1).fill(0));
  for(let i=1;i<=R;i++) for(let j=1;j<=C;j++){
    const s = flip ? score(slots[j-1],topics[i-1]) : score(slots[i-1],topics[j-1]);
    a[i][j] = -s;                         // minimalizace záporných bodů = maximalizace
  }
  const res=hungarian(a,R,C), out=[];
  for(let i=1;i<=R;i++){
    const j=res[i]; if(!j) continue;
    const slot  = flip?slots[j-1]:slots[i-1];
    const topic = flip?topics[i-1]:topics[j-1];
    const s=score(slot,topic);
    if(s>0) out.push({slot,topic,score:s});   // 0 = o téma nikdo nestojí
  }
  return out;
}
async function toggleNavrh(){
  const box=document.getElementById("navrhBox"), btn=document.getElementById("toggleNavrh");
  const open = box.style.display==="none";
  box.style.display = open ? "" : "none";
  btn.textContent = open ? "Skrýt návrh" : "Spočítat návrh";
  if(!open) return;
  if(!sb){ box.innerHTML=`<p class="muted">Návrh není momentálně dostupný.</p>`; return; }
  box.innerHTML=`<p class="muted">Počítám…</p>`;
  const [{data:votes},{data:rez}] = await Promise.all([
    sb.from("votes").select("teacher,topic_id,rank"),
    sb.from("assignments").select("topic_id,teacher")
  ]);
  const hlasy=votes||[], rezervace=rez||[];
  if(!hlasy.length && !rezervace.length){ box.innerHTML=`<p class="muted">Zatím nikdo nehlasoval.</p>`; return; }

  // body: první volba 8, poslední 1
  const bod={};
  for(const h of hlasy) bod[h.teacher+"|"+h.topic_id] = 9-h.rank;

  // rezervace jsou dané — učiteli uberou jeden slot, tématu možnost jít jinam
  const pevne = rezervace.map(r=>({ucitel:r.teacher, id:r.topic_id, fix:true, body:bod[r.teacher+"|"+r.topic_id]||0}));
  const obsazena = new Set(rezervace.map(r=>r.topic_id));

  // učitelé = ti, kdo se zapsali (hlasovali nebo mají rezervaci)
  const ucitele = [...new Set([...hlasy,...rezervace].map(r=>r.teacher))].sort((a,b)=>a.localeCompare(b,"cs"));
  const kapacita = u => (KAPACITY[u]!==undefined ? KAPACITY[u] : VYCHOZI_POCET);
  const zbyva = {};
  for(const u of ucitele) zbyva[u] = kapacita(u);
  for(const r of rezervace) if(zbyva[r.teacher]!==undefined) zbyva[r.teacher]--;

  // sloty = učitel × zbývající kapacita
  const slots=[];
  for(const u of ucitele) for(let k=0;k<Math.max(0,zbyva[u]);k++) slots.push(u);
  const volna = DATA.map(t=>t.id).filter(id=>!obsazena.has(id));
  const navrh = rozdel(slots, volna, (ucitel,id)=>bod[ucitel+"|"+id]||0)
                  .map(x=>({ucitel:x.slot, id:x.topic, fix:false, body:x.score}));

  const vse=[...pevne,...navrh].sort((a,b)=>a.ucitel.localeCompare(b.ucitel,"cs"));
  const nazev=id=>{ const t=DATA.find(x=>x.id===id); return t?`${t.id}. ${t.nazev}`:id; };
  const poradi=(u,id)=>{ const h=hlasy.find(x=>x.teacher===u&&x.topic_id===id); return h?h.rank+". volba":"nehlasoval"; };

  let html=`<table><tr><th>Učitel</th><th>Téma</th><th>Volba</th></tr>`;
  for(const r of vse) html+=`<tr class="${r.fix?"fix":""}"><td>${r.ucitel}</td><td>${nazev(r.id)}${r.fix?" <span class='muted'>(rezervováno)</span>":""}</td><td class="volba">${poradi(r.ucitel,r.id)}</td></tr>`;
  const bezTematu = ucitele.filter(u=>!vse.some(r=>r.ucitel===u));
  for(const u of bezTematu) html+=`<tr class="nic"><td>${u}</td><td>— bez tématu —</td><td class="volba">—</td></tr>`;
  html+=`</table>`;

  const prvni=vse.filter(r=>poradi(r.ucitel,r.id)==="1. volba").length;
  const soucet=vse.reduce((a,r)=>a+r.body,0);
  html+=`<div class="navrhSouhrn">Zapsaných učitelů: <b>${ucitele.length}</b> ·
    rozdělených témat: <b>${vse.length}</b> z ${DATA.length} ·
    první volbu dostalo <b>${prvni}</b> z ${vse.length} ·
    součet preferencí <b>${soucet}</b> bodů.`;
  if(bezTematu.length) html+=`<br>Bez tématu: ${bezTematu.join(", ")}.`;
  html+=`</div>`;
  box.innerHTML=html;
}

document.getElementById("scChips").addEventListener("click",e=>{
  if(!e.target.dataset.sc) return;
  fSC=e.target.dataset.sc;
  [...e.currentTarget.children].forEach(ch=>ch.classList.toggle("active",ch===e.target));
  render();});
document.getElementById("trChips").addEventListener("click",e=>{
  if(!e.target.dataset.tr) return;
  fTR=e.target.dataset.tr;
  [...e.currentTarget.children].forEach(ch=>ch.classList.toggle("active",ch===e.target));
  render();});
document.getElementById("search").addEventListener("input",e=>{q=e.target.value; render();});
document.getElementById("viewChips").addEventListener("click",e=>{
  if(!e.target.dataset.view) return;
  view=e.target.dataset.view;
  [...e.currentTarget.children].forEach(ch=>ch.classList.toggle("active",ch===e.target));
  render();});
render();
openFromHash();
</script>
</body>
</html>
"""

html = (HTML.replace("__DATA__", DATA).replace("__KAM__", KAM)
            .replace("__KAPACITY__", KAPACITY).replace("__VYCHOZI_POCET__", VYCHOZI_POCET)
            .replace("__VERSION__", VERSION))
open("index.html", "w", encoding="utf-8", newline="\n").write(html)
print(f"OK index.html ({len(html)//1024} kB, {len(topics)} témat, verze {VERSION})")
