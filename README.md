# EXIT Toys Crawler - Kennisbank voor HALO Chatbot

## Wat doet dit systeem?

Dit systeem zorgt ervoor dat de **HALO AI-chatbot** altijd up-to-date productinformatie heeft van de EXIT Toys website. Het werkt volledig automatisch:

1. Elke ochtend om **06:00 uur** wordt de hele exittoys.nl website gescand
2. Alle producten, veelgestelde vragen (FAQs), blogposts en pagina's worden verzameld
3. Deze data wordt opgeslagen als "kennisbank" in de cloud
4. HALO haalt deze kennisbank automatisch op en gebruikt het om vragen te beantwoorden

**Je hoeft hier normaal gesproken niets aan te doen** - alles draait automatisch.

---

## Hoe werkt het? (simpele uitleg)

```
exittoys.nl website
        |
        v
  [GitHub Actions]        <-- Automatische taakplanner (draait elke ochtend)
        |
        v
  [Python Crawler]        <-- Leest alle pagina's van de website
        |
        v
  [Kennisbank JSON]       <-- Alle info in een gestructureerd bestand
        |
        v
  [Vercel Blob Storage]   <-- Cloudopslag waar het bestand wordt bewaard
        |
        v
  [API Endpoint]          <-- Adres waar HALO de data ophaalt
        |
        v
  [CM HALO Chatbot]       <-- Beantwoordt klantvragen met actuele info
```

### De drie systemen uitgelegd

| Systeem | Wat het doet | Vergelijking |
|---------|-------------|--------------|
| **GitHub Actions** | Plant en start de dagelijkse crawl automatisch | Een wekker die elke ochtend een taak start |
| **Vercel** | Host het dashboard en de API waar HALO data ophaalt | Een website met een digitale kluis voor de data |
| **HALO** | De AI-chatbot die klantvragen beantwoordt | De medewerker die het antwoordenboek gebruikt |

---

## Dashboard bekijken

Het dashboard toont de status van de kennisbank:

**URL:** https://exit-toys-crawler-vercel.vercel.app

Hier zie je:
- **Laatste update** - Wanneer de crawler voor het laatst heeft gedraaid
- **Totaal entries** - Hoeveel items er in de kennisbank zitten
- **Verdeling** - Hoeveel producten, FAQs, blogs en pagina's

Als je hier "Nog geen data beschikbaar" ziet, heeft de crawler nog niet gedraaid.

---

## Handmatig een crawl starten

Soms wil je de kennisbank direct bijwerken, bijvoorbeeld na een grote productwijziging op de website. Dit doe je zo:

### Stap voor stap

1. **Ga naar GitHub Actions:**
   - Open https://github.com/svendijk2408/exit-toys-crawler-vercel/actions
   - Log in met het EXIT GitHub-account

2. **Selecteer de workflow:**
   - Klik links op **"EXIT Toys Crawler"**

3. **Start de crawl:**
   - Klik op de **"Run workflow"** knop (rechtsboven, grijs)
   - Klik op de groene **"Run workflow"** knop in het dropdown-menu

4. **Wacht tot het klaar is:**
   - Je ziet een nieuwe run verschijnen met een geel bolletje (= bezig)
   - Na 20-45 minuten wordt dit een groen vinkje (= gelukt) of een rood kruisje (= mislukt)

5. **Controleer het resultaat:**
   - Ga naar het dashboard: https://exit-toys-crawler-vercel.vercel.app
   - Controleer of de "Laatste update" is bijgewerkt

### Let op

- **Start geen nieuwe crawl als er al een draait** - je kunt dit zien aan het gele bolletje bij de lopende run
- De crawl duurt 20-45 minuten, dit is normaal
- Als een crawl mislukt (rood kruisje), probeer het nog een keer. Lukt het daarna nog niet? Neem contact op met Sven

---

## Wat wordt er precies gecrawld?

| Type | Wat | Voorbeelden |
|------|-----|-------------|
| **Producten** | Alle productpagina's | Trampolines, zwembaden, speelhuisjes, sport |
| **FAQs** | Veelgestelde vragen | Levering, retourneren, veiligheid, onderhoud |
| **Blogs** | Alle blogartikelen | Tips, gidsen, productnieuws |
| **Pagina's** | Informatiepagina's | Over ons, contact, leveringsinfo |

De crawler slaat de volgende pagina's bewust over: homepage, zoekpagina, winkelwagen, account en checkout.

---

## Hoe komt de data in HALO?

HALO is gekoppeld via een **API Connection**. Dit werkt als volgt:

