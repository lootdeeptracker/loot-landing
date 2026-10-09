#!/usr/bin/env python3
# ============================================================================
# OS IDIOMAS DO SITE (09/10/2026). Português na raiz; inglês, russo e espanhol em /en/, /ru/ e /es/, com o MESMO nome
# de arquivo. Este script põe a "fiação" em todas as páginas, nos quatro idiomas, e pode rodar de novo sem duplicar
# nada (tudo o que ele escreve fica entre marcadores `idiomas:`):
#   - o seletor PT · EN · RU · ES no menu, que leva à MESMA página no outro idioma e guarda a escolha;
#   - canonical, og:url, og:locale e os hreflang de cada página (o Google indexa cada idioma separado);
#   - nas páginas em português, a ida automática ao idioma do navegador na PRIMEIRA visita (navegador sem nenhum dos
#     quatro vai para o inglês; nunca para robô de busca, nunca depois de a pessoa escolher um idioma no seletor);
#   - os caminhos de assets nas pastas de idioma (`./assets/` → `/assets/`) e o simulador de cada idioma;
#   - a Oswald como reserva da Pathway Gothic One, que não tem letras russas (o mesmo que o app faz nos títulos);
#   - o sitemap com as quatro versões de cada página.
# Uso: python3 tools/idiomas.py   (na raiz do repositório)
# 🔒 O texto traduzido NÃO sai daqui: cada /<idioma>/arquivo.html é a tradução do arquivo da raiz. Mudou o português,
#    muda as três traduções e roda este script.
# ============================================================================
import os, re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://www.lootdeep.com'
IDIOMAS = ['pt', 'en', 'ru', 'es']
OG_LOCALE = {'pt': 'pt_BR', 'en': 'en_US', 'ru': 'ru_RU', 'es': 'es_ES'}
ROTULO = {'pt': 'Idioma', 'en': 'Language', 'ru': 'Язык', 'es': 'Idioma'}
PAGINAS = ['index.html', 'guias.html', 'manual-jogador.html', 'manual-coach.html', 'manual-eqty.html']


def caminho(lang, pagina):
    """A URL pública da página naquele idioma (o index é a pasta)."""
    base = '/' if lang == 'pt' else f'/{lang}/'
    return base if pagina == 'index.html' else base + pagina


def bloco(nome, conteudo):
    return f'<!-- idiomas:{nome} -->{conteudo}<!-- /idiomas:{nome} -->'


def trocar_bloco(s, nome, conteudo, ancora_antes):
    """Põe (ou atualiza) o bloco marcado; na primeira vez entra logo antes de `ancora_antes`."""
    novo = bloco(nome, conteudo)
    padrao = re.compile(rf'<!-- idiomas:{nome} -->[\s\S]*?<!-- /idiomas:{nome} -->')
    if padrao.search(s):
        return padrao.sub(lambda _: novo, s, count=1)
    i = s.index(ancora_antes)
    return s[:i] + novo + '\n  ' + s[i:]


CSS_SELETOR = (
    '.idiomas{display:flex;align-items:center;gap:2px;padding:2px;border-radius:8px;border:1px solid rgba(255,255,255,.08);'
    'font-family:\'Geist Mono\',ui-monospace,monospace;font-size:11px;letter-spacing:.04em;flex-shrink:0}'
    '.idiomas a{display:inline-flex;align-items:center;justify-content:center;min-width:28px;height:24px;padding:0 6px;'
    'border-radius:6px;color:#80858C;text-decoration:none;transition:color .15s,background .15s}'
    '.idiomas a:hover{color:#EDEEF0}'
    '.idiomas a[aria-current="true"]{color:#EDEEF0;background:rgba(255,255,255,.08)}'
    # no celular o seletor vira um botão só (o idioma atual) que abre a lista: o menu não tem largura para os quatro
    '.idiomas-m{display:none;position:relative;flex-shrink:0;font-family:\'Geist Mono\',ui-monospace,monospace;font-size:12px}'
    '.idiomas-m summary{list-style:none;cursor:pointer;display:inline-flex;align-items:center;gap:6px;height:32px;padding:0 10px;'
    'border-radius:8px;border:1px solid rgba(255,255,255,.1);color:#EDEEF0}'
    '.idiomas-m summary::-webkit-details-marker{display:none}'
    '.idiomas-m summary::after{content:"";width:6px;height:6px;border-right:1.5px solid #80858C;border-bottom:1.5px solid #80858C;transform:translateY(-2px) rotate(45deg)}'
    '.idiomas-m[open] summary::after{transform:translateY(1px) rotate(225deg)}'
    '.idiomas-m .lista{position:absolute;top:calc(100% + 6px);right:0;min-width:120px;display:flex;flex-direction:column;padding:4px;'
    'border-radius:10px;border:1px solid rgba(255,255,255,.1);background:#0B0C0D;box-shadow:0 12px 32px rgba(0,0,0,.6);z-index:30}'
    '.idiomas-m .lista a{display:flex;justify-content:space-between;gap:12px;padding:8px 10px;border-radius:6px;color:#80858C;text-decoration:none}'
    '.idiomas-m .lista a[aria-current="true"]{color:#EDEEF0;background:rgba(255,255,255,.06)}'
    '.nav .btn{white-space:nowrap}'
    '@media (max-width:640px){.idiomas{display:none}.idiomas-m{display:block}}'
)

