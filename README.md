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
| `data/ucitele.json` | nastavení hlasování (kdo vede víc témat) | zřídka — jména se nezadávají |
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

**Jména se nezadávají dopředu.** Kdo přijde hlasovat, napíše si příjmení sám;
každý další už dostane našeptávání z těch, kdo se zapsali dřív.

Aby z překlepů nevznikali „noví“ lidé (`Novák` / `novák` / `Nováková` jako tři
učitelé), appka jméno porovná s už zapsanými:

- **liší se jen diakritikou nebo velikostí písmen** → trvá na jednotném zápisu,
- **je o písmeno či dvě vedle** → zeptá se „Nemyslíš …?“, ale nechá pokračovat,
- **je to skutečně jiné příjmení** → tiše zapíše jako nového.

Nikoho to nezablokuje — jen se ptá. Zároveň to není bezpečnostní opatření:
kdokoli se může zapsat pod cizím příjmením. Řeší to čistotu dat, ne zlou vůli.

V `data/ucitele.json` se nastavuje jen kapacita — kolik témat kdo může vést:

```json
{ "vychozi_pocet": 1, "kapacity": { "Nováková": 2 } }
```

Jméno v `kapacity` musí sedět přesně na to, jak je zapsané v hlasování.

### Rozdělení témat

Tlačítko „Spočítat návrh" rozdělí témata tak, aby byl součet preferencí
co největší (maďarský algoritmus, ne jen hrubý odhad). Pravidla:

- už zarezervovaná témata bere jako daná a učiteli ubírají kapacitu,
- kdo nehlasoval, nedostane náhodné téma,
- **nic nikam nezapisuje** — je to podklad k rozhodnutí, ne rozhodnutí.

Chceš-li návrh zafixovat, udělej z něj rezervace ručně.
