# Urna do Grêmio Estudantil — Versão simples

Projeto da E.E. Prof. Armando Gomes de Araújo.

**Sem Python, sem arquivos BAT, sem banco de dados e sem cadastro de alunos.** Só HTML, CSS e JavaScript. As chapas continuam cadastradas: **13 — Menos Bullying mais Inclusão** e **33 — Ao Infinito e Além**.

## Como abrir

1. Atualize o repositório no GitHub Desktop (Pull origin).
2. Abra a pasta no VS Code e use **Go Live** (Live Server) para abrir `index.html`.
3. A urna já inicia mostrando **Digite o número da chapa**.
4. Digite 13 ou 33, confira a foto e o logo, e pressione **CONFIRMA**. Também há BRANCO, CORRIGE e voto NULO para número não cadastrado.
5. Após **registrar no navegador**, toca o som final, aparece **FIM** e a urna volta sozinha à digitação.

## Como consultar, baixar e zerar os votos

Abra **`relatorio.html` pelo MESMO Live Server, no MESMO navegador/perfil e porta da urna.** Por exemplo, se a urna abrir em `http://127.0.0.1:5500/index.html`, o relatório estará em `http://127.0.0.1:5500/relatorio.html`.

No relatório você verá os votos **em sequência** (1º voto, 2º voto etc.), as chapas 13/33, brancos e nulos, e os totais. Nele existem três botões:

- **Baixar relatório CSV para abrir no VS Code:** gera `relatorio_votos_gremio.csv` em Downloads. Você pode abri-lo no VS Code ou colocá-lo na pasta do projeto.
- **Atualizar relatório:** relê os dados da urna.
- **Zerar contagem:** requer confirmação e a palavra `ZERAR`. Apaga os registros desse navegador e faz a sequência recomeçar do 1º voto. Faça uma cópia do CSV ANTES de zerar.

**Limitação do navegador:** um site estático NÃO consegue alterar automaticamente arquivos do repositório que aparecem no VS Code. Portanto, os dados são salvos automaticamente no **localStorage do navegador**, mas o CSV só é criado no computador quando você clica para baixar. Não é uma planilha atualizada automaticamente no disco. Os dados NÃO vão ao GitHub.

**Use sempre o mesmo endereço e perfil do navegador:** `127.0.0.1:5500`, `localhost:5500`, outro número de porta e GitHub Pages podem guardar dados em lugares separados. Limpar dados do navegador, usar modo anônimo ou mudar de computador pode apagar ou ocultar os registros. Faça exportações periódicas.

## Sobre votos anteriores

Se você chegou a utilizar o sistema antigo com Python, os dados anteriores continuam na pasta privada que ele criou, fora do repositório. A nova versão **não importa automaticamente** esses registros. Não apague essa pasta sem conferir a existência dos dados.

## Aviso importante para a eleição

O histórico por ordem associado à folha de assinaturas permite identificar a escolha de cada aluno: **a votação não é secreta nesse formato**. Informe isso aos estudantes e à comissão, e limite o acesso ao relatório. Para uma votação sigilosa e com maior segurança contra perda/alteração de dados, é necessário um sistema de apuração diferente.

Esta versão é adequada para **ensaio e uso simples, com as limitações assumidas pela escola**. Não é auditada: armazenamento no navegador pode ser apagado ou alterado. Antes da votação, realize testes, faça backup dos arquivos CSV e confira os totais.
