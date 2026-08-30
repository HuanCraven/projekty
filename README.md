# Projekty 2026/27 — katalog témat podle ScioCílů

Katalog 55 projektových témat pro předmět Projekty (ScioŠkola Dejvice),
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
| `podklady/` | osnovy kamenů SC1/4/5/8, digest revidovaného RVP, digest učiva ŠVP, `poznamky.md` (rozhodnutí a odložené nápady) | referenční |

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
- Většina témat je použitelná ve všech trojročích. Výjimky: jen pro 3. trojročí
  jsou č. 40 (Právo pro život) a č. 51 (Čtení tě mění — 1. a 2. trojročí mají
  čtenářskou dílnu), jen pro 1. trojročí jsou č. 54 (Zvládnu to sám!) a č. 55
  (Naše třída) — starším slouží č. 7, 35, 22 a 23.
  U témat omezených na jedno trojročí nese obsah příslušná `difN` a ostatní
  dvě jsou `—`; do jedné z nich patří krátké vysvětlení, proč téma pro dané
  trojročí není. Č. 26 (Láska, vztahy a hranice) bylo v srpnu 2026 otevřeno
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

Třetí záložka webu — učitelé si vyberou témata, která chtějí vést, a případně
si téma rezervují. Data jdou do Supabase projektu `projekty-hlasovani`,
tabulky `votes` a `assignments`. V HTML je jen *publishable* klíč, nic tajného.

### Hlasuje se po blocích

Pololetí má **čtyři bloky** (měsíce) a každý blok patří jednomu ScioCíli —
celá škola dělá v jednom měsíci projekty k jednomu cíli. V každém bloku vzniká
**9 projektů**, každý s **garantem** a **tandemem**; za pololetí je to 36 projektů.

Hlasuje se o všech čtyřech blocích najednou: **v každém bloku dvě témata**
(1. a 2. volba), celkem tedy osm. Pořadí bloků drží `BLOKY` v generátoru,
teď `SC1, SC4, SC5, SC8` — první blok je „Umím se učit".

Do tabulky `votes` jde **průběžné pořadí 1–8** přes všechny bloky (blok po bloku,
uvnitř bloku 1. a 2. volba). Volbu uvnitř bloku dopočítá `volbyVBloku()` ze
`skupina` tématu. Díky tomu se **schéma tabulky nemuselo měnit** a stará data
zůstala čitelná. Kdyby se počet voleb na blok měnil, hlídej, ať `rank` zůstane
souvislá řada od 1 — na tom stojí i pohled `vote_results`, který appka sama
už nepoužívá (výsledky si počítá z `votes` a ukazuje je po blocích).

Modul je **součástí generátoru** (`build_web.py`) — CSS, sekce `#hlas`,
načtení Supabase SDK z CDN i funkce `initHlas()` a spol. Přegenerování
`index.html` ho tedy zachová. Po každém buildu se vyplatí ověřit:

```bash
grep -c Hlasování index.html    # očekávej 6 (0 = modul z generátoru vypadl)
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

`data/ucitele.json` se **už nepoužívá** — kapacitu určuje struktura pololetí
(4 bloky × 9 projektů) a role rozděluje návrh sám. Soubor zůstal v repozitáři
pro případ, že by se ruční kapacity vrátily; generátor ho nečte.

### Rozdělení témat

Tlačítko „Spočítat návrh" počítá **ve dvou kolech**:

1. **Garanti.** Každý z 9 projektů v bloku dostane garanta, a to **jen z lidí,
   kteří pro to téma hlasovali**. Tím se zároveň vybere, kterých 9 témat
   z bloku se pojede.
2. **Tandemy.** K vybraným projektům se doplní druhý člověk — přednost mají
   ti, kdo pro téma hlasovali, a když preference dojdou, doplní se kdokoli další.

Obojí řeší **min-cost max-flow** (postupné nejkratší cesty) nad celým pololetím
najednou, ne blok po bloku — jinak by první blok „vyžral" ty nejžádanější lidi.
Férovost je nastavená tak, aby **vždycky přebila preference**: cena každé další
role je `FER = 1000`, zatímco nejlepší preference má hodnotu 2. Nikdo tedy
nedostane druhé garantství, dokud nemají první všichni ostatní.

Další pravidla:

- rezervované téma je dané — rezervující je jeho garantem,
- jeden člověk je v bloku nejvýš jednou garantem a nejvýš jednou tandemem;
  obojí naráz v jednom bloku stojí `DVOJROLE = 300`, takže k tomu dojde jen
  tam, kde by projekty jinak zůstaly prázdné (a souhrn to hlásí),
- blok, kde má hlasy míň než 9 témat, vyjde neúplný — appka to napíše
  a je potřeba ho doplnit ručně nebo nechat dohlasovat,
- **nic nikam nezapisuje** — je to podklad k rozhodnutí, ne rozhodnutí.

Chceš-li návrh zafixovat, udělej z něj rezervace ručně.

Algoritmus se dá testovat mimo prohlížeč: funkce `navrhRozdeleni()` je
soběstačná (potřebuje jen `DATA`), takže se dá vytáhnout z `index.html`
a pustit v Node nad vygenerovanými hlasy.
