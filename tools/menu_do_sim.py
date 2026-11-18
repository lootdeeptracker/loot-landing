#!/usr/bin/env python3
# ============================================================================
# O MENU DO SIMULADOR (18/11/2026). A barra lateral e os ícones do header das 10 telas do simulador, nos 4 idiomas,
# saem DAQUI, espelhando o menu do app (loot-app: lib/services/menuDoLoot.ts, components/layout/dashboard-header.tsx).
#
# Por que existe: cada Sim-*.dc.html tinha a SUA cópia do menu (40 cópias, em 4 formatos), e as cópias divergiram do app
# e entre si (ícones diferentes por tela, idiomas com rótulo em português, itens novos do app faltando).
#
# O que ele reescreve em cada tela (e só isto; o resto da tela não é tocado):
#   - as declarações `var NAV`, `var ICP`, `var IDS`, `var BETA`, `var NM` e `var ATIVO` (cada tela mantém o formato dela);
#   - no header, o envelope antigo vira o balão do Chat, e entra a coroa do Battle antes do calendário.
# Regra do app que vale aqui: só a seção da tela fica aberta (sidebar.tsx abre a seção do item ativo).
# Os ícones são os do app: o desenho do lucide (e o "duas cartas" do Hands, e a coroa do header) em um path só.
#
# Uso: python3 tools/menu_do_sim.py   (na raiz do repositório; roda de novo sem duplicar nada)
# Mudou o menu do app: mude ITENS/LIDER/JOGADOR/ROTULOS abaixo e rode.
# ============================================================================
import os, re, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDIOMAS = {'pt': 'sim', 'en': 'en/sim', 'es': 'es/sim', 'ru': 'ru/sim'}

# a ordem e o selo beta são os do app (LIDER_NAV e PLAYER_NAV); o 2º campo é a tela do simulador que o item abre
LIDER = [('time', 'time'), ('gestao', 'gestao'), ('financeiro', 'financeiro'), ('report', 'report'), ('coaches', None),
         ('jogadores', None), ('candidaturas', None), ('discussoes', None), ('videoteca', None), ('transacoes', None),
         ('performance', None), ('torneios', None), ('analises', 'analises'), ('battle', None), ('grades', None),
         ('config', None)]
JOGADOR = [('dashboard', 'dashboard'), ('folha', 'folha'), ('report', None), ('schedule', 'schedule'), ('stats', 'stats'),
           ('eqty', None), ('hands', None), ('discussoes', None), ('videoteca', None), ('performance', 'performance'),
           ('torneios', None), ('analises', None), ('battle', None), ('transacoes', None)]
BETA = {('lider', 'grades'), ('jogador', 'schedule')}

# os rótulos do app (lib/i18n/textos/casca e base/papeis): pt, en, es, ru
ROTULOS = {
    'lider': ('Líder', 'Leader', 'Líder', 'Руководитель'),
    'coach': ('Coach', 'Coach', 'Coach', 'Тренер'),
    'jogador': ('Jogador', 'Player', 'Jugador', 'Игрок'),
    'time': ('Time', 'Team', 'Equipo', 'Команда'),
    'gestao': ('Gestão', 'Management', 'Gestión', 'Менеджер'),
    'financeiro': ('Financeiro', 'Finance', 'Finanzas', 'Финансы'),
    'report': ('Report', 'Report', 'Report', 'Report'),
    'coaches': ('Coaches', 'Coaches', 'Coaches', 'Тренеры'),
    'jogadores': ('Jogadores', 'Players', 'Jugadores', 'Игроки'),
    'candidaturas': ('Candidaturas', 'Applications', 'Postulaciones', 'Заявки'),
    'discussoes': ('Discussões', 'Discussions', 'Discusiones', 'Разборы'),
    'videoteca': ('Videoteca', 'Video library', 'Videoteca', 'Видеотека'),
    'transacoes': ('Transações', 'Transactions', 'Transacciones', 'Транзакции'),
    'performance': ('Performance', 'Performance', 'Performance', 'Performance'),
    'torneios': ('Torneios', 'Tournaments', 'Torneos', 'Турниры'),
    'analises': ('Análises', 'Analyses', 'Análisis', 'Аналитика'),
    'battle': ('Battle', 'Battle', 'Battle', 'Battle'),
    'grades': ('Grades', 'Lineups', 'Grillas', 'Сетки'),
    'config': ('Config.', 'Settings', 'Configuración', 'Настройки'),
    'dashboard': ('Dashboard', 'Dashboard', 'Dashboard', 'Дашборд'),
    'folha': ('Minha Folha', 'My ledger', 'Mi registro', 'Мой учёт'),
    'schedule': ('Schedule', 'Schedule', 'Schedule', 'Schedule'),
    'stats': ('Stats', 'Stats', 'Stats', 'Stats'),
    'eqty': ('Eq&ty', 'Eq&ty', 'Eq&ty', 'Eq&ty'),
    'hands': ('Hands', 'Hands', 'Hands', 'Hands'),
}
POS = {'pt': 0, 'en': 1, 'es': 2, 'ru': 3}

