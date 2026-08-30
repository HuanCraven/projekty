#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vygeneruje projekty.html – jednostránkový katalog témat s vloženými daty."""
import json, re

VERSION = "2026.08.30-02"  # při každém buildu zvyš (RRRR.MM.DD-NN)

topics = []
for f in ["data/temata_sc4.json", "data/temata_sc1.json", "data/temata_sc5.json", "data/temata_sc8.json"]:
    topics += json.load(open(f, encoding="utf-8"))
topics.sort(key=lambda t: t["id"])
v3 = json.load(open("data/znalosti_v3.json", encoding="utf-8"))

def strip_source(s):
    s = re.sub(r"^ŠVP \(Ú\d(?:/Ú\d)*\):\s*", "", s)
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


# klíče ke ScioCílům (metodika) — seskupené podle kódu kamene
_kl_path = "data/klice.json"
_kl = json.load(open(_kl_path, encoding="utf-8")).get("klice", []) if os.path.exists(_kl_path) else []
_klice_map = {}
for _k in _kl:
    _klice_map.setdefault(_k["kod"], []).append(
        {"o": _k["otazka"], "p": _k["pojmy"], "v": _k["vybrany"], "t": _k["kratka"]})
KLICE = json.dumps(_klice_map, ensure_ascii=False)

# přípravy z minulých let — seskupené podle id tématu
_pr_path = "data/pripravy.json"
_pr = json.load(open(_pr_path, encoding="utf-8")) if os.path.exists(_pr_path) else {}
_pripravy_map = {}
for _s in _pr.get("slozky", []):
    for _tid in _s.get("temata", []):
        _pripravy_map.setdefault(str(_tid), []).append(
            {"n": _s["slozka"], "s": _s["souboru"], "o": _s["obsahuje"]})
