# Projekty 2026/27 — katalog témat podle ScioCílů

Katalog 50 projektových témat pro předmět Projekty (ScioŠkola Dejvice),
1. pololetí 2026/27, ScioCíle 4, 1, 5 a 8, úrovně 2 a 3 (2. a 3. trojročí).

Web běží na GitHub Pages: `https://huancraven.github.io/projekty/`

## Struktura

| cesta | co je | edituje se ručně? |
|---|---|---|
| `index.html` | webový katalog (vše v jednom souboru) | **NE — generuje se** |
| `data/temata_sc{4,1,5,8}.json` | témata: název, kameny, anotace, aktivity, diferenciace | ano — zdroj pravdy |
| `data/znalosti_v3.json` | tvrdé znalosti + didaktické tipy k tématům (klíč = id tématu) | ano — zdroj pravdy |
| `data/kameny.json` | rejstřík stavebních kamenů ScioCílů (zdroj pro záložku Rejstřík) | zřídka — referenční |
| `data/ucitele.json` | seznam sboru pro přihlášení do hlasování | ano — před každým hlasováním |
| `tools/build_web.py` | generátor `index.html` | zřídka |
| `tools/build_docx.js` | generátor Word katalogu (`vystupy/`) — vyžaduje npm balíček `docx` | zřídka |
| `tools/build_xlsx.py` | generátor Excel tabulky (`vystupy/`) — vyžaduje `openpyxl` | zřídka |
| `vystupy/` | vygenerovaný Word + Excel | NE — generuje se |
| `podklady/` | osnovy kamenů SC1/4/5/8, digest revidovaného RVP, digest učiva ŠVP | referenční |

## Jak upravit nebo přidat téma

1. Uprav příslušný `data/temata_scN.json` (nové téma = nové nejvyšší `id`)
   a případně `data/znalosti_v3.json` (klíč = id tématu).
   Pozor na uvozovky v JSON: uvnitř textů používej české `„…“`, nikdy rovné `"`.
2. Přegeneruj výstupy z kořene repozitáře:

```bash
python3 tools/build_web.py     # -> index.html
python3 tools/build_xlsx.py    # -> vystupy/Projektova_temata.xlsx
node tools/build_docx.js       # -> vystupy/Katalog_projektovych_temat.docx
```

Poprvé je potřeba doinstalovat závislosti (`build_web.py` žádné nemá):

```bash
pip install openpyxl && npm install
```

`build_xlsx.py` při běhu vypíše kontrolu pokrytí kamenů — očekávaný stav je
„Nepokryté kameny (1): 5.2.3.3".

3. Commitni a pushni — GitHub Pages web obnoví do minuty.

`index.html` nikdy needituj ručně — příští generace by změny přepsala.

## Pravidla obsahu

- Označení zdrojů („ŠVP (Ú2):", „RVP – ") zůstává v datech, ale generátory ho
  z výstupů odstraňují — ve webu, Wordu i Excelu se nezobrazuje.
- Úroveň 2 ≈ 6. ročník, úroveň 3 ≈ 9. ročník (dle ŠVP).
- Většina témat je společná pro obě trojročí; jen pro 3. trojročí: č. 26 (Láska,
  vztahy a hranice) a č. 40 (Právo pro život).
- Kontrolu pokrytí kamenů hlásí `build_xlsx.py` (záměrně nepokrytý jen 5.2.3.3).

## Záložka Hlasování

Třetí záložka webu — učitelé seřadí až 8 témat (první volba má nejvyšší váhu)
a rezervují si téma (jedno téma = jeden učitel). Data jdou do Supabase projektu
`projekty-hlasovani`, tabulky `votes`, `vote_results`, `assignments`.
V HTML je jen *publishable* klíč, nic tajného.

Modul je **součástí generátoru** (`build_web.py`) — CSS, sekce `#hlas`,
načtení Supabase SDK z CDN i funkce `initHlas()` a spol. Přegenerování
`index.html` ho tedy zachová. Po každém buildu se vyplatí ověřit:

```bash
grep -c Hlasování index.html    # očekávej 2
```

Jméno hlasujícího si drží prohlížeč v `localStorage` (klíč `hlasName`).
Když se SDK nenačte (offline), záložka zobrazí varovný řádek místo pádu.

### Přihlášení

Hlasuje se pod příjmením vybraným ze seznamu v `data/ucitele.json`:

```json
{ "ucitele": [
  { "prijmeni": "Nováková", "pocet": 2 },
  { "prijmeni": "Svoboda" }
] }
```

`pocet` = kolik témat může učitel vést (nepovinné, výchozí 1). Seznam se
řadí abecedně sám. **Dokud je prázdný, hlasování je zavřené** — je to
pojistka, aby nevznikaly hlasy na překlepy ve jménech.

Není to bezpečnostní opatření: kdokoli si může vybrat cizí příjmení.
Řeší to identitu a čistotu dat, ne ochranu před zlou vůlí.

### Rozdělení témat

Tlačítko „Spočítat návrh" rozdělí témata tak, aby byl součet preferencí
co největší (maďarský algoritmus, ne jen hrubý odhad). Pravidla:

- už zarezervovaná témata bere jako daná a učiteli ubírají kapacitu,
- kdo nehlasoval, nedostane náhodné téma,
- **nic nikam nezapisuje** — je to podklad k rozhodnutí, ne rozhodnutí.

Chceš-li návrh zafixovat, udělej z něj rezervace ručně.