# a tela → o item aceso (seção, item)
ATIVO = {
    'Time': ('lider', 'time'), 'Gestao': ('lider', 'gestao'), 'Financeiro': ('lider', 'financeiro'),
    'Report': ('lider', 'report'), 'Analises': ('lider', 'analises'), 'Dashboard': ('jogador', 'dashboard'),
    'Folha': ('jogador', 'folha'), 'Stats': ('jogador', 'stats'), 'Schedule': ('jogador', 'schedule'),
    'Performance': ('jogador', 'performance'),
}
COD = {'lider': 'L', 'coach': 'C', 'jogador': 'J'}

# os ícones do app em um path só (grade 24): lucide v1.7 (o do menuDoLoot.ts), "duas cartas" do Hands e a coroa do header
ICONES = {
    'time': 'M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519l-2.834 10.246a1 1 0 0 1-.956.734H5.81a1 1 0 0 1-.957-.734L2.02 6.02a.5.5 0 0 1 .798-.519l4.276 3.664a1 1 0 0 0 1.516-.294zM5 21h14',
    'gestao': 'M4 3h5a1 1 0 0 1 1 1v7a1 1 0 0 1 -1 1h-5a1 1 0 0 1 -1 -1v-7a1 1 0 0 1 1 -1ZM15 3h5a1 1 0 0 1 1 1v3a1 1 0 0 1 -1 1h-5a1 1 0 0 1 -1 -1v-3a1 1 0 0 1 1 -1ZM15 12h5a1 1 0 0 1 1 1v7a1 1 0 0 1 -1 1h-5a1 1 0 0 1 -1 -1v-7a1 1 0 0 1 1 -1ZM4 16h5a1 1 0 0 1 1 1v3a1 1 0 0 1 -1 1h-5a1 1 0 0 1 -1 -1v-3a1 1 0 0 1 1 -1Z',
    'financeiro': 'M12 2L12 22M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6',
    'report': 'M21 12c.552 0 1.005-.449.95-.998a10 10 0 0 0-8.953-8.951c-.55-.055-.998.398-.998.95v8a1 1 0 0 0 1 1zM21.21 15.89A10 10 0 1 1 8 2.83',
    'coaches': 'M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0zM22 10v6M6 12.5V16a6 3 0 0 0 12 0v-3.5',
    'jogadores': 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M16 3.128a4 4 0 0 1 0 7.744M22 21v-2a4 4 0 0 0-3-3.87M5 7a4 4 0 1 0 8 0a4 4 0 1 0 -8 0',
    'candidaturas': 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M5 7a4 4 0 1 0 8 0a4 4 0 1 0 -8 0M19 8L19 14M22 11L16 11',
    'discussoes': 'M16 10a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 14.286V4a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2zM20 9a2 2 0 0 1 2 2v10.286a.71.71 0 0 1-1.212.502l-2.202-2.202A2 2 0 0 0 17.172 19H10a2 2 0 0 1-2-2v-1',
    'videoteca': 'M12.296 3.464l3.02 3.956M20.2 6 3 11l-.9-2.4c-.3-1.1.3-2.2 1.3-2.5l13.5-4c1.1-.3 2.2.3 2.5 1.3zM3 11h18v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2zM6.18 5.276l3.1 3.899',
    'transacoes': 'M8 3 4 7l4 4M4 7h16M16 21l4-4-4-4M20 17H4',
    'performance': 'M16 7h6v6M22 7l-8.5 8.5-5-5L2 17',
    'torneios': 'M10 14.66v1.626a2 2 0 0 1-.976 1.696A5 5 0 0 0 7 21.978M14 14.66v1.626a2 2 0 0 0 .976 1.696A5 5 0 0 1 17 21.978M18 9h1.5a1 1 0 0 0 0-5H18M4 22h16M6 9a6 6 0 0 0 12 0V3a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1zM6 9H4.5a1 1 0 0 1 0-5H6',
    'analises': 'M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2zM14 2v5a1 1 0 0 0 1 1h5M8 18v-1M12 18v-6M16 18v-3',
    'battle': 'M14.5 17.5L3 6L3 3L6 3L17.5 14.5M13 19L19 13M16 16L20 20M19 21L21 19M14.5 6.5L18 3L21 3L21 6L17.5 9.5M5 14L9 18M7 17L4 20M3 19L5 21',
    'grades': 'M16 19h6M16 2v4M19 16v6M21 12.598V6a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h8.5M3 10h18M8 2v4',
    'config': 'M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915M9 12a3 3 0 1 0 6 0a3 3 0 1 0 -6 0',
    'dashboard': 'M4 3h5a1 1 0 0 1 1 1v7a1 1 0 0 1 -1 1h-5a1 1 0 0 1 -1 -1v-7a1 1 0 0 1 1 -1ZM15 3h5a1 1 0 0 1 1 1v3a1 1 0 0 1 -1 1h-5a1 1 0 0 1 -1 -1v-3a1 1 0 0 1 1 -1ZM15 12h5a1 1 0 0 1 1 1v7a1 1 0 0 1 -1 1h-5a1 1 0 0 1 -1 -1v-7a1 1 0 0 1 1 -1ZM4 16h5a1 1 0 0 1 1 1v3a1 1 0 0 1 -1 1h-5a1 1 0 0 1 -1 -1v-3a1 1 0 0 1 1 -1Z',
    'folha': 'M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2zM14 2v5a1 1 0 0 0 1 1h5M8 13h2M14 13h2M8 17h2M14 17h2',
    'schedule': 'M8 2v4M16 2v4M5 4h14a2 2 0 0 1 2 2v14a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2ZM3 10h18M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01M16 18h.01',
    'stats': 'M3 3v16a2 2 0 0 0 2 2h16M18 17V9M13 17V5M8 17v-3',
    'eqty': 'M12 18v4M2 14.499a5.5 5.5 0 0 0 9.591 3.675.6.6 0 0 1 .818.001A5.5 5.5 0 0 0 22 14.5c0-2.29-1.5-4-3-5.5l-5.492-5.312a2 2 0 0 0-3-.02L5 8.999c-1.5 1.5-3 3.2-3 5.5',
    'chat': 'M22 17a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 21.286V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2z',
    'hands': 'M9 6.4 5.1 7.1a2 2 0 0 0-1.6 2.3l1.9 10.8a2 2 0 0 0 2.3 1.6l3.3-.6M11 3h8a2 2 0 0 1 2 2v13a2 2 0 0 1 -2 2h-8a2 2 0 0 1 -2 -2v-13a2 2 0 0 1 2 -2ZM15 8.6 17.2 11.5 15 14.4 12.8 11.5z',
    'coroa': 'M3.5 8.5 8 12l4-6.5 4 6.5 4.5-3.5-1.8 10H5.3z'
}


