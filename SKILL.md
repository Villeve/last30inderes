# last30inderes

Tutki mitä suomalainen sijoittajayhteisö keskustelee Inderes-foorumilla tietystä aiheesta.

## Käyttö
/last30inderes <aihe> [--days N] [--deep] [--category SLUG]

## Argumentit
- aihe: Tutkittava aihe (yrityksen nimi, markkinakonsepti, sektori jne.)
- --days N: Aikaväli päivissä (oletus: 30, max: 90)
- --deep: Hae viestien koko sisältö (hitaampi mutta tarkempi)
- --category SLUG: Rajaa kategoriaan (esim. osakkeet, sijoittaminen, talous-ja-markkinat)

## Työnkulku
1. Jäsennä aihe ja määritä hakustrategia
2. Suorita: python3 scripts/inderes_fetch.py "{aihe}" --days {N} [--deep] [--category {slug}]
3. Lue tuotos (pisteytetyt viestit markdown-muodossa)
4. Tiivistä löydökset katsaukseksi: "Mitä suomalainen sijoittajayhteisö keskustelee aiheesta {aihe}?"
5. Rakenna vastaus seuraavasti:
   - **Keskeiset teemat**: 3-5 päälöydöstä tai -tunnelmaa
   - **Merkittävät näkemykset**: Kiinnostavimmat mielipiteet lähdeviitteineen
   - **Yhteisön sentimentti**: Yleinen arvio (positiivinen/negatiivinen/neutraali, bullish/bearish)
   - **Tilastot**: Yhteenveto aktiivisuudesta
6. Viittaa aina alkuperäislähteisiin linkeillä
7. Vastaa suomeksi. Sisällytä suoria lainauksia foorumilta.

## Oikeudet
- Bash: python3-skriptien suoritus (scripts/-hakemisto)

## Esimerkkejä
- /last30inderes Nokia
- /last30inderes osingot --days 7
- /last30inderes "asuntomarkkina 2026" --category talous-ja-markkinat
- /last30inderes Remedy --deep
- /last30inderes "korkosijoitukset" --days 14