NOME = {'pt': 'Português', 'en': 'English', 'ru': 'Русский', 'es': 'Español'}

# fecha a lista do celular ao tocar fora dela
JS_FECHAR = ("document.addEventListener('click',function(e){var d=document.querySelector('details.idiomas-m[open]');"
             "if(d&&!d.contains(e.target))d.removeAttribute('open')});")

# a escolha no seletor vale para as próximas visitas (e desliga a ida automática)
JS_ESCOLHA = "try{localStorage.setItem('loot_idioma',this.dataset.idioma)}catch(e){}"

# 🔒 Só nas páginas em português. Vai ao idioma do navegador UMA vez: quem já escolheu no seletor fica onde escolheu,
#    robô de busca nunca é redirecionado (o português tem de continuar indexado), e português no navegador fica.
JS_PRIMEIRA_VISITA = (
    "(function(){try{if(localStorage.getItem('loot_idioma'))return}catch(e){return}"
    "if(/bot|crawl|spider|slurp|lighthouse|headless/i.test(navigator.userAgent)||navigator.webdriver)return;"
    "var ls=navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language||''];"
    "for(var i=0;i<ls.length;i++){var b=String(ls[i]).toLowerCase().split('-')[0];if(b==='pt')return;"
    "if(b==='en'||b==='ru'||b==='es'){try{localStorage.setItem('loot_idioma',b)}catch(e){}"
    "location.replace('/'+b+location.pathname+location.search+location.hash);return}}"
    # nenhum dos quatro no navegador (alemão, francês...): o inglês serve melhor que o português
    "try{localStorage.setItem('loot_idioma','en')}catch(e){}location.replace('/en'+location.pathname+location.search+location.hash)})();"
)


ATUAL = ' aria-current="true"'


def seletor(lang, pagina):
    links = ''.join(
        f'<a href="{caminho(l, pagina)}" hreflang="{l}" lang="{l}" data-idioma="{l}"'
        f'{ATUAL if l == lang else ""} onclick="{JS_ESCOLHA}">{l.upper()}</a>'
        for l in IDIOMAS
    )
    lista = ''.join(
        f'<a href="{caminho(l, pagina)}" hreflang="{l}" lang="{l}" data-idioma="{l}"'
        f'{ATUAL if l == lang else ""} onclick="{JS_ESCOLHA}">{NOME[l]}<span>{l.upper()}</span></a>'
        for l in IDIOMAS
    )
    return (f'<div class="idiomas" role="group" aria-label="{ROTULO[lang]}">{links}</div>'
            f'<details class="idiomas-m"><summary aria-label="{ROTULO[lang]}">{lang.upper()}</summary>'
            f'<div class="lista">{lista}</div></details>')


def cabecalho(lang, pagina, indexavel):
    partes = []
    if indexavel:
        # 🔒 os manuais e o guia são `noindex` por decisão (09/2026): sem canonical nem hreflang, e fora do sitemap
        partes.append(f'<link rel="canonical" href="{SITE}{caminho(lang, pagina)}" />')
        partes += [f'<link rel="alternate" hreflang="{l}" href="{SITE}{caminho(l, pagina)}" />' for l in IDIOMAS]
        partes.append(f'<link rel="alternate" hreflang="x-default" href="{SITE}{caminho("pt", pagina)}" />')
    if lang == 'ru':
        # a Pathway Gothic One não tem cirílico: a Oswald entra só para as letras russas dos títulos
        partes.append('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@400&amp;display=swap" />')
    partes.append(f'<style>{CSS_SELETOR}</style>')
    partes.append(f'<script>{JS_FECHAR}</script>')
    if lang == 'pt':
        partes.append(f'<script>{JS_PRIMEIRA_VISITA}</script>')
    return '\n  '.join(partes)


