# last30inderes

Selvitä mitä suomalainen sijoittajayhteisö keskustelee [Inderes-foorumilla](https://forum.inderes.com) mistä tahansa aiheesta — yhtiöistä, trendeistä tai markkinailmiöistä.

Claude Code -skill joka hakee keskusteluja suoraan Discourse JSON API:sta ja syntetisoi katsauksen.

## Miksi?

Inderes-foorumilla on yli 70 000 suomalaista sijoittajaa jotka keskustelevat aktiivisesti yhtiöistä, markkinoista ja sijoitusstrategioista. Foorumi on arvokas pulssimittari sille mitä yksityissijoittajat oikeasti ajattelevat — mutta satojen viestien läpikäynti käsin on hidasta.

Tällä skillillä voit esimerkiksi:

- **Ennen ostopäätöstä**: "Mitä muut sijoittajat ajattelevat Fortumista juuri nyt? Onko jotain mitä en ole huomannut?"
- **Tuloskauden aikana**: "Miten yhteisö reagoi Nesteen Q4-tulokseen? Mikä yllätti?"
- **Trendien seuranta**: "Puhutaanko tekoälystä vielä vai onko hype laantunut?"
- **Uuden aiheen tutkiminen**: "En tiedä korkosijoittamisesta mitään — mistä foorumilla keskustellaan?"

Skill tiivistää kymmeniä tai satoja viestejä muutaman kappaleen katsaukseksi suorine lainauksineen ja linkkeineen, jotta voit nopeasti hahmottaa yhteisön tunnelman ja porautua kiinnostaviin keskusteluihin.

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

### Vaatimukset

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (CLI, desktop tai IDE-laajennus)
- Ei muita riippuvuuksia — skill käyttää Claude Coden sisäänrakennettua WebFetch-työkalua

### Asennus GitHubista

```bash
# Kloonaa repo skills-hakemistoon
git clone https://github.com/vhalme/last30inderes.git ~/.claude/skills/last30inderes
```

### Manuaalinen asennus

```bash
# Luo skills-hakemisto jos ei vielä ole
mkdir -p ~/.claude/skills

# Kopioi tai symlinkitä tämä hakemisto
cp -r /polku/last30inderes ~/.claude/skills/last30inderes
# tai
ln -s /polku/last30inderes ~/.claude/skills/last30inderes
```

### Varmista asennus

Käynnistä Claude Code ja kirjoita:

```
/last30inderes Nokia
```

Jos skill latautuu ja alkaa hakea foorumidataa, asennus onnistui.

## Esimerkkitulosteita

- [examples/nokia_30d.md](examples/nokia_30d.md) — `/last30inderes Nokia` — yhtiökohtainen katsaus teemoineen, lainauksineen ja sentimenttianalyyseineen
- [examples/tekoaly_30d.md](examples/tekoaly_30d.md) — `/last30inderes tekoäly` — teemakohtainen haku joka löytää keskusteluja kymmenistä eri ketjuista

## Laajennettavuus

Discourse API on geneerinen — sama logiikka toimii mille tahansa Discourse-foorumille vaihtamalla base URL SKILL.md:ssä.