1. HALO is ingesteld om data op te halen van dit adres:
   ```
   GET https://exit-toys-crawler-vercel.vercel.app/api/knowledge-base
   ```
2. Dit endpoint geeft een lijst terug met items, elk met:
   - **trigger** - Zoekwoorden (productnaam, artikelnummer, categorie)
   - **content** - De volledige productinfo, specificaties, FAQ-antwoorden, etc.
3. Wanneer een klant een vraag stelt, zoekt HALO in de triggers naar relevante items
4. De bijbehorende content wordt gebruikt om een antwoord te formuleren

**De HALO-koppeling hoeft niet aangepast te worden** - zolang de crawler draait, blijft de data actueel.

---

## Veelgestelde vragen

### De crawler is mislukt, wat nu?
1. Ga naar GitHub Actions en klik op de mislukte run (rood kruisje)
2. Klik op **"crawl-and-upload"** om de logberichten te zien
3. Meestal is het een tijdelijk probleem (website traag, time-out). Probeer het opnieuw via "Run workflow"
4. Lukt het na 2 pogingen niet? Neem contact op met Sven

### De chatbot geeft verouderde informatie
Controleer op het dashboard wanneer de laatste update was. Als dit meer dan 2 dagen geleden is, start handmatig een crawl. Als de crawl wel recent is maar de info niet klopt, kan het zijn dat:
- De website nog niet is bijgewerkt
- HALO de cache nog niet heeft ververst (duurt maximaal 1 uur)

### Er is een nieuw product toegevoegd aan de website
De crawler pikt dit automatisch op bij de volgende run (06:00 uur). Wil je het sneller? Start handmatig een crawl.

### Kan ik zien wat er in de kennisbank zit?
Ja, open deze URL in je browser:
```
https://exit-toys-crawler-vercel.vercel.app/api/knowledge-base
```
Je krijgt dan de volledige kennisbank te zien als tekst (dit is het ruwe bestand dat HALO gebruikt).

### Hoeveel kost dit systeem?
- **GitHub Actions**: Gratis (binnen de gratis limiet van GitHub)
- **Vercel**: Gratis (Hobby plan, voldoende voor dit gebruik)
- **Totaal**: Geen kosten

---

## Overzicht van de automatische planning

| Wat | Wanneer | Hoe |
|-----|---------|-----|
| Crawler draait | Elke dag om 06:00 NL | Automatisch via GitHub Actions |
| Kennisbank wordt bijgewerkt | Direct na succesvolle crawl | Automatisch upload naar Vercel |
| HALO haalt nieuwe data op | Bij elk klantgesprek (met 1 uur cache) | Automatisch via API |

---

## Technische details (voor ontwikkelaars)

<details>
<summary>Klik om technische details te bekijken</summary>

### Stack
- **Crawler**: Python 3.12 (aiohttp, BeautifulSoup4, Playwright)
- **Frontend/API**: Next.js 16, React 19, TypeScript
- **Hosting**: Vercel (Edge runtime)
- **Opslag**: Vercel Blob Storage
- **CI/CD**: GitHub Actions

### Repository
https://github.com/svendijk2408/exit-toys-crawler-vercel

### Projectstructuur
```
exit-toys-crawler-vercel/
├── .github/workflows/crawl.yml    # Automatische planning
├── crawler/                        # Python webcrawler
│   ├── crawlers/                   # URL-discovery en ophalen
│   ├── parsers/                    # HTML-extractie
│   ├── formatters/                 # Data-formattering
│   ├── utils/                      # Hulpfuncties
│   ├── config.py                   # Configuratie
│   └── main.py                     # Startpunt
├── src/app/                        # Next.js frontend
│   ├── api/knowledge-base/route.ts # API-endpoint
│   └── page.tsx                    # Dashboard
├── scripts/upload-to-blob.mjs      # Upload script
├── vercel.json                     # Vercel configuratie
└── package.json                    # Node.js dependencies
```

### Environment variabelen
- `BLOB_READ_WRITE_TOKEN` - Vercel Blob Storage token (opgeslagen in GitHub Secrets)

### Rate limiting
- Max 3 gelijktijdige requests naar exittoys.nl
- Max 2 requests per seconde
- 30 seconden timeout per request
- Automatische retry (max 3 pogingen)

### API Response format
```json
[
  {
    "trigger": "EXIT Elegant Premium Trampoline 244 52.74.10.00",
    "content": "Product: EXIT Elegant Premium Trampoline\nPrijs: ..."
  }
]
```

</details>
