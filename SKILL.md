# last30inderes

Tutki mitä suomalainen sijoittajayhteisö keskustelee Inderes-foorumilla tietystä aiheesta.

## Käyttö
/last30inderes <aihe> [--days N] [--deep] [--category SLUG]

## Argumentit
- aihe: Tutkittava aihe (yrityksen nimi, markkinakonsepti, sektori jne.)
- --days N: Aikaväli päivissä (oletus: 30, max: 90)
- --deep: Hae useampia sivuja ja viestien koko sisältö
- --category SLUG: Rajaa kategoriaan (esim. osakkeet, sijoittaminen, talous-ja-markkinat)

## Discourse JSON API

Inderes-foorumi (forum.inderes.com) on Discourse-pohjainen. Kaikki data haetaan WebFetch-työkalulla JSON-rajapinnasta.

### Haku

```
https://forum.inderes.com/search.json?q={aihe}+after:{YYYY-MM-DD}&page={1,2,3}
```

- Laske `after`-päivämäärä: tämä päivä miinus --days (oletus 30)
- Hae sivu 1. Jos vastauksen `grouped_search_result.more_full_page_results` on true, hae sivu 2 (ja 3 --deep-tilassa)
- Vastaus sisältää `posts`-listan (id, username, blurb, like_count, created_at, topic_id) ja `topics`-listan (id, title, slug, views, reply_count, like_count, tags)
- Jos --category annettu, lisää hakuun `##{category}`

### Tagi-täydennys

Jos aihe vaikuttaa yksittäiseltä yhtiöltä tai tunnetulta tagiltä, hae myös:
```
https://forum.inderes.com/tag/{aihe-lowercase}.json
```
Tämä löytää keskusteluja jotka eivät välttämättä näy tekstihaussa.

### Viestin koko sisältö (--deep tai kiinnostava viesti)

```
https://forum.inderes.com/t/{topic_id}/posts.json?post_ids[]={id1}&post_ids[]={id2}
```
Palauttaa `post_stream.posts`-listan jossa `cooked` (HTML), `reads`, `reply_count`, `score`.

### Linkkien muodostaminen

- Keskustelu: `https://forum.inderes.com/t/{slug}/{topic_id}`
- Yksittäinen viesti: `https://forum.inderes.com/t/{slug}/{topic_id}/{post_number}`

## Työnkulku

1. **Hae** keskusteluja hakurajapinnasta (1-3 sivua riippuen tuloksista ja --deep-flagista)
2. **Täydennä** tagi-haulla jos aihe on yhtiö tai tunnettu termi
3. **Analysoi** tulokset: tunnista eniten tykätyt/kommentoidut viestit, toistuvat teemat, merkittävät näkemykset
4. **Syntetisoi** katsaus suomeksi seuraavalla rakenteella:

### Vastauksen rakenne

- **Yhteenveto**: 2-3 lauseen tiivistys mitä yhteisö ajattelee aiheesta
- **Keskeiset teemat**: 3-5 päälöydöstä tai -tunnelmaa
- **Merkittävät näkemykset**: Kiinnostavimmat mielipiteet — sisällytä suoria lainauksia ja linkit alkuperäisiin viesteihin
- **Yhteisön sentimentti**: Yleinen arvio (positiivinen/negatiivinen/neutraali, bullish/bearish)
- **Tilastot**: Montako viestiä/keskustelua löytyi, aktiivisimmat keskustelijat, suosituimmat ketjut
- **Linkit**: Listaa tärkeimmät keskusteluketjut linkkeineen

## Huomioita

- Vastaa aina suomeksi
- Sisällytä suoria lainauksia foorumilta kun ne ovat osuvia
- Viittaa aina alkuperäislähteisiin linkeillä
- Huomioi tykkäysmäärät — paljon tykätyt viestit edustavat yhteisön mielipidettä paremmin
- Discourse rate limit: ~12 req/s. Jos saat 429-vastauksen, odota Retry-After-headerin ilmoittama aika.
- Tagit voivat olla dictejä (`{"name": "nokia"}`) — käytä name-kenttää

## Esimerkkejä
- /last30inderes tekoäly
- /last30inderes Fortum --days 7
- /last30inderes "asuntomarkkina 2026" --category talous-ja-markkinat
- /last30inderes Remedy --deep
- /last30inderes "korkosijoitukset" --days 14
