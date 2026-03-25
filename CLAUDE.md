# last30inderes

Inderes-foorumin keskustelujen tutkimustyökalu ja Claude Code -skill.

## Rakenne
- `scripts/inderes_fetch.py` — CLI-pääohjelma
- `scripts/lib/` — Moduulit: discourse (API), schema, normalize, score, render
- `SKILL.md` — Claude Code -skillin määritys
- `tests/` — Testit pytest:llä

## Kehitys
- Python 3.10+, ei ulkoisia riippuvuuksia (vain stdlib)
- Testit: `python3 -m pytest tests/ -v`
- Foorumi: forum.inderes.com (Discourse JSON API, julkinen)

## Konventiot
- Koodikommentit ja muuttujat englanniksi
- Käyttöliittymätekstit ja tuloste suomeksi
- Uudet foorumit: lisää uusi client-luokka lib/-hakemistoon, tuota ForumPost-objekteja