def rot(chave, lang):
    return ROTULOS[chave][POS[lang]]


def js(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"


def secoes_do_menu(tela):
    """[(chave da seção, aberta, [(item, alvo, beta)])]: só a seção do item aceso fica aberta (sidebar.tsx)."""
    sec_ativa = ATIVO[tela][0]
    out = []
    for sec, itens in (('lider', LIDER), ('coach', []), ('jogador', JOGADOR)):
        aberta = sec == sec_ativa
        out.append((sec, aberta, [(k, alvo, (sec, k) in BETA) for k, alvo in itens] if aberta else []))
    return out


def gerar(s, tela, lang, arq):
    m_nav = re.search(r'var NAV = \[.*?\n {4}\];', s, re.S)
    if not m_nav:
        raise SystemExit(f'{arq}: sem `var NAV`')
    nav_antigo = m_nav.group(0)
    chave_aberta = 'aberto' if 'aberto:' in nav_antigo else 'aberta'
    if '{ n: ' in nav_antigo:
        formato = 'objetos'
    elif "itens: [['" in nav_antigo:
        formato = 'pares'
    elif "sec: '" in nav_antigo:
        formato = 'codigos'
    else:
        formato = 'nomes'
    tem_nm = re.search(r'var NM = \{[^\n]*\};', s) is not None
    # com NM, o menu guarda o português e o NM traduz na hora de desenhar; sem NM, o menu já guarda o rótulo do idioma
    lang_dos_nomes = 'pt' if tem_nm else lang

    def nome(k):
        return rot(k, lang_dos_nomes)

    secs = secoes_do_menu(tela)
    linhas = []
    for sec, aberta, itens in secs:
        nm_sec = nome(sec)
        ab = 'true' if aberta else 'false'
        if formato == 'objetos':
            objs = []
            for k, alvo, beta in itens:
                o = '{ n: ' + js(nome(k))
                if alvo:
                    o += ', id: ' + js(alvo)
                if beta:
                    o += ', beta: true'
                objs.append(o + ' }')
            corpo = ', '.join(objs)
        elif formato == 'pares':
            pares = []
            for k, alvo, beta in itens:
                p = [js(nome(k))]
                if alvo or beta:
                    p.append(js(alvo) if alvo else 'null')
                if beta:
                    p.append('1')
                pares.append('[' + ', '.join(p) + ']')
            corpo = ', '.join(pares)
        else:
            corpo = ', '.join(js(nome(k)) for k, _, _ in itens)
        extra = f", sec: '{COD[sec]}'" if formato == 'codigos' else ''
        linhas.append(f"      {{ nome: {js(nm_sec)}, {chave_aberta}: {ab}{extra}, itens: [{corpo}] }}")
    nav_novo = 'var NAV = [\n' + ',\n'.join(linhas) + '\n    ];'
    s = s.replace(nav_antigo, nav_novo, 1)

    def chave_mapa(sec, k):
        prefixo = COD[sec] if formato == 'codigos' else nome(sec)
        return prefixo + ':' + nome(k)

    # IDS e BETA (só os formatos que guardam o alvo e o selo fora do menu)
    if formato in ('nomes', 'codigos'):
        ids, betas = [], []
        for sec, _, itens in secoes_do_menu_completo():
            for k, alvo, beta in itens:
                if alvo:
                    ids.append(f'{js(chave_mapa(sec, k))}: {js(alvo)}')
                if beta:
                    betas.append(f'{js(chave_mapa(sec, k))}: true')
        s, n1 = re.subn(r'var IDS = \{[^\n]*\};', lambda _: 'var IDS = { ' + ', '.join(ids) + ' };', s, count=1)
        s, n2 = re.subn(r'var BETA = \{[^\n]*\};', lambda _: 'var BETA = { ' + ', '.join(betas) + ' };', s, count=1)
        if not (n1 and n2):
            raise SystemExit(f'{arq}: formato {formato} sem IDS/BETA')

    # NM: o português → o idioma (seções e itens)
    if tem_nm:
        if lang == 'pt':
            raise SystemExit(f'{arq}: NM numa tela em português')
        pares = []
        vistos = set()
        for k in ['lider', 'coach', 'jogador'] + [k for k, _ in LIDER] + [k for k, _ in JOGADOR]:
            pt, alvo = rot(k, 'pt'), rot(k, lang)
            if pt in vistos or pt == alvo:
                continue
            vistos.add(pt)
            pares.append(f'{js(pt)}: {js(alvo)}')
        s = re.sub(r'var NM = \{[^\n]*\};', lambda _: 'var NM = {' + ', '.join(pares) + '};', s, count=1)

    # ICP: um ícone por rótulo (o do app)
    icp, vistos = [], set()
    for k in [k for k, _ in LIDER] + [k for k, _ in JOGADOR]:
        n = nome(k)
        if n in vistos:
            continue
        vistos.add(n)
        icp.append(f'      {js(n)}: {js(ICONES[k])}')
    s, n3 = re.subn(r'var ICP = \{.*?\n {4}\};', lambda _: 'var ICP = {\n' + ',\n'.join(icp) + '\n    };', s, count=1, flags=re.S)
    if not n3:
        raise SystemExit(f'{arq}: sem `var ICP`')

    # ATIVO
    sec, k = ATIVO[tela]
    s, n4 = re.subn(r"var ATIVO = '[^']*';", lambda _: f'var ATIVO = {js(chave_mapa(sec, k))};', s, count=1)
    if not n4:
        raise SystemExit(f'{arq}: sem `var ATIVO`')
    return s


def secoes_do_menu_completo():
    return [('lider', True, [(k, a, ('lider', k) in BETA) for k, a in LIDER]), ('coach', False, []),
            ('jogador', True, [(k, a, ('jogador', k) in BETA) for k, a in JOGADOR])]


ENVELOPE = re.compile(r'(<button type="button" class="[^"]*") aria-label="[^"]*"([^>]*>)(<svg[^>]*viewBox="0 0 24 24"[^>]*>)'
                      r'<rect x="3" y="5\.5" width="18" height="13" rx="2\.5"></rect><path d="m3\.8 7 8\.2 6 8\.2-6"></path></svg></button>')
CALENDARIO = re.compile(r'<button type="button" class="[^"]*" aria-label="[^"]*"[^>]*>(<svg[^>]*viewBox="0 0 24 24"[^>]*>)'
                        r'<rect x="3\.5" y="5" width="17" height="15" rx="2\.5"></rect>')


def header(s, arq):
    """O header do app: o Chat é o balão (IconeDoChat) e a coroa do Battle vem antes do calendário (dashboard-header.tsx)."""
    s, n = ENVELOPE.subn(lambda m: f'{m.group(1)} aria-label="Chat"{m.group(2)}{m.group(3)}<path d="{ICONES["chat"]}"></path></svg></button>', s)
    if n == 0 and 'aria-label="Chat"' not in s:
        raise SystemExit(f'{arq}: sem o ícone de mensagens no header')
    if 'aria-label="Battle"' not in s:
        m = CALENDARIO.search(s)
        if not m:
            raise SystemExit(f'{arq}: sem o calendário no header')
        abre = re.match(r'<button[^>]*>', m.group(0)).group(0)
        abre = re.sub(r'aria-label="[^"]*"', 'aria-label="Battle"', abre)
        coroa = f'{abre}{m.group(1)}<path d="{ICONES["coroa"]}"></path></svg></button>\n'
        # a mesma indentação do calendário
        ini = s.rfind('\n', 0, m.start()) + 1
        indent = s[ini:m.start()]
        s = s[:m.start()] + coroa + indent + s[m.start():]
    return s


def main():
    mudou = 0
    for lang, pasta in IDIOMAS.items():
        for tela in ATIVO:
            arq = os.path.join(RAIZ, pasta, f'Sim-{tela}.dc.html')
            s0 = open(arq, encoding='utf-8').read()
            s = header(gerar(s0, tela, lang, arq), arq)
            if s != s0:
                open(arq, 'w', encoding='utf-8', newline='').write(s)
                mudou += 1
    print(f'menu do simulador: {mudou} tela(s) reescrita(s)')


if __name__ == '__main__':
    sys.exit(main())
