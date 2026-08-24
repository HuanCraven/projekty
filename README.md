# Projekty 2026/27 — katalog témat podle ScioCílů

Katalog 53 projektových témat pro předmět Projekty (ScioŠkola Dejvice),
1. pololetí 2026/27, ScioCíle 4, 1, 5 a 8, úrovně 1–3 (1.–3. trojročí).

Web běží na GitHub Pages: `https://huancraven.github.io/projekty/`

## Struktura

| cesta | co je | edituje se ručně? |
|---|---|---|
| `index.html` | webový katalog (vše v jednom souboru) | **NE — generuje se** |
| `data/temata_sc{4,1,5,8}.json` | témata: název, kameny, anotace, aktivity, diferenciace | ano — zdroj pravdy |
| `data/znalosti_v3.json` | tvrdé znalosti + didaktické tipy k tématům (klíč = id tématu) | ano — zdroj pravdy |
| `data/kameny.json` | rejstřík stavebních kamenů ScioCílů (zdroj pro záložku Rejstřík) | zřídka — referenční |
| `data/ucitele.json` | nastavení hlasování (kdo vede víc témat) | zřídka — jména se nezadávají |
| `data/klice.json` | klíče ke ScioCílům — otázka, pojmy a krátká odpověď u kamene | generováno ze Zdrojů |
| `data/pripravy.json` | odkazy na přípravy z minulých let (materiály zůstávají na Disku) | ručně |
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

> **Přegeneruj vždy všechny tři výstupy, ne jen web.** Web se dělá často,
> Word a Excel se snadno zapomenou. V srpnu 2026 byly `vystupy/` půl měsíce
> pozadu (obsahovaly stav před otevřením tématu 26 druhému trojročí) a
> nikdo si toho nevšiml, protože web byl v pořádku.
>
> Nová pole je navíc potřeba doplnit do generátorů zvlášť — `dif1` se
> původně přidalo jen do webu a ve Wordu chybělo. Po buildu se vyplatí
> zkontrolovat v Excelu sloupec „Trojročí" a ve Wordu sekci „Diferenciace".

## Pravidla obsahu

- Označení zdrojů („ŠVP (Ú2):", „RVP – ") zůstává v datech, ale generátory ho
  z výstupů odstraňují — ve webu, Wordu i Excelu se nezobrazuje.
- Úroveň 1 ≈ 3. ročník, úroveň 2 ≈ 6. ročník, úroveň 3 ≈ 9. ročník (dle ŠVP).
- **Pole `urovne` je seznam trojročí, ve kterých je téma použitelné** — čísla
  oddělená čárkou, např. `"1,2,3"` (výchozí u nových témat), `"3"` (jen třetí),
  `"2,3"`. Popisek na kartě i filtry se z něj skládají samy, takže stačí zapsat
  správný seznam. Hodnota `"obě"` ze starého modelu už neplatí.
- **U nového tématu vyplň všechny tři diferenciace** (`dif1`, `dif2`, `dif3`) —
  katalog je od srpna 2026 určený pro 1.–3. trojročí, ne jen pro 2. a 3.
- Většina témat je použitelná ve všech trojročích; jen pro 3. trojročí je č. 40
  (Právo pro život). Č. 26 (Láska, vztahy a hranice) bylo v srpnu 2026 otevřeno
  i 2. trojročí — Úroveň 2 u jeho kamenů (5.2.4.1–3, 5.2.1.2, 5.1.1.6) tento
  obsah pro 2. trojročí přímo popisuje, takže dřívější omezení bylo v rozporu
  se zdrojem. Rozdíl mezi trojročími nese `dif2`/`dif3`, ne dostupnost tématu.
- Kontrolu pokrytí kamenů hlásí `build_xlsx.py` (záměrně nepokrytý jen 5.2.3.3).

## Klíče ke ScioCílům

U stavebních kamenů se v detailu tématu i v rejstříku rozbaluje **klíč** —
metodika Scia: otázka, klíčové pojmy a krátká odpověď. Pokrytí je částečné
(105 klíčů k 76 ze 120 kamenů), takže u řady kamenů žádný klíč není a web
s tím počítá.

**Texty klíčů generovala AI a nejsou kontrolované člověkem** — píše to sám
zdroj, proto to web u každého klíče uvádí. Klíče označené ve zdroji 🪢🪢
mají na webu štítek „vybraný".

Data vznikla extrakcí z `Zdroje/Klíče*` (.docx) — vytahuje se jen sekce
„Krátká odpověď"; plné klíče (~27 tis. znaků každý) zůstávají na Disku.
Pět klíčů odkazovalo na kódy ze staršího číslování (1.2.3.5, 5.2.3.5,
8.2.2.3, 8.2.3.5, 8.3.4.2), které v katalogu nejsou — ty se vynechávají.

## Přípravy z minulých let

`data/pripravy.json` mapuje 29 složek starých příprav (2024–2026) na 19 témat.
Materiály samotné (779 MB, převážně obrázky) **do repozitáře nepatří** a
zůstávají na Google Disku; web na ně jen odkazuje. URL rodičovské složky se
vyplňuje do klíče `_odkaz` — dokud je prázdný, web místo odkazu zobrazí jen
název složky, kterou má průvodce na Disku hledat.

Pozor: přípravy používají **staré číslování ScioCílů** („ScK 2", „4.5.1"),
které na aktuální kameny nelze automaticky převést.

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
