# last30inderes

Selvitä mitä suomalainen sijoittajayhteisö keskustelee [Inderes-foorumilla](https://forum.inderes.com) mistä tahansa aiheesta — yhtiöistä, trendeistä tai markkinailmiöistä.

Toimii sekä Claude Code -skillinä että itsenäisenä CLI-työkaluna.

## Käyttöesimerkkejä

```bash
# Mitä foorumilla puhutaan tekoälystä viimeisen kuukauden ajalta?
python3 scripts/inderes_fetch.py "tekoäly" --days 30

# Millä tunnelmilla Fortumia kommentoidaan tällä viikolla?
python3 scripts/inderes_fetch.py "Fortum" --days 7

# Syvähaku korkosijoituksista — hakee viestien koko sisällön
python3 scripts/inderes_fetch.py "korkosijoitukset" --days 14 --deep

# Rajaa osakekategoriaan
python3 scripts/inderes_fetch.py "Neste" --category osakkeet
```

Claude Code -skillinä:
```
/last30inderes tekoäly
/last30inderes Fortum --days 7
/last30inderes "asuntomarkkina 2026" --deep
```

## Mitä se tekee?

1. **Hakee** Inderes-foorumin keskusteluja Discourse-rajapinnasta (haku + tagi-täydennys)
2. **Pisteyttää** viestit kolmella signaalilla: relevanssi (45%), sitoutuminen (30%), tuoreus (25%)
3. **Tiivistää** tulokset markdown-muotoon, ryhmiteltynä keskusteluittain
4. **Claude syntetisoi** (skill-moodissa) katsauksen: keskeiset teemat, merkittävät näkemykset ja yhteisön sentimentti

## Esimerkkituloste

Katso [examples/tekoaly_30d.md](examples/tekoaly_30d.md) — haku "tekoäly" 30 päivän ajalta. Löysi 121 viestiä 30 keskustelusta.

## Asennus

Ei ulkoisia riippuvuuksia — pelkkä Python 3.10+ stdlib.

Claude Code -skilliksi: kopioi tai linkitä tämä hakemisto `~/.claude/skills/last30inderes/` -polkuun.

## Laajennettavuus

`DiscourseClient` on geneerinen — toimii minkä tahansa Discourse-foorumin kanssa. Uuden foorumin lisääminen:

```python
from lib.discourse import DiscourseClient
client = DiscourseClient("https://toinen-foorumi.com", forum_name="muu")
```

Ei-Discourse-lähteitä varten: luo uusi client-moduuli joka tuottaa `ForumPost`-objekteja.
