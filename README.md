# MiniBlocket – Flask (individuell fördjupning)

Liten prototyp för den individuella fördjupningen i Development of Web Applications (C1UT1B).

Samma domän som labb 2 (MiniBlocket): annonser. Här är det **bara en entitet**, `Listing`, med CRUD. Ingen inloggning, roller eller Azure. Det är medvetet, eftersom uppgiften ber om en mikro-artefakt på cirka 4–8 timmar.

**Spår:** B, standalone micro-prototype  
**Ramverk:** Flask 3  
**Jämförelse:** ASP.NET Core MVC i labb 2

## Köra

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Öppna http://127.0.0.1:5000

Första starten skapar `listings.db` och två exempelannonser. Filen ligger inte i git.

## Vad som finns

- Lista, skapa, visa, redigera, ta bort
- Fritextsök och kategorifilter
- Validering på servern (tom titel, fel pris, ogiltig kategori)

## Filer

- `app.py` – routes och SQLite
- `templates/` – Jinja-vyer
- `static/style.css`