PRIPRAVY = json.dumps(_pripravy_map, ensure_ascii=False)
PRIPRAVY_ODKAZ = json.dumps(_pr.get("_odkaz", ""), ensure_ascii=False)

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
  /* se čtyřmi záložkami se přepínač na úzkých displejích nevejde */
  @media(max-width:430px){
    .seg .chip{padding:7px 9px; font-size:.8rem;}
  }
  @media(max-width:340px){
    .seg{overflow-x:auto; -webkit-overflow-scrolling:touch;}
    .seg .inner{flex:0 0 auto;}
  }
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
  .hlasinfo{max-width:560px; margin:0 auto 16px; background:#eef4f6; border:1px solid #cfe0e6;
            border-left:4px solid #1f4e5f; border-radius:10px; padding:11px 14px; font-size:.85rem; line-height:1.5;}
  .hlasinfo b{color:#1f4e5f;}
  .hlasbox{max-width:480px; margin:0 auto 14px;}
  .hlasbox input, #hlasSearch{width:100%; padding:8px 12px; border:1px solid var(--line); border-radius:8px; font-size:.9rem; background:#fff;}
  .hlascol{max-width:560px; margin:0 auto 10px;}
  .hlaslist{max-height:320px; overflow-y:auto;}
  .hlasrow{display:flex; align-items:center; justify-content:space-between; gap:8px; padding:7px 10px; border:1px solid var(--line); border-radius:8px; margin-bottom:6px; background:#fff; font-size:.85rem; cursor:pointer;}
  .hlasrow.picked{border-color:#1f4e5f; background:#eef4f6;}
  .hlasnum{font-weight:700; min-width:22px; text-align:center; color:#1f4e5f;}
  #hlasSubmit{display:block; margin:10px auto; background:#1f4e5f; color:#fff; border:none; border-radius:999px; padding:9px 22px; font-size:.9rem; cursor:pointer;}
  #hlasMsg{text-align:center; font-size:.82rem; color:var(--muted); margin-top:4px;}
  #toggleResults{display:block; margin:14px auto; border:1px solid var(--line); background:#fff; border-radius:999px; padding:7px 16px; font-size:.85rem; cursor:pointer;}
  #exportCsv{display:block; margin:6px auto 0; border:none; background:none; color:var(--muted); font-size:.78rem; text-decoration:underline; cursor:pointer;}
  /* návod */
  #navod{max-width:720px; margin:0 auto; background:#fff; border:1px solid var(--line); border-radius:14px; padding:20px 22px 26px;}
  #navod h2{font-size:1.25rem; color:#1f4e5f; margin-bottom:10px;}
  #navod h3{font-size:.98rem; color:#1f4e5f; margin:20px 0 7px; padding-top:14px; border-top:1px solid var(--line);}
  #navod p{font-size:.88rem; margin-bottom:8px;}
  #navod p.lead{font-size:.92rem; color:#374151;}
  #navod code{background:var(--bg); border-radius:5px; padding:1px 5px; font-size:.84em;}
  .nav-dl{font-size:.88rem;}
  .nav-dl dt{font-weight:600; color:var(--ink); margin-top:9px;}
  .nav-dl dd{margin:2px 0 0 0; padding-left:12px; border-left:2px solid var(--line); color:#374151;}
  .nav-ol{font-size:.88rem; padding-left:20px; margin-top:6px;}
  .nav-ol li{margin-bottom:7px; color:#374151;}
  .navklic{font-size:.8rem;}
  /* klíče ke ScioCílům (metodika) */
  .klic{margin-top:8px; border-top:1px dashed var(--line); padding-top:7px;}
  .klic>summary{cursor:pointer; list-style:none; font-size:.8rem; color:var(--accent); font-weight:600; display:flex; gap:6px; align-items:flex-start;}
  .klic>summary::-webkit-details-marker{display:none;}
  .klic>summary::before{content:"🔑"; font-size:.8rem; flex:0 0 auto;}
  .klic[open]>summary{margin-bottom:6px;}
  .klicbody{font-size:.83rem; line-height:1.5;}
  .klicbody p{margin-bottom:6px;}
  .klicpojmy{margin:4px 0 7px; font-size:.74rem; color:var(--muted);}
  .klicpojmy span{display:inline-block; background:#eef0f3; border-radius:999px; padding:2px 8px; margin:2px 3px 0 0;}
  .klicvyb{background:#fef6e7; color:#92400e; border-radius:999px; padding:1px 7px; font-size:.68rem; font-weight:600; white-space:nowrap;}
  .klicai{margin-top:7px; font-size:.7rem; color:var(--muted); font-style:italic;}
  /* přípravy z minulých let */
  .pripbox{background:#f7f7f5; border-radius:10px; padding:10px 12px; margin-top:6px; font-size:.85rem;}
  .pripbox .p{display:flex; justify-content:space-between; gap:8px; padding:4px 0; border-bottom:1px solid var(--line);}
  .pripbox .p:last-of-type{border-bottom:none;}
  .pripbox .pn{font-weight:600;}
  .pripbox .po{font-size:.72rem; color:var(--muted);}
  .pripbox a{color:var(--accent);}
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
  .blok{max-width:560px; margin:0 auto 14px; border:1px solid var(--line); border-radius:12px; padding:10px 12px; background:#fbfcfc;}
  .blok h4{display:flex; align-items:center; justify-content:space-between; gap:8px; margin:0 0 6px; font-size:.88rem; color:#1f4e5f;}
  .blok .pocet{font-size:.75rem; color:var(--muted); border:1px solid var(--line); border-radius:999px; padding:1px 8px; background:#fff; white-space:nowrap;}
  .blok .pocet.hotovo{color:#1f4e5f; border-color:#1f4e5f; background:#eef4f6; font-weight:600;}
  .blok .hlaslist{max-height:230px;}
  .blokvyber{font-size:.8rem; margin-bottom:8px;}
  .blokvyber b{color:#1f4e5f;}
  button.prohod{border:1px solid var(--line); background:#fff; border-radius:999px; padding:2px 9px; font-size:.74rem; cursor:pointer; margin-left:6px;}
  h4.navrhblok{max-width:560px; margin:14px auto 4px; font-size:.85rem; color:#1f4e5f;}
  p.chybi{max-width:560px; margin:6px auto 0; font-size:.8rem; color:#92400e; background:#fef6e7; border:1px solid #f3d9a4; border-radius:8px; padding:6px 10px;}
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
  <p>1. pololetí · ScioCíle 4, 1, 5 a 8 · 1.–3. trojročí · klepněte na kartu pro detail</p>
</header>

<div class="toolbar">
  <div class="seg"><div class="inner" id="viewChips">
    <span class="chip active" data-view="temata">Témata</span>
    <span class="chip" data-view="kameny">Rejstřík kamenů</span>
    <span class="chip" data-view="hlas">Hlasování</span>
    <span class="chip" data-view="navod">Návod</span>
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
    <span class="chip active" data-tr="vse">Všechna trojročí</span>
    <span class="chip" data-tr="1">Pro 1. trojročí</span>
    <span class="chip" data-tr="2">Pro 2. trojročí</span>
    <span class="chip" data-tr="3">Pro 3. trojročí</span>
  </div>
  <div class="searchwrap"><input id="search" type="search" placeholder="Hledat v tématech, kamenech, aktivitách…"></div>
  <div id="count"></div>
</div>

<main><div class="grid" id="grid"></div><div id="kamlist" style="display:none"></div>
<div id="navod" style="display:none">
  <h2>Jak se v katalogu vyznat</h2>
  <p class="lead">Katalog obsahuje 50 projektových témat na 1. pololetí 2026/27.
  Ke každému tématu najdete anotaci, náměty aktivit, napojení na ScioCíle a to,
  jak ho pojmout v různých trojročích. Nemusíte nic instalovat ani se registrovat —
  odkaz si můžete uložit na plochu telefonu.</p>

  <h3>Záložky nahoře</h3>
  <dl class="nav-dl">
    <dt>Témata</dt><dd>Dlaždice všech témat katalogu. Klepnutím na kartu se otevře detail.</dd>
    <dt>Rejstřík kamenů</dt><dd>Obrácený pohled — vyjdete od stavebního kamene ScioCíle
      a uvidíte, ve kterých tématech se naplňuje. Užitečné, když potřebujete doložit
      konkrétní kámen.</dd>
    <dt>Hlasování</dt><dd>Výběr témat, která chcete vést, a rezervace.
      <b>Hlasování běží</b> — v každém ze čtyř bloků si vyberte dvě témata,
      1. a 2. volbu.</dd>
    <dt>Návod</dt><dd>Tahle stránka.</dd>
  </dl>

  <h3>Hledání a filtry</h3>
  <p>Pole <b>Hledat</b> prohledává názvy, anotace, aktivity, kameny i tvrdé znalosti —
  klidně napište „konflikt“ nebo „rozpočet“ a uvidíte, kde se to objevuje.
  Diakritiku ani velikost písmen řešit nemusíte.</p>
  <p>Filtry <b>SC4 / SC1 / SC5 / SC8</b> zúží výběr na jeden ScioCíl,
  filtr <b>trojročí</b> ukáže jen témata vhodná pro danou skupinu.
  V rejstříku kamenů hledání funguje i na odborné pojmy z klíčů
  (zkuste „Dunbar“ nebo „prokrastinace“).</p>

  <h3>Co najdete v detailu tématu</h3>
  <dl class="nav-dl">
    <dt>Stěžejní a vedlejší kameny</dt><dd>Rozklikněte kámen a uvidíte, co znamená
      v 1., 2. a 3. trojročí. Štítky <i>Postoje / Znalosti / Sebeznalosti / Dovednosti</i>
      otevřou přesné znění ze ScioCílů.</dd>
    <dt>Náměty aktivit</dt><dd>Pět konkrétních návrhů, co se dá dělat. Není to program,
      ale zásobník — vyberte si a doplňte svoje.</dd>
    <dt>Tvrdé znalosti</dt><dd>Příklady učiva, které se dá v tématu přirozeně probrat.
      Hodí se, když potřebujete ukázat, že projekt není „jen zážitek“.</dd>
    <dt>Diferenciace podle trojročí</dt><dd>Jak stejné téma pojmout s mladšími a jak
      se staršími. Většina témat je použitelná napříč.</dd>
    <dt>Klíč <span class="navklic">🔑</span></dt><dd>Metodika Scia k danému kameni:
      otázka, klíčové pojmy a krátká odpověď opřená o výzkum.
      <b>Tyhle texty psala AI a nikdo je nekontroloval</b> — berte je jako dobrý
      odrazový můstek, ne jako ověřený pramen. Plné klíče jsou na Disku.</dd>
    <dt>Přípravy z minulých let</dt><dd>U témat, která už se u nás v nějaké podobě
      dělala, uvidíte složky s loňskými materiály. Samotné soubory jsou na Google Disku.</dd>
  </dl>

  <h3>Tisk a sdílení</h3>
  <p>V detailu tématu je vpravo nahoře tlačítko <b>🖨 Tisk</b> — vytiskne jen tu jednu
  kartu, hodí se na poradu nebo pro rodiče. Adresa v prohlížeči se u otevřeného tématu
  mění (např. <code>…/#14</code>), takže jde poslat odkaz přímo na konkrétní téma.</p>

  <h3>Hlasování krok za krokem</h3>
  <ol class="nav-ol">
    <li><b>Napište si příjmení.</b> Nikde se předem neregistrujete. Kdo přijde po vás,
      uvidí vaše jméno v našeptávači — a když ho napíše trochu jinak, appka se zeptá,
      jestli nemyslel vás. Tím se hlídá, aby z překlepů nevznikli dva lidé.</li>
    <li><b>V každém bloku vyberte dvě témata.</b> Blok je jeden měsíc a jeden ScioCíl
      pro celou školu; v každém bloku vznikne devět projektů, každý s garantem a tandemem.
      První klepnutí je 1. volba, druhé 2. volba — tlačítkem <i>prohodit pořadí</i> je
      vyměníte. Celkem tedy vybíráte osm témat, dvě do každého ze čtyř bloků.</li>
    <li><b>Uložte hlasy.</b> Můžete se kdykoli vrátit a přepsat je — uvidíte svůj poslední
      výběr.</li>
    <li><b>Rezervace</b> je něco jiného než hlas: kdo si téma rezervuje, je jeho garant
      a návrh s tím počítá jako s daným. Používejte ji, až když je jasno.</li>
    <li><b>Spočítat návrh</b> rozdělí projekty ve dvou kolech: nejdřív dá každému projektu
      garanta z těch, kdo pro téma hlasovali, pak k němu doplní tandem. Garantství se
      rozdělují co nejrovnoměrněji — nikdo nedostane druhé, dokud nemají první všichni
      ostatní. <b>Nic to nezapisuje</b> — je to jen podklad k rozhodnutí u stolu.</li>
  </ol>

  <h3>Když něco nesedí</h3>
  <p>Katalog není hotová věc. Když v tématu najdete chybu, chybějící kámen nebo vás
  napadne lepší aktivita, řekněte Huanovi — data se dají opravit a web se přegeneruje.
  Totéž platí pro klíče: pokud v nich narazíte na nesmysl, je to očekávatelné
  (viz upozornění výše) a stojí za to to nahlásit.</p>
</div>
<div id="hlas" style="display:none">
  <p class="muted" id="hlasWarn" style="display:none; text-align:center; font-size:.8rem;">⚠ Modul hlasování se nenačetl — zkontroluj připojení k internetu a obnov stránku.</p>
  <div class="hlasinfo">
    <b>Hlasování běží.</b>
    Napiš si příjmení a v každém ze čtyř bloků vyber dvě témata, která bys chtěl/a vést.
    Hlasy můžeš kdykoli přepsat — platí vždycky to poslední, co uložíš.
  </div>
  <div class="hlasbox"><label>Přihlaš se pod svým příjmením<br>
    <input id="hlasName" type="text" list="hlasZnami" autocomplete="off" placeholder="např. Nováková">
    <datalist id="hlasZnami"></datalist></label>
    <div id="hlasJmenoMsg"></div></div>

  <h3>V každém bloku si vyber dvě témata</h3>
  <p class="muted">Pololetí má čtyři bloky a každý blok patří jednomu ScioCíli — celá škola
  dělá v jednom měsíci projekty k jednomu cíli. V každém bloku vznikne devět projektů,
  každý s garantem a tandemem. Klepni v každém bloku na dvě témata: první klepnutí je
  1. volba, druhé 2. volba.</p>
  <div class="hlascol"><input id="hlasSearch" type="search" placeholder="Hledat téma…"></div>
  <div id="hlasBloky"></div>
  <button id="hlasSubmit">Uložit hlasy</button>
  <div id="hlasMsg"></div>

  <hr class="tooldiv">
  <h3>Rezervace tématu</h3>
  <p class="muted">Jedno téma = jeden učitel. Klepnutím vyplň jméno výše, pak rezervuj nebo uvolni.</p>
  <div id="rezList"></div>

  <hr class="tooldiv">
  <button id="toggleResults">Zobrazit výsledky hlasování</button>
  <div id="hlasResults" style="display:none"></div>
  <button id="exportCsv" title="Stáhne aktuální hlasy i rezervace do souboru — záloha pro případ, že by se data ztratila.">Stáhnout hlasy jako CSV</button>

  <hr class="tooldiv">
  <h3>Návrh rozdělení projektů</h3>
  <p class="muted">Počítá ve dvou kolech: nejdřív dá každému projektu garanta — jen z těch,
  kdo pro dané téma hlasovali — a tím se vybere i devítka témat na blok. Pak k projektům
  doplní tandem: přednost mají hlasující, a když preference dojdou, doplní se kdokoli další.
  Garantství rozděluje co nejrovnoměrněji. Rezervované téma bere jako dané.
  Nic nikam nezapíše — je to jen podklad.</p>
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
const KLICE = __KLICE__;
const PRIPRAVY = __PRIPRAVY__, PRIPRAVY_ODKAZ = __PRIPRAVY_ODKAZ__;
let znamiUcitele = [];   // příjmení těch, kdo už hlasovali nebo mají rezervaci
const SCN = {SC4:"SC4 Rozvíjím svou odolnost", SC1:"SC1 Umím se učit", SC5:"SC5 Buduji dobré vztahy", SC8:"SC8 Mám život ve svých rukou"};
const COL = {SC4:["var(--sc4)","var(--sc4bg)"], SC1:["var(--sc1)","var(--sc1bg)"], SC5:["var(--sc5)","var(--sc5bg)"], SC8:["var(--sc8)","var(--sc8bg)"]};
/* urovne = seznam trojročí, ve kterých je téma použitelné, např. "1,2,3" nebo "3".
   Popisek se z něj skládá, takže unese i budoucí kombinace („2,3“ apod.). */
function trt(u){
  const t = String(u).split(",").map(x=>x.trim()).filter(Boolean).sort();
  if(t.length === 0) return "";
  if(t.length === 1) return `jen ${t[0]}. trojročí`;
  if(t.length === 3) return "1.–3. trojročí";
  return t.map(x=>x+".").join(" a ") + " trojročí";
}
function proTrojrocí(u, tr){ return String(u).split(",").map(x=>x.trim()).includes(tr); }
let fSC="vse", fTR="vse", q="", view="temata";
// index: kámen -> témata
const KIDX = {};
for(const t of DATA){
  for(const k of t.vedouci){ const c=k.split(" ")[0].replace(/\\.$/,""); (KIDX[c]=KIDX[c]||{lead:[],side:[]}).lead.push(t); }
  for(const k of t.vedlejsi){ const c=k.split(" ")[0].replace(/\\.$/,""); (KIDX[c]=KIDX[c]||{lead:[],side:[]}).side.push(t); }
}

const sb = window.supabase ? window.supabase.createClient("https://iluznnvfvlpstipylhgg.supabase.co", "sb_publishable_brVec8GeC-v5GiiPuIHmoA_Kmp1zPLo") : null;
let myPicks = {}, hlasInit = false, resultsShown = false;

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
    const kt = (KLICE[c]||[]).map(k=>k.o+" "+k.p.join(" ")).join(" ");
    if(nq && !norm(c+" "+info.n+" "+info.u1+" "+info.u2+" "+info.u3+" "+kt).includes(nq)) continue;
    cnt++;
    const g = c.split(".")[0];
    if(g!==lastG){ html+=`<h3 style="color:var(--${sc.toLowerCase()})">${grpName[g]}</h3>`; lastG=g; }
    const idx = KIDX[c]||{lead:[],side:[]};
    let body="";
    if(info.u1) body+=`<div class="urov"><b>Úroveň 1 (1. trojročí):</b> ${info.u1}</div>`;
    if(info.u2) body+=`<div class="urov"><b>Úroveň 2 (2. trojročí):</b> ${info.u2}</div>`;
    if(info.u3) body+=`<div class="urov"><b>Úroveň 3 (3. trojročí):</b> ${info.u3}</div>`;
    const chips=["p","z","s","d"].filter(x=>info[x]).map(x=>`<button onclick="bub(event,'${c}','${x}')">${MTIT[x]}</button>`).join("");
    if(chips) body+=`<div class="chipsmini">${chips}</div>`;
    const lk = ts=>ts.map(t=>`<span class="temlink" onclick="openD(${t.id})">${t.id}. ${t.nazev}</span>`).join(", ");
    if(idx.lead.length) body+=`<div class="temrow"><b>Stěžejní v:</b> ${lk(idx.lead)}</div>`;
    if(idx.side.length) body+=`<div class="temrow"><b>Vedlejší v:</b> ${lk(idx.side)}</div>`;
    if(!idx.lead.length && !idx.side.length) body+=`<div class="temrow" style="color:var(--muted)">Zatím bez tématu.</div>`;
    body += klicHtml(c);
    html+=`<details class="kd" style="--accent:var(--${sc.toLowerCase()});--accentbg:var(--${sc.toLowerCase()}bg)"><summary>${c} ${info.n}</summary><div class="kdb">${body}</div></details>`;
  }
  document.getElementById("kamlist").innerHTML=html;
  count.textContent=`Zobrazeno ${cnt} ze ${Object.keys(KAM).length} kamenů`;
}
function render(){
  document.getElementById("grid").style.display = view==="temata" ? "" : "none";
  document.getElementById("kamlist").style.display = view==="kameny" ? "" : "none";
  document.getElementById("hlas").style.display = view==="hlas" ? "" : "none";
  document.getElementById("navod").style.display = view==="navod" ? "" : "none";
  const bezFiltru = (view==="hlas" || view==="navod");
  document.getElementById("trChips").style.display = view==="temata" ? "" : "none";
  document.getElementById("scChips").style.display = bezFiltru ? "none" : "";
  document.querySelector(".searchwrap").style.display = bezFiltru ? "none" : "";
  count.style.display = bezFiltru ? "none" : "";
  if(view==="navod") return;
  if(view==="kameny"){ renderKam(); return; }
  if(view==="hlas"){
    if(!hlasInit){ hlasInit=true; initHlas(); } else { loadMyVotes(); renderRez(); }
    return;
  }
  const nq=norm(q);
  const items=DATA.filter(t=>
    (fSC==="vse"||t.skupina===fSC) &&
    (fTR==="vse"||proTrojrocí(t.urovne, fTR)) &&
    (!nq||hay(t).includes(nq)));
  grid.innerHTML=items.map(t=>{
    const [c,cb]=COL[t.skupina];
    return `<div class="card" style="--accent:${c};--accentbg:${cb}" onclick="openD(${t.id})">
      <div class="num">Téma ${t.id}</div>
      <h3>${t.nazev}</h3>
      <div class="tagrow"><span class="tag">${SCN[t.skupina]}</span><span class="tag tr">${trt(t.urovne)}</span></div>
      <p>${t.anotace}</p>
      <div class="kam">Kameny: ${t.vedouci.map(k=>k.split(" ")[0]).join(", ")}${t.vedlejsi.length?" + "+t.vedlejsi.map(k=>k.split(" ")[0]).join(", "):""}</div>
    </div>`;}).join("");
  count.textContent=`Zobrazeno ${items.length} z ${DATA.length} témat`;
}

const MTIT = {p:"Postoje", z:"Znalosti", s:"Sebeznalosti", d:"Dovednosti"};

/* Klíče ke ScioCílům — metodika Scia k jednotlivým kamenům. Texty generovala
   AI a nejsou kontrolované člověkem, proto to u každého klíče říkáme nahlas. */
function klicHtml(code){
  const ks = KLICE[code];
  if(!ks || !ks.length) return "";
  return ks.map(k=>`<details class="klic">
    <summary><span>${k.o}</span>${k.v?`<span class="klicvyb">vybraný</span>`:""}</summary>
    <div class="klicbody">
      ${k.p.length?`<div class="klicpojmy">${k.p.map(p=>`<span>${p}</span>`).join("")}</div>`:""}
      <p>${k.t.split("\\n").filter(x=>x.trim()).join("</p><p>")}</p>
      <div class="klicai">Klíč ke ScioCílům (Scio). Text generovala AI, není kontrolovaný člověkem.</div>
    </div></details>`).join("");
}
function kamHtml(k, lead){
  const code = k.split(" ")[0].replace(/\\.$/,"");
  const info = KAM[code];
  if(!info || (!info.u1 && !info.u2 && !info.u3 && !info.p && !info.z && !info.s && !info.d && !KLICE[code]))
    return `<div style="padding:5px 0; font-size:.88rem; ${lead?"font-weight:600;":""}">${k}</div>`;
  let body = "";
  if(info.u1) body += `<div class="urov"><b>Úroveň 1 (1. trojročí):</b> ${info.u1}</div>`;
  if(info.u2) body += `<div class="urov"><b>Úroveň 2 (2. trojročí):</b> ${info.u2}</div>`;
  if(info.u3) body += `<div class="urov"><b>Úroveň 3 (3. trojročí):</b> ${info.u3}</div>`;
  if(!info.u1 && !info.u2 && !info.u3) body += `<div class="urov" style="color:var(--muted)">Úrovně u tohoto kamene zatím nejsou ve zdroji rozpracované.</div>`;
  const chips = ["p","z","s","d"].filter(x=>info[x]).map(x=>
    `<button onclick="bub(event,'${code}','${x}')">${MTIT[x]}</button>`).join("");
  if(chips) body += `<div class="chipsmini">${chips}</div>`;
  body += klicHtml(code);
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
    <div class="num">Téma ${t.id} · ${SCN[t.skupina]} · ${trt(t.urovne)}</div>
    <h2>${t.nazev}</h2>
    <div class="anot">${t.anotace}</div>`;
  h+=sec("Stěžejní kameny",t.vedouci.map(k=>kamHtml(k,true)).join(""),true);
  h+=sec("Vedlejší kameny",t.vedlejsi.map(k=>kamHtml(k,false)).join(""));
  h+=sec("Náměty aktivit",`<ul>${t.aktivity.map(a=>`<li>${a}</li>`).join("")}</ul>`);
  if(t.znalosti&&t.znalosti.length) h+=sec("Tvrdé znalosti — příklady učiva",`<ul>${t.znalosti.map(z=>`<li>${z}</li>`).join("")}</ul>`);
  if(t.didaktika&&t.didaktika.length) h+=sec("Z didaktiky ScioCíle",`<ul>${t.didaktika.map(d=>`<li>${d}</li>`).join("")}</ul>`);
  let dif=`<div class="difbox">`;
  if(t.dif1 && t.dif1!=="—") dif+=`<b>1. trojročí:</b> ${t.dif1}<br>`;
  if(t.dif2!=="—") dif+=`<b>2. trojročí:</b> ${t.dif2}<br>`;
  dif+=`<b>3. trojročí:</b> ${t.dif3}</div>`;
  h+=sec("Diferenciace podle trojročí",dif);
  if(t.loni) h+=sec("Návaznost na projekty 2025/26",`<div class="loni">${t.loni}</div>`);
  const pr = PRIPRAVY[String(t.id)];
  if(pr && pr.length){
    const odkaz = PRIPRAVY_ODKAZ
      ? `<a href="${PRIPRAVY_ODKAZ}" target="_blank" rel="noopener">Otevřít přípravy na Google Disku</a>`
      : `<span class="muted">Materiály jsou na Google Disku ve složce „Přípravy na projekty“.</span>`;
    h+=sec(`Přípravy z minulých let (${pr.length})`,
      `<div class="pripbox">${pr.map(p=>`<div class="p"><span class="pn">${p.n}</span>
         <span class="po">${p.s} souborů · ${p.o.slice(0,3).join(", ")}</span></div>`).join("")}
       <div style="margin-top:8px">${odkaz}</div></div>`);
  }
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
function esc(s){ return String(s).replace(/[&<>"']/g, c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
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
  document.getElementById("hlasZnami").innerHTML = znamiUcitele.map(u=>`<option value="${esc(u)}">`).join("");
}
function zkontrolujJmeno(){
  const el=document.getElementById("hlasName"), box=document.getElementById("hlasJmenoMsg");
  const jm=el.value.trim();
  box.innerHTML="";
  if(!jm) return;
  const p=podobneJmeno(jm);
  if(!p){
    if(!znamiUcitele.includes(jm)) box.innerHTML=`<span class="muted">Zapisuješ se poprvé jako <b>${esc(jm)}</b>.</span>`;
    return;
  }
  box.innerHTML = p.stejne
    ? `<span class="varovani">Už tu hlasuje <b>${esc(p.jmeno)}</b> — použij stejný zápis.
       <button onclick="pouzijJmeno('${esc(p.jmeno).replace(/'/g,"&#39;")}')">Použít ${esc(p.jmeno)}</button></span>`
    : `<span class="varovani">Nemyslíš <b>${esc(p.jmeno)}</b>?
       <button onclick="pouzijJmeno('${esc(p.jmeno).replace(/'/g,"&#39;")}')">Ano, jsem ${esc(p.jmeno)}</button>
       <span class="muted">Jinak pokračuj, zapíšu tě jako ${esc(jm)}.</span></span>`;
}
function pouzijJmeno(jm){
  const el=document.getElementById("hlasName");
  el.value=jm; localStorage.setItem("hlasName",jm);
  zkontrolujJmeno(); loadMyVotes(); renderRez();
}
/* Záloha hlasů. RLS dovoluje komukoli s odkazem hlasy smazat — než se to utáhne,
   ať je aspoň možné kdykoli stáhnout snapshot. */
function csvPole(v){
  const t = v===null || v===undefined ? "" : String(v);
  return /[",;\\n]/.test(t) ? '"'+t.replace(/"/g,'""')+'"' : t;
}
async function exportCsv(){
  const btn = document.getElementById("exportCsv");
  if(!sb){ btn.textContent = "Export není dostupný — hlasování se nenačetlo"; return; }
  const puvodni = btn.textContent;
  btn.textContent = "Stahuji…";
  const [{data:votes,error:e1},{data:rez,error:e2}] = await Promise.all([
    sb.from("votes").select("teacher,topic_id,rank").order("teacher").order("rank"),
    sb.from("assignments").select("teacher,topic_id")
  ]);
  if(e1||e2){ btn.textContent = "Stažení selhalo — zkus to znovu"; return; }
  const nazev = id => { const t = DATA.find(x=>x.id===id); return t ? t.nazev : ""; };
  const blok = id => { const t = DATA.find(x=>x.id===id); return t ? t.skupina : ""; };
  const vb = volbyVBloku(votes||[]);
  const radky = [["typ","ucitel","blok","id_tematu","nazev_tematu","poradi_celkem","volba_v_bloku"]];
  for(const v of (votes||[])) radky.push(["hlas", v.teacher, blok(v.topic_id), v.topic_id, nazev(v.topic_id), v.rank, vb[v.teacher+"|"+v.topic_id]||""]);
  for(const r of (rez||[]))   radky.push(["rezervace", r.teacher, blok(r.topic_id), r.topic_id, nazev(r.topic_id), "", ""]);
  const csv = "\\ufeff" + radky.map(r=>r.map(csvPole).join(";")).join("\\r\\n");
  const d = new Date(), p2 = x => String(x).padStart(2,"0");
  const jmeno = `hlasovani_${d.getFullYear()}-${p2(d.getMonth()+1)}-${p2(d.getDate())}_${p2(d.getHours())}${p2(d.getMinutes())}.csv`;
  const url = URL.createObjectURL(new Blob([csv], {type:"text/csv;charset=utf-8"}));
  const a = document.createElement("a");
  a.href = url; a.download = jmeno; document.body.appendChild(a); a.click();
  a.remove(); URL.revokeObjectURL(url);
  btn.textContent = `Staženo ✓ (${(votes||[]).length} hlasů, ${(rez||[]).length} rezervací)`;
  setTimeout(()=>{ btn.textContent = puvodni; }, 4000);
}
/* --- hlasování po blocích ---------------------------------------------------
   Pololetí má čtyři bloky (měsíce) a každý blok patří jednomu ScioCíli — celá
   škola dělá v jednom měsíci projekty k jednomu cíli. V každém bloku vzniká
   9 projektů, každý projekt má garanta a k němu tandem.
   Hlasuje se o všech čtyřech blocích najednou: v každém bloku si člověk vybere
   dvě témata (1. a 2. volbu). Do databáze jde pořadí 1–8 přes všechny bloky,
   pořadí uvnitř bloku se dopočítá — tabulka `votes` se tím nemusela měnit. */
const BLOKY = ["SC1","SC4","SC5","SC8"];
const POCET_V_BLOKU = 9;
const MAX_VOLEB = 2;
const nazevTematu = id => { const t=DATA.find(x=>x.id===id); return t ? t.nazev : String(id); };
const blokTematu  = id => { const t=DATA.find(x=>x.id===id); return t ? BLOKY.indexOf(t.skupina) : -1; };
function prazdnePicks(){ const o={}; for(const s of BLOKY) o[s]=[]; return o; }
function stejnePicks(a,b){ return BLOKY.every(s=>(a[s]||[]).join(",")===(b[s]||[]).join(",")); }

/* Hlasy se ukládají s průběžným pořadím 1..8 přes všechny bloky. Tohle z nich
   udělá zpátky pořadí uvnitř bloku (1. nebo 2. volba). */
function volbyVBloku(hlasy){
  const podle={};
  for(const h of hlasy){
    const t=DATA.find(x=>x.id===h.topic_id); if(!t) continue;
    const k=h.teacher+"|"+t.skupina;
    (podle[k]=podle[k]||[]).push(h);
  }
  const out={};
  for(const k in podle)
    podle[k].sort((a,b)=>a.rank-b.rank).forEach((h,i)=>{ out[h.teacher+"|"+h.topic_id]=i+1; });
  return out;
}

function initHlas(){
  myPicks = prazdnePicks();
  if(!sb) document.getElementById("hlasWarn").style.display="";
  const nameEl = document.getElementById("hlasName");
  nameEl.value = localStorage.getItem("hlasName") || "";
  nactiZname().then(zkontrolujJmeno);
  nameEl.addEventListener("change", e=>{
    const jm=e.target.value.trim(); e.target.value=jm;
    localStorage.setItem("hlasName", jm);
    zkontrolujJmeno(); loadMyVotes(); renderRez();
  });
  document.getElementById("exportCsv").addEventListener("click", exportCsv);
  document.getElementById("hlasSearch").addEventListener("input", renderBloky);
  document.getElementById("hlasSubmit").addEventListener("click", submitVotes);
  document.getElementById("toggleResults").addEventListener("click", toggleResults);
  document.getElementById("toggleNavrh").addEventListener("click", toggleNavrh);
  renderBloky();
  loadMyVotes();
  renderRez();
}
function renderBloky(){
  const nq = norm(document.getElementById("hlasSearch").value);
  document.getElementById("hlasBloky").innerHTML = BLOKY.map((sk,bi)=>{
    const vyb = myPicks[sk] || [];
    const items = DATA.filter(t=> t.skupina===sk && (!nq || hay(t).includes(nq)));
    const rows = items.map(t=>{
      const i = vyb.indexOf(t.id);
      return `<div class="hlasrow ${i>=0?"picked":""}" onclick="togglePick(${t.id})">
        <span>${t.id}. ${esc(t.nazev)}</span><span class="hlasnum">${i>=0?(i+1)+".":"+"}</span></div>`;
    }).join("") || `<p class="muted" style="padding:6px 10px">Hledání v tomhle bloku nic nenašlo.</p>`;
    const prohod = vyb.length===MAX_VOLEB
      ? ` <button class="prohod" onclick="prohodit('${sk}')">prohodit pořadí</button>` : "";
    const shrnuti = vyb.length
      ? vyb.map((id,i)=>`<b>${i+1}. volba:</b> ${esc(nazevTematu(id))}`).join(" &nbsp;·&nbsp; ") + prohod
      : '<span class="muted">zatím nevybráno</span>';
    return `<div class="blok">
      <h4><span>${bi+1}. blok — ${esc(SCN[sk])}</span>
        <span class="pocet ${vyb.length===MAX_VOLEB?"hotovo":""}">${vyb.length}/${MAX_VOLEB}</span></h4>
      <div class="blokvyber">${shrnuti}</div>
      <div class="hlaslist">${rows}</div>
    </div>`;
  }).join("");
}
function togglePick(id){
  const t = DATA.find(x=>x.id===id);
  if(!t || !myPicks[t.skupina]) return;
  const arr = myPicks[t.skupina], i = arr.indexOf(id);
  if(i>=0) arr.splice(i,1);
  else{
    if(arr.length>=MAX_VOLEB){ alert("V jednom bloku si vybíráš " + MAX_VOLEB + " témata — nejdřív jedno odeber."); return; }
    arr.push(id);
  }
  renderBloky();
}
function prohodit(sk){
  const arr = myPicks[sk];
  if(arr && arr.length===MAX_VOLEB){ arr.reverse(); renderBloky(); }
}
/* Překreslujeme jen tehdy, když se výběr opravdu změnil. Načtení hlasů běží
   na pozadí a doběhne často zrovna ve chvíli, kdy člověk klepe na první téma —
   kdybychom seznam přepsali pod rukou, kliknutí by se ztratilo (myš by stiskla
   jeden prvek a pustila už jiný). */
async function loadMyVotes(){
  if(!sb) return;
  const name = document.getElementById("hlasName").value.trim();
  if(!name){
    const prazdne = prazdnePicks();
    if(!stejnePicks(myPicks, prazdne)){ myPicks = prazdne; renderBloky(); }
    return;
  }
  const {data,error} = await sb.from("votes").select("topic_id,rank").eq("teacher",name).order("rank");
  /* Přepisujeme jen tehdy, když v databázi něco je. Kdo si nejdřív naklikal témata
     a teprve pak napsal jméno, o rozpracovaný výběr nepřijde. */
  if(!error && data && data.length){
    const nove = prazdnePicks();
    for(const r of data){
      const t = DATA.find(x=>x.id===r.topic_id);
      if(t && nove[t.skupina] && nove[t.skupina].length<MAX_VOLEB) nove[t.skupina].push(r.topic_id);
    }
    if(!stejnePicks(myPicks, nove)){ myPicks = nove; renderBloky(); }
  }
}
async function submitVotes(){
  const msg = document.getElementById("hlasMsg");
  if(!sb){ msg.textContent="Hlasování není momentálně dostupné."; return; }
  const name = document.getElementById("hlasName").value.trim();
  if(!name){ msg.textContent="Nejdřív napiš své příjmení."; return; }
  const poradi = [];
  for(const sk of BLOKY) for(const id of (myPicks[sk]||[])) poradi.push(id);
  if(!poradi.length){ msg.textContent="Vyber aspoň jedno téma."; return; }
  localStorage.setItem("hlasName", name);
  msg.textContent = "Ukládám…";
  /* Staré hlasy si nejdřív odložíme. Kdyby vkládání nových selhalo (výpadek sítě),
     vrátíme původní stav — jinak by učiteli zmizely i hlasy, které už měl uložené. */
  const {data:puvodni} = await sb.from("votes").select("topic_id,rank").eq("teacher",name);
  await sb.from("votes").delete().eq("teacher",name);
  const rows = poradi.map((id,i)=>({teacher:name, topic_id:id, rank:i+1}));
  const {error} = await sb.from("votes").insert(rows);
  if(error){
    if(puvodni && puvodni.length){
      await sb.from("votes").insert(puvodni.map(r=>({teacher:name, topic_id:r.topic_id, rank:r.rank})));
      msg.textContent = "Uložení selhalo ("+error.message+") — tvoje předchozí hlasy zůstaly beze změny. Zkus to prosím znovu.";
    } else {
      msg.textContent = "Uložení selhalo: "+error.message+" — zkus to prosím znovu.";
    }
    return;
  }
  const chybi = BLOKY.filter(sk=>(myPicks[sk]||[]).length<MAX_VOLEB);
  msg.textContent = "Uloženo ✓ ("+rows.length+" hlasů)"
    + (chybi.length ? " — ještě chybí výběr v blocích: " + chybi.map(s=>SCN[s]).join(", ") + "." : "");
  nactiZname();
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
    else action = `<span class="muted">obsazeno: ${esc(who)}</span>`;
    return `<div class="hlasrow"><span>${t.id}. ${esc(t.nazev)}</span>${action}</div>`;
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
  const {data} = await sb.from("votes").select("teacher,topic_id,rank");
  const hlasy = data || [];
  if(!hlasy.length){ box.innerHTML = `<p class="muted">Zatím žádné hlasy.</p>`; return; }
  const vb = volbyVBloku(hlasy);
  const agg = {};
  for(const h of hlasy){
    const r = vb[h.teacher+"|"+h.topic_id]; if(!r) continue;
    const a = agg[h.topic_id] = agg[h.topic_id] || {pocet:0, skore:0, prvni:0};
    a.pocet++; a.skore += (MAX_VOLEB+1-r); if(r===1) a.prvni++;
  }
  box.innerHTML = BLOKY.map((sk,bi)=>{
    const ids = DATA.filter(t=>t.skupina===sk && agg[t.id]).map(t=>t.id)
      .sort((a,b)=> agg[b].skore-agg[a].skore || agg[b].prvni-agg[a].prvni || a-b);
    const rows = ids.map(id=>`<div class="hlasrow" style="cursor:default"><span>${id}. ${esc(nazevTematu(id))}</span>
      <span>${agg[id].skore} b. · ${agg[id].prvni}× 1. volba · ${agg[id].pocet} hlasů</span></div>`).join("")
      || `<p class="muted">V tomhle bloku zatím nikdo nehlasoval.</p>`;
    return `<h4 class="navrhblok">${bi+1}. blok — ${esc(SCN[sk])} <span class="muted">(témat s hlasem: ${ids.length} z ${POCET_V_BLOKU} potřebných)</span></h4>${rows}`;
  }).join("");
}

/* --- návrh rozdělení: nejdřív garanti, pak tandemy --------------------------
   Dvě kola. V prvním dostane každý z 9 projektů v bloku garanta, a to jen
   z lidí, kteří pro to téma hlasovali — tím se zároveň vybere, kterých 9 témat
   z bloku se pojede. Ve druhém kole se k vybraným projektům doplní tandem:
   přednost mají ti, kdo pro téma hlasovali, a když preference dojdou, doplní
   se kdokoli další.
   Obojí počítá min-cost max-flow (postupné nejkratší cesty) — hledá nejlepší
   rozdělení jako celek, ne postupné „kdo dřív přijde“. Férovost je nastavená
   tak, aby vždycky přebila preference: nikdo nedostane druhou roli, dokud
   nemají první všichni ostatní. */
const FER = 1000;       // cena za každou další roli navíc — vždy přebije preference
const DVOJROLE = 300;   // penalta za garanta i tandem ve stejném bloku (jen když to jinak nejde)

function MCMF(n){
  return {
    n:n, to:[], cap:[], cost:[], head:Array.from({length:n},()=>[]),
    add(u,v,cap,cost){
      this.head[u].push(this.to.length); this.to.push(v); this.cap.push(cap); this.cost.push(cost);
      this.head[v].push(this.to.length); this.to.push(u); this.cap.push(0);   this.cost.push(-cost);
    },
    run(s,t){
      let flow=0;
      for(;;){
        const dist=new Array(this.n).fill(Infinity), inq=new Array(this.n).fill(false), pe=new Array(this.n).fill(-1);
        dist[s]=0; const q=[s]; inq[s]=true;
        while(q.length){
          const u=q.shift(); inq[u]=false;
          for(const e of this.head[u]){
            if(this.cap[e]<=0) continue;
            const v=this.to[e], nd=dist[u]+this.cost[e];
            if(nd<dist[v]){ dist[v]=nd; pe[v]=e; if(!inq[v]){ inq[v]=true; q.push(v); } }
          }
        }
        if(dist[t]===Infinity) break;
        let pridej=Infinity;
        for(let v=t; v!==s; ){ const e=pe[v]; pridej=Math.min(pridej,this.cap[e]); v=this.to[e^1]; }
        for(let v=t; v!==s; ){ const e=pe[v]; this.cap[e]-=pridej; this.cap[e^1]+=pridej; v=this.to[e^1]; }
        flow+=pridej;
      }
      return flow;
    }
  };
}

function navrhRozdeleni(ucitele, bod, rezervace){
  const T=ucitele.length, B=BLOKY.length;
  if(!T) return [];
  const vybrane=[];                       // {id, bi, garant, tandem, rezervace}
  const volno=BLOKY.map(()=>POCET_V_BLOKU);
  const roli={}; for(const u of ucitele) roli[u]=0;

  // rezervace bereme jako dané: rezervující je garantem toho tématu
  const rezervovano={};
  for(const r of rezervace){
    const bi=blokTematu(r.id);
    if(bi<0 || rezervovano[r.id] || volno[bi]<=0) continue;
    rezervovano[r.id]=true; volno[bi]--;
    if(roli[r.ucitel]!==undefined) roli[r.ucitel]++;
    vybrane.push({id:r.id, bi:bi, garant:r.ucitel, rezervace:true});
  }
  const jeVBloku=(u,b)=>vybrane.some(v=>v.bi===b && v.garant===u);

  // --- 1. kolo: garanti (jen z těch, kdo pro téma hlasovali)
  const kand=DATA.filter(t=>BLOKY.indexOf(t.skupina)>=0 && !rezervovano[t.id])
                 .map(t=>({id:t.id, bi:BLOKY.indexOf(t.skupina)}));
  const U=1, TB=U+T, TP=TB+T*B, BL=TP+kand.length, SINK=BL+B;
  const g=MCMF(SINK+1), hrany=[];
  for(let i=0;i<T;i++){
    const u=ucitele[i];
    for(let k=0;k<B;k++) g.add(0, U+i, 1, FER*(roli[u]+k));
    for(let b=0;b<B;b++) if(!jeVBloku(u,b)) g.add(U+i, TB+i*B+b, 1, 0);
  }
  kand.forEach((t,j)=>{
    g.add(TP+j, BL+t.bi, 1, 0);
    for(let i=0;i<T;i++){
      const b=bod[ucitele[i]+"|"+t.id];
      if(b){ hrany.push({i:i, j:j, e:g.to.length}); g.add(TB+i*B+t.bi, TP+j, 1, -b); }
    }
  });
  for(let b=0;b<B;b++) g.add(BL+b, SINK, Math.max(0,volno[b]), 0);
  g.run(0,SINK);
  for(const h of hrany) if(g.cap[h.e]===0){
    const u=ucitele[h.i];
    vybrane.push({id:kand[h.j].id, bi:kand[h.j].bi, garant:u});
    roli[u]++;
  }
  vybrane.sort((a,b)=> a.bi-b.bi || a.id-b.id);

  // --- 2. kolo: tandemy (nejdřív podle hlasů, pak kdokoli další)
  const U2=1, TB2=U2+T, TP2=TB2+T*B, SINK2=TP2+vybrane.length;
  const g2=MCMF(SINK2+1), hrany2=[];
  for(let i=0;i<T;i++){
    const u=ucitele[i];
    for(let k=0;k<B;k++) g2.add(0, U2+i, 1, FER*(roli[u]+k));
    for(let b=0;b<B;b++) g2.add(U2+i, TB2+i*B+b, 1, jeVBloku(u,b) ? DVOJROLE : 0);
  }
  vybrane.forEach((v,j)=>{
    g2.add(TP2+j, SINK2, 1, 0);
    for(let i=0;i<T;i++){
      if(ucitele[i]===v.garant) continue;
      hrany2.push({i:i, j:j, e:g2.to.length});
      g2.add(TB2+i*B+v.bi, TP2+j, 1, -(bod[ucitele[i]+"|"+v.id]||0));
    }
  });
  g2.run(0,SINK2);
  for(const h of hrany2) if(g2.cap[h.e]===0) vybrane[h.j].tandem = ucitele[h.i];
  return vybrane;
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
  const hlasy=votes||[], rezervace=(rez||[]).map(r=>({ucitel:r.teacher, id:r.topic_id}));
  if(!hlasy.length && !rezervace.length){ box.innerHTML=`<p class="muted">Zatím nikdo nehlasoval.</p>`; return; }

  const vb = volbyVBloku(hlasy);
  const bod = {};
  for(const h of hlasy){
    const r = vb[h.teacher+"|"+h.topic_id];
    if(r) bod[h.teacher+"|"+h.topic_id] = MAX_VOLEB+1-r;   // 1. volba 2 body, 2. volba 1 bod
  }
  const ucitele=[...new Set([...hlasy.map(h=>h.teacher), ...rezervace.map(r=>r.ucitel)])]
                  .sort((a,b)=>a.localeCompare(b,"cs"));
  const vybrane = navrhRozdeleni(ucitele, bod, rezervace);
  const volba = (u,id)=>{ const r=vb[u+"|"+id]; return r ? r+". volba" : "nehlasoval"; };

  let html="";
  BLOKY.forEach((sk,bi)=>{
    const proj = vybrane.filter(v=>v.bi===bi);
    html += `<h4 class="navrhblok">${bi+1}. blok — ${esc(SCN[sk])}</h4>`;
    html += `<table><tr><th>Téma</th><th>Garant</th><th>Tandem</th></tr>`;
    for(const v of proj){
      const g = `${esc(v.garant)} <span class="volba">(${v.rezervace ? "rezervace" : volba(v.garant,v.id)})</span>`;
      const t = v.tandem ? `${esc(v.tandem)} <span class="volba">(${volba(v.tandem,v.id)})</span>`
                         : `<span class="muted">— nikdo nezbyl —</span>`;
      html += `<tr class="${v.rezervace?"fix":""}"><td>${v.id}. ${esc(nazevTematu(v.id))}</td><td>${g}</td><td>${t}</td></tr>`;
    }
    if(!proj.length) html += `<tr class="nic"><td colspan="3">V tomhle bloku nikdo nehlasoval.</td></tr>`;
    html += `</table>`;
    if(proj.length<POCET_V_BLOKU)
      html += `<p class="chybi">Vyšlo jen ${proj.length} projektů z ${POCET_V_BLOKU} — na zbylá témata v tomhle bloku nikdo nehlasoval. Doplň je ručně.</p>`;
  });

  const pocty={}; for(const u of ucitele) pocty[u]={g:0, t:0};
  for(const v of vybrane){
    if(pocty[v.garant]) pocty[v.garant].g++;
    if(v.tandem && pocty[v.tandem]) pocty[v.tandem].t++;
  }
  html += `<h4 class="navrhblok">Kdo co vede</h4><table><tr><th>Učitel</th><th>Garant</th><th>Tandem</th></tr>`;
  for(const u of ucitele)
    html += `<tr class="${pocty[u].g+pocty[u].t ? "" : "nic"}"><td>${esc(u)}</td><td>${pocty[u].g}×</td><td>${pocty[u].t}×</td></tr>`;
  html += `</table>`;

  const sGarant = vybrane.length;
  const sTandem = vybrane.filter(v=>v.tandem).length;
  const prvniG = vybrane.filter(v=>!v.rezervace && vb[v.garant+"|"+v.id]===1).length;
  const gPocty = ucitele.map(u=>pocty[u].g);
  const bezRole = ucitele.filter(u=>!pocty[u].g && !pocty[u].t);
  const dvojrole = vybrane.filter(v=>v.tandem && vybrane.some(w=>w.bi===v.bi && w.garant===v.tandem)).length;
  html += `<div class="navrhSouhrn">Hlasovalo <b>${ucitele.length}</b> lidí ·
    obsazeno <b>${sGarant}</b> z ${POCET_V_BLOKU*BLOKY.length} projektů ·
    tandem má <b>${sTandem}</b> z nich ·
    garant dostal svou 1. volbu <b>${prvniG}</b>× ·
    garantství na osobu: <b>${Math.min(...gPocty)}–${Math.max(...gPocty)}</b>.`;
  if(bezRole.length) html += `<br>Bez role zůstali: ${esc(bezRole.join(", "))}.`;
  if(dvojrole) html += `<br>V ${dvojrole} případech je tandem zároveň garantem jiného projektu ve stejném bloku — na tolik projektů nás v bloku není dost.`;
  if(sGarant < POCET_V_BLOKU*BLOKY.length) html += `<br>Neobsazené projekty vznikají tam, kde na téma nikdo nehlasoval. Buď je doplň ručně, nebo nech dohlasovat třetí volbu.`;
  html += `<br><span class="muted">Nic se nikam nezapisuje — je to jen podklad k rozhodnutí u stolu.</span></div>`;
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
/* Kdo přijde poprvé, uvidí návod; při dalších návštěvách rovnou katalog.
   Odkaz přímo na téma (…/#14) má přednost — ten návod nikdy nepřebije. */
(function uvitani(){
  let poprve = false;
  try { poprve = !localStorage.getItem("videlNavod"); localStorage.setItem("videlNavod","1"); }
  catch(e) { poprve = false; }          // privátní režim: prostě ukážeme katalog
  if(!poprve || location.hash) return;
  view = "navod";
  [...document.getElementById("viewChips").children].forEach(ch=>
    ch.classList.toggle("active", ch.dataset.view === "navod"));
})();

render();
openFromHash();
</script>
</body>
</html>
"""

html = (HTML.replace("__DATA__", DATA).replace("__KAM__", KAM)
            .replace("__KLICE__", KLICE)
            .replace("__PRIPRAVY__", PRIPRAVY).replace("__PRIPRAVY_ODKAZ__", PRIPRAVY_ODKAZ)
            .replace("__VERSION__", VERSION))
open("index.html", "w", encoding="utf-8", newline="\n").write(html)
print(f"OK index.html ({len(html)//1024} kB, {len(topics)} témat, verze {VERSION})")
