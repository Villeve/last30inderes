# last30inderes

Selvitä mitä suomalainen sijoittajayhteisö keskustelee [Inderes-foorumilla](https://forum.inderes.com) mistä tahansa aiheesta — yhtiöistä, trendeistä tai markkinailmiöistä.

Claude Code -skill joka hakee keskusteluja suoraan Discourse JSON API:sta ja syntetisoi katsauksen.

## Käyttö

```
/last30inderes tekoäly
/last30inderes Fortum --days 7
/last30inderes "asuntomarkkina 2026" --deep
/last30inderes "korkosijoitukset" --days 14 --category sijoittaminen
```

## Mitä se tekee?

1. **Hakee** Inderes-foorumin keskusteluja Discourse JSON -rajapinnasta (haku + tagi-täydennys)
2. **Analysoi** viestien tykkäykset, vastaukset, katselut ja luottamustasot
3. **Syntetisoi** katsauksen suomeksi: keskeiset teemat, merkittävät näkemykset, yhteisön sentimentti ja linkit alkuperäisiin viesteihin

## Asennus

Kopioi tai linkitä tämä hakemisto `~/.claude/skills/last30inderes/` -polkuun.

Ei riippuvuuksia — skill käyttää Claude Coden WebFetch-työkalua suoraan.

## Esimerkkituloste

Katso [examples/tekoaly_30d.md](examples/tekoaly_30d.md) — haku "tekoäly" 30 päivän ajalta.

## Laajennettavuus

Discourse API on geneerinen — sama logiikka toimii mille tahansa Discourse-foorumille vaihtamalla base URL SKILL.md:ssä.
