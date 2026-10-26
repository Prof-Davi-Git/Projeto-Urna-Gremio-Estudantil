# Urna do Grêmio Estudantil — E.E. Prof. Armando Gomes de Araújo

Urna das chapas **13 — Menos Bullying mais Inclusão** e **33 — Ao Infinito e Além**.

## Como usar no único computador da eleição

**Requer Python 3. Não precisa instalar MySQL nem cadastrar alunos.**

1. Na pasta do projeto, abra **Iniciar_Urna.bat** com dois cliques. Não feche a janela preta durante a votação.
2. O programa abre o **Controle do Mesário** e a **Urna**. A janela preta mostrará um PIN de seis dígitos, exclusivo do mesário.
3. Antes de cada votação, o aluno assina na lista em papel. Use o link de impressão na tela do mesário.
4. O mesário confere a assinatura e usa o PIN para clicar **LIBERAR UM VOTO**.
5. O eleitor digita 13 ou 33, escolhe BRANCO, ou digita número não cadastrado para nulo. CONFIRMA registra a escolha.
6. Só depois de o registro ter sido gravado o som final toca e aparece **FIM**. A urna volta a ficar bloqueada e aguarda o próximo eleitor.
7. Se aparecer **VOTO NÃO CONFIRMADO**, não reinicie a página: chame o mesário e aperte CONFIRMA novamente. A mesma requisição não será contada duas vezes.

**Importante:** não utilize o Live Server do VS Code nem o GitHub Pages para uma votação real. Eles não conseguem gravar votos. Use o endereço http://127.0.0.1:8765 aberto pelo programa acima. O servidor só aceita conexões do próprio computador.

## Armazenamento sem banco de dados

O sistema cria automaticamente uma pasta privada CHAMADA Urna_Gremio_Dados_Privados **ao lado da pasta do repositório**, nunca dentro do GitHub. Nela fica o arquivo apuracao_privada.json.

O arquivo contém apenas **totais por chapa (13 e 33), brancos, nulos, total geral**, e identificadores aleatórios de confirmação. Esses IDs não registram escolha, nome, matrícula, turma ou ordem de chegada.

**A lista de assinaturas é separada do voto.** Não será criado relatório do tipo '1º aluno assinou → votou 13'. Isso quebraria o sigilo eleitoral.

## Como gerar o relatório depois da eleição

1. Encerre a votação; na janela do servidor, use Ctrl+C.
2. Dê dois cliques em **Gerar_Relatorio.bat**.
3. Abra o arquivo relatorio_apuracao.csv na pasta Urna_Gremio_Dados_Privados (ao lado do repositório).
4. Compare o **TOTAL DE VOTOS** com a quantidade de assinaturas em papel. Registre qualquer diferença.

**Não apague a pasta de dados.** Os votos não são enviados ao GitHub nem à nuvem. Faça uma cópia de segurança protegida após encerrar a eleição.

## Arquivos do sistema

- servidor_urna.py — serviço Python local e gravação atômica da apuração.
- Iniciar_Urna.bat — inicializador Windows com dois cliques.
- mesario.html e mesario.js — liberação por PIN de um voto por vez.
- lista_assinaturas.html — folhas numeradas prontas para impressão.
- Gerar_Relatorio.bat — CSV de apuração para conferência.
- script.js, index.html, style.css e assets — interface da urna e imagens/áudios.

## Teste antes da votação

Dê dois cliques em **Testar_Urna.bat**. Os testes simulam liberações e gravações em arquivos temporários, sem alterar a apuração verdadeira. O resultado esperado é **OK**. Esse teste automático não substitui um ensaio com mesário, duas ou mais pessoas e a impressora.

## Avisos para a comissão eleitoral

Esta é uma primeira implementação local, **não uma urna eleitoral certificada ou auditada**. A lista em papel e o mesário ajudam a controlar quem vota, mas não identificam automaticamente alunos repetidos: a comissão precisa fazer essa conferência no papel.

Um administrador com acesso aos arquivos enquanto a votação acontece poderia comparar totais sucessivos e inferir votos individuais. Restrinja o acesso aos arquivos privados e só faça a apuração depois de encerrar.

Antes da eleição real, teste votos válidos, branco, nulo, CORRIGE, som final, bloqueio entre eleitores, queda de energia e perda de conexão. Planeje como separar votos de teste dos votos oficiais com a comissão.