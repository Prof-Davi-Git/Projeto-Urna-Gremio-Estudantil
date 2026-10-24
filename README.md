# Urna do Grêmio Estudantil

Interface inicial da urna da **E.E. Prof. Armando Gomes de Araújo**.

## Como abrir

Abra `index.html` no navegador ou publique a raiz do repositório pelo GitHub Pages (Settings → Pages → Deploy from a branch → main → /root).

## Interface criada

- Formato de urna: visor à esquerda e painel numérico à direita.
- Layout responsivo que ocupa a tela do navegador.
- Teclas clicáveis 0–9, **BRANCO**, **CORRIGE**, **CONFIRMA**.
- Digitação opcional pelo teclado físico, Enter para confirmar e Backspace para corrigir.
- Botão de tela cheia (o navegador pode exigir permissão).
- Fluxo **abertura → número de chapa (2 dígitos) → revisão → encerramento da simulação**.
- Símbolo escolar vetorial **provisório**, inspirado na imagem enviada; substituir pelo arquivo oficial aprovado da escola posteriormente.

## Importante — ainda não é uma urna de produção

**O protótipo não registra, transmite nem totaliza votos e não tem autenticação de eleitores.** A interface apresenta aviso permanente para evitar uso acidental como eleição oficial. O sistema foi feito dessa maneira intencionalmente, até definirmos os requisitos da votação real.

Para uma eleição verdadeira será necessário planejar, implementar e testar:
1. Cadastro oficial das chapas, com número, nome e identificação visual;
2. Lista de alunos aptos e liberação individual por mesário;
3. Proteção contra múltiplos votos com preservação do sigilo, **separando eleitor da escolha**;
4. Serviço/backend e banco de dados com acesso restrito (GitHub Pages sozinho não oferece isso);
5. Validação dos votos no servidor, apuração, auditoria e política de retenção de dados;
6. Plano para falhas de energia/internet, testes prévios com a comissão eleitoral e regras da escola.

Não usar o protótipo para coletar votos válidos antes de implementar e validar esses controles.
