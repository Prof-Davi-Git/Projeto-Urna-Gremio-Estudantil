# Urna do Grêmio Estudantil

Interface visual da E.E. Prof. Armando Gomes de Araújo.

## Primeira versão — painel frontal em tela inteira

A tela do computador **é o painel da urna**. A arte `urna.webp` aparece recortada para remover o topo, a base e as laterais da caixa física. O painel do visor, os botões numéricos, BRANCO, CORRIGE, CONFIRMA e os logotipos permanecem no visual original, com os botões clicáveis no navegador.

O projeto foi organizado em:
- `index.html`: estrutura da interface;
- `style.css`: enquadramento do painel frontal para ocupar 100% da janela;
- `script.js`: teclas clicáveis, teclado físico e navegação;
- `urna.webp`: imagem-base aprovada pelo professor.

**Como abrir:** `index.html` no navegador ou GitHub Pages (branch `main`, pasta raiz). O botão discreto ⛶ no canto superior esquerdo ativa tela cheia quando o navegador permitir. Também é possível usar F11 no computador.

## Segurança e uso real

**O site ainda não grava votos**. Esta fase valida somente o visual e a interação com a urna. Antes de utilizá-la para uma eleição verdadeira, será necessário implementar cadastro das chapas, autorização individual dos eleitores, prevenção de múltiplos votos, sigilo do voto, armazenamento seguro no servidor, auditoria, apuração e testes. GitHub Pages sozinho não garante essas funções.

A mensagem fixa de "modo demonstração" foi retirada do visual conforme solicitado. A ausência desse aviso **não significa que a urna esteja pronta para receber votos reais**.