def processar_pagina(lang, pagina):
    arq = os.path.join(RAIZ, pagina) if lang == 'pt' else os.path.join(RAIZ, lang, pagina)
    s = open(arq, encoding='utf-8').read()
    indexavel = 'noindex' not in s
    # o canonical antigo (fora do bloco) sai: quem manda é o do bloco
    if '<!-- idiomas:cabecalho -->' not in s:
        s = re.sub(r'\n[ \t]*<link rel="canonical"[^>]*>', '', s)
    s = re.sub(r'(<meta property="og:url" content=")[^"]*(")', rf'\g<1>{SITE}{caminho(lang, pagina)}\g<2>', s)
    s = re.sub(r'(<meta property="og:locale" content=")[^"]*(")', rf'\g<1>{OG_LOCALE[lang]}\g<2>', s)
    s = trocar_bloco(s, 'cabecalho', cabecalho(lang, pagina, indexavel), '</head>')
    # o seletor entra no menu, logo antes do botão de entrar/falar (o último item do menu)
    nav = re.search(r'<nav class="nav"[\s\S]*?</nav>', s).group(0)
    if '<!-- idiomas:seletor -->' in nav:
        nav_novo = re.sub(r'<!-- idiomas:seletor -->[\s\S]*?<!-- /idiomas:seletor -->', bloco('seletor', seletor(lang, pagina)), nav)
    else:
        ultimo = list(re.finditer(r'\n(\s*)<a class="btn', nav))[-1]
        nav_novo = nav[:ultimo.start()] + '\n' + ultimo.group(1) + bloco('seletor', seletor(lang, pagina)) + nav[ultimo.start():]
    s = s.replace(nav, nav_novo)
    if lang != 'pt':
        s = s.replace('"./assets/', '"/assets/')
    if lang == 'ru':
        s = s.replace("'Pathway Gothic One', sans-serif", "'Pathway Gothic One', 'Oswald', sans-serif")
    open(arq, 'w', encoding='utf-8').write(s)


def processar_simulador(lang):
    """O simulador de cada idioma: o mesmo motor (/sim/dc.js), as telas traduzidas da pasta do idioma."""
    orig = open(os.path.join(RAIZ, 'sim', 'index.html'), encoding='utf-8').read()
    s = orig.replace('<html lang="pt-BR">', f'<html lang="{lang}">')
    s = s.replace("window.DC_BASE = '/sim/';", f"window.DC_BASE = '/{lang}/sim/';")
    titulo = {'en': 'Loot simulator', 'ru': 'Симулятор Loot', 'es': 'Simulador de Loot'}[lang]
    s = s.replace('<title>Simulador do Loot</title>', f'<title>{titulo}</title>')
    open(os.path.join(RAIZ, lang, 'sim', 'index.html'), 'w', encoding='utf-8').write(s)
    if lang == 'ru':
        for nome in os.listdir(os.path.join(RAIZ, 'ru', 'sim')):
            if nome.endswith('.dc.html'):
                p = os.path.join(RAIZ, 'ru', 'sim', nome)
                t = open(p, encoding='utf-8').read()
                t = t.replace("'Pathway Gothic One', sans-serif", "'Pathway Gothic One', 'Oswald', sans-serif")
                t = t.replace('family=Pathway+Gothic+One&amp;', 'family=Pathway+Gothic+One&amp;family=Oswald:wght@400&amp;')
                open(p, 'w', encoding='utf-8').write(t)


def sitemap():
    urls = []
    for pagina in [p for p in PAGINAS if 'noindex' not in open(os.path.join(RAIZ, p), encoding='utf-8').read()]:
        alternativas = ''.join(
            f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{SITE}{caminho(l, pagina)}" />' for l in IDIOMAS
        ) + f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{caminho("pt", pagina)}" />'
        for l in IDIOMAS:
            prioridade = '1.0' if pagina == 'index.html' else '0.6'
            urls.append(f'  <url>\n    <loc>{SITE}{caminho(l, pagina)}</loc>{alternativas}\n    <changefreq>weekly</changefreq>\n    <priority>{prioridade}</priority>\n  </url>')
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
           + '\n'.join(urls) + '\n</urlset>\n')
    open(os.path.join(RAIZ, 'sitemap.xml'), 'w', encoding='utf-8').write(xml)


if __name__ == '__main__':
    for lang in IDIOMAS:
        for pagina in PAGINAS:
            processar_pagina(lang, pagina)
        if lang != 'pt':
            processar_simulador(lang)
    # a reserva de fonte do css dos manuais vale para todos (sem a Oswald carregada, nada muda fora do russo)
    css = os.path.join(RAIZ, 'assets', 'docs.css')
    c = open(css, encoding='utf-8').read()
    if "'Oswald'" not in c:
        open(css, 'w', encoding='utf-8').write(c.replace("'Pathway Gothic One', sans-serif", "'Pathway Gothic One', 'Oswald', sans-serif"))
    sitemap()
    print('ok')
