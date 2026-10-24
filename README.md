# Urna do Grêmio Estudantil

Projeto da E.E. Prof. Armando Gomes de Araújo.

## Estrutura

- `index.html`: estrutura HTML.
- `style.css`: a urna preenche a tela de forma proporcional e mantém a disposição visual da arte.
- `script.js`: regiões transparentes clicáveis alinhadas ao teclado da imagem; simulação do voto.
- `urna.png`: imagem original da urna aprovada, **arquivo binário ainda pendente de envio**.

**Nota:** a publicação do site exige que `urna.png` esteja na raiz, pois os arquivos de interface não reproduzem a arte por código. Não substituir por recriação aproximada.

## Simulação

Pressione CONFIRMA para iniciar, digite dois números, confira, use CORRIGE para alterar e CONFIRMA para concluir. Também há suporte a teclado físico e comando de tela cheia.

**Não usar em eleições reais:** a interface não tem autenticação de eleitor, gravação dos votos, sigilo verificável nem apuração. Esses componentes exigem backend e testes com a comissão eleitoral.