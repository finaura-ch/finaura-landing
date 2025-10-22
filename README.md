
# FINAURA Landingpage v1.0.0

## Quickstart
```bash
npm install
npm run dev
```
Open http://localhost:3000

### CTA-Link setzen
In `app/page.tsx` die Zeile
```tsx
<Button href="#" variant="primary">Jetzt anonym starten</Button>
```
auf eure Streamlit-URL ändern, z. B.:
```tsx
<Button href="https://finaura.streamlit.app" variant="primary">Jetzt anonym starten</Button>
```
