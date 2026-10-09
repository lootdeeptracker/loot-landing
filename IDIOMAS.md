# Idiomas do site

Português na raiz. Inglês, russo e espanhol em `/en/`, `/ru/` e `/es/`, com o mesmo nome de arquivo
(`manual-jogador.html` → `en/manual-jogador.html`). O simulador de cada idioma fica em `/<idioma>/sim/` e usa o mesmo
motor (`/sim/dc.js`) e as mesmas imagens (`/sim/img/`).

**Mudou um texto em português?** Mude também as três traduções e rode, na raiz do repositório:

```
python3 tools/idiomas.py
```

O script põe (e atualiza, sem duplicar) em todas as páginas: o seletor PT · EN · RU · ES, canonical e hreflang, a ida
automática ao idioma do navegador na primeira visita (só nas páginas em português; navegador em outro idioma vai para o
inglês; robô de busca nunca é redirecionado), os caminhos de `/assets/`, a fonte Oswald para os títulos em russo e o
`sitemap.xml`.

Página nova: crie as quatro versões e acrescente o nome em `PAGINAS` no `tools/idiomas.py`.
Glossário dos termos: `docs/i18n-glossario.md` do repositório do app.
