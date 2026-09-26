/*
 * dc.js — renderizador dos componentes .dc.html do simulador da landing.
 * Lê o <x-dc> de cada arquivo (holes {{caminho}}, <sc-for>, <sc-if>, <dc-import>),
 * injeta o <helmet> no <head> uma vez por arquivo e monta tudo com Preact.
 */
(function () {
  'use strict';
  var P = window.preact;
  var h = P.h, Fragment = P.Fragment;

  var HOLE_INTEIRO = /^\s*\{\{\s*([^{}]+?)\s*\}\}\s*$/;
  var HOLE = /\{\{\s*([^{}]+?)\s*\}\}/g;

  function valorLiteral(p) {
    if (p === 'true') return { ok: true, v: true };
    if (p === 'false') return { ok: true, v: false };
    if (p === 'null') return { ok: true, v: null };
    if (/^-?\d+(\.\d+)?$/.test(p)) return { ok: true, v: Number(p) };
    if (/^'[^']*'$|^"[^"]*"$/.test(p)) return { ok: true, v: p.slice(1, -1) };
    return { ok: false };
  }

  function busca(caminho, escopo) {
    var lit = valorLiteral(caminho);
    if (lit.ok) return lit.v;
    var partes = caminho.split('.');
    var v = escopo[partes[0]];
    for (var i = 1; i < partes.length; i++) {
      if (v === null || v === undefined) return undefined;
      v = v[partes[i]];
    }
    return v;
  }

  function interpola(txt, escopo) {
    return txt.replace(HOLE, function (_, p) {
      var v = busca(p, escopo);
      return v === null || v === undefined ? '' : String(v);
    });
  }

  function valorDeAtributo(txt, escopo) {
    var m = HOLE_INTEIRO.exec(txt);
    if (m) return busca(m[1], escopo);
    if (txt.indexOf('{{') >= 0) return interpola(txt, escopo);
    return txt;
  }

  function camel(nome) {
    return nome.replace(/-([a-z])/g, function (_, c) { return c.toUpperCase(); });
  }

  // ---- compilação do markup em descritores ----
  function compila(no) {
    if (no.nodeType === 3) {
      var t = no.nodeValue;
      if (!t) return null;
      if (!/\S/.test(t) && t.indexOf('\n') >= 0) return null;
      return { k: 't', t: t, din: t.indexOf('{{') >= 0 };
    }
    if (no.nodeType !== 1) return null;
    var tag = no.localName;
    if (tag === 'helmet' || tag === 'script') return null;
    var attrs = [];
    for (var i = 0; i < no.attributes.length; i++) {
      var a = no.attributes[i];
      attrs.push([a.name, a.value]);
    }
    var filhos = [];
    var fonte = tag === 'template' ? no.content.childNodes : no.childNodes;
    for (var j = 0; j < fonte.length; j++) {
      var c = compila(fonte[j]);
      if (c) filhos.push(c);
    }
    return { k: 'e', tag: tag, attrs: attrs, filhos: filhos };
  }

  function attr(desc, nome) {
    for (var i = 0; i < desc.attrs.length; i++) if (desc.attrs[i][0] === nome) return desc.attrs[i][1];
    return null;
  }

  function renderFilhos(lista, escopo) {
    var out = [];
    for (var i = 0; i < lista.length; i++) {
      var r = renderNo(lista[i], escopo);
      if (r === null || r === undefined) continue;
      if (Array.isArray(r)) { for (var j = 0; j < r.length; j++) out.push(r[j]); }
      else out.push(r);
    }
    return out;
  }

  function renderNo(d, escopo) {
    if (d.k === 't') return d.din ? interpola(d.t, escopo) : d.t;
    var tag = d.tag;
    if (tag === 'sc-if') {
      var cond = valorDeAtributo(attr(d, 'value') || '', escopo);
      return cond ? renderFilhos(d.filhos, escopo) : null;
    }
    if (tag === 'sc-for') {
      var lista = valorDeAtributo(attr(d, 'list') || '', escopo) || [];
      var nome = attr(d, 'as') || 'item';
      var out = [];
      for (var i = 0; i < lista.length; i++) {
        var esc = Object.create(escopo);
        esc[nome] = lista[i];
        esc.$index = i;
        var fs = renderFilhos(d.filhos, esc);
        for (var j = 0; j < fs.length; j++) out.push(fs[j]);
      }
      return out;
    }
    if (tag === 'dc-import') {
      var props = {};
      var arquivo = null, dica = null;
      for (var k = 0; k < d.attrs.length; k++) {
        var n = d.attrs[k][0], v = d.attrs[k][1];
        if (n === 'name') arquivo = v;
        else if (n === 'hint-size') dica = v;
        else if (n.indexOf('hint-') === 0) continue;
        else props[camel(n)] = valorDeAtributo(v, escopo);
      }
      return h(Importado, { key: arquivo, arquivo: arquivo, dica: dica, props: props });
    }
    var p = {};
    for (var a = 0; a < d.attrs.length; a++) {
      var an = d.attrs[a][0], av = valorDeAtributo(d.attrs[a][1], escopo);
      if (an.indexOf('hint-') === 0) continue;
      if (an.length > 2 && an[0] === 'o' && an[1] === 'n') {
        if (typeof av === 'function') p[an] = av;
        continue;
      }
      if (av === undefined || av === null || av === false) continue;
      p[an] = av;
    }
    return h(tag, p, renderFilhos(d.filhos, escopo));
  }

  // ---- DCLogic ----
  function DCLogic(props) { P.Component.call(this, props); }
  DCLogic.prototype = Object.create(P.Component.prototype);
  DCLogic.prototype.constructor = DCLogic;
  DCLogic.prototype.render = function () {
    var vals = this.renderVals ? this.renderVals() : {};
    return h(Fragment, null, renderFilhos(this.__arvore, vals || {}));
  };

  // ---- carregamento de arquivos ----
  var cache = {};
  var headInjetado = {};

  function injetaHelmet(helmet) {
    if (!helmet) return;
    var nos = helmet.childNodes;
    for (var i = 0; i < nos.length; i++) {
      var no = nos[i];
      if (no.nodeType !== 1) continue;
      var chave = no.localName === 'link' ? 'link:' + no.getAttribute('href') : 'style:' + no.textContent.length + ':' + no.textContent.slice(0, 80);
      if (headInjetado[chave]) continue;
      headInjetado[chave] = true;
      var el = document.createElement(no.localName);
      for (var j = 0; j < no.attributes.length; j++) el.setAttribute(no.attributes[j].name, no.attributes[j].value);
      if (no.localName === 'style') el.textContent = no.textContent;
      document.head.appendChild(el);
    }
  }

  function carrega(nome) {
    if (cache[nome]) return cache[nome];
    cache[nome] = fetch((window.DC_BASE || '') + nome + '.dc.html').then(function (r) {
      if (!r.ok) throw new Error('dc: não achei ' + nome);
      return r.text();
    }).then(function (texto) {
      var doc = new DOMParser().parseFromString(texto, 'text/html');
      var xdc = doc.querySelector('x-dc');
      injetaHelmet(xdc.querySelector('helmet'));
      var arvore = [];
      for (var i = 0; i < xdc.childNodes.length; i++) {
        var c = compila(xdc.childNodes[i]);
        if (c) arvore.push(c);
      }
      var script = doc.querySelector('script[data-dc-script]');
      var Classe = new Function('DCLogic', script.textContent + '\n;return Component;')(DCLogic);
      Classe.prototype.__arvore = arvore;
      return Classe;
    });
    return cache[nome];
  }

  function Importado(props) { P.Component.call(this, props); this.state = { C: null }; }
  Importado.prototype = Object.create(P.Component.prototype);
  Importado.prototype.constructor = Importado;
  Importado.prototype.componentDidMount = function () {
    var self = this;
    carrega(this.props.arquivo).then(function (C) { self.setState({ C: C }); })['catch'](function (e) { console.error(e); });
  };
  Importado.prototype.shouldComponentUpdate = function (np, ns) {
    if (ns.C !== this.state.C || np.arquivo !== this.props.arquivo) return true;
    var a = this.props.props || {}, b = np.props || {};
    var ka = Object.keys(a), kb = Object.keys(b);
    if (ka.length !== kb.length) return true;
    for (var i = 0; i < kb.length; i++) if (a[kb[i]] !== b[kb[i]]) return true;
    return false;
  };
  Importado.prototype.render = function () {
    var C = this.state.C;
    if (!C) {
      var tam = (this.props.dica || '').split(',');
      return h('div', { style: tam.length === 2 ? 'width:' + tam[0] + ';height:' + tam[1] : '' });
    }
    return h(C, this.props.props);
  };

  window.DC = {
    montar: function (nome, alvo, props) {
      carrega(nome).then(function (C) { P.render(h(C, props || {}), alvo); });
    },
    preCarregar: function (nomes) { nomes.forEach(carrega); }
  };
})();
