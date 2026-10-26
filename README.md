# Urna do Grêmio Estudantil — Como usar (um computador)

**Funcionamento simples:** a urna fica liberada o tempo todo. Não há PIN, cadastro de alunos, tela de mesário ou MySQL.

## Para testar agora, sem misturar com os votos oficiais

1. Deixe a pasta do GitHub atualizada no computador (GitHub Desktop → Pull origin).
2. Feche qualquer janela antiga chamada *Urna Grêmio - MODO TESTE* (Ctrl+C na janela preta).
3. Abra **Iniciar_Teste.bat** com dois cliques. O navegador abre a urna automaticamente.
4. Digite **13** ou **33**, confira a chapa e aperte **CONFIRMA**. Também existem BRANCO, CORRIGE e voto NULO.
5. Depois do som e da mensagem **FIM**, a urna volta **sozinha** à digitação para o próximo voto.
6. A janela preta deve ficar aberta durante a votação. Os votos de teste ficam em outra pasta.

## Eleição oficial

Quando estiver tudo testado, feche a janela preta de teste e execute **Iniciar_Urna.bat**.
O aluno assina a lista em papel, vota na urna já liberada e sai. A conferência de quem já votou é **manual, pela equipe e pela lista**; o programa não impede que o mesmo aluno volte a votar.

**A urna deve ser aberta pelo arquivo .bat no Windows, NÃO pelo Live Server ou GitHub Pages**. É necessário ter Python 3 instalado, como já foi usado no teste.

## Onde ficam os votos?

Os arquivos ficam em uma pasta privada, fora do GitHub, **ao lado da pasta do projeto**:

- Oficial: **Urna_Gremio_Dados_Privados**
- Testes: **Urna_Gremio_Dados_TESTE**

Em cada pasta, o sistema atualiza automaticamente um CSV sequencial. Na eleição oficial, chama-se **historico_votos.csv**. Ele registra por exemplo:

| Ordem | Número/Tipo | Escolha |
|---|---|---|
| 1º voto | 13 | Chapa 13 - Menos Bullying mais Inclusão |
| 2º voto | 33 | Chapa 33 - Ao Infinito e Além |
| 3º voto | BRANCO | Branco |

Para gerar a **contagem total por chapa**, depois de encerrar a votação execute **Gerar_Relatorio.bat**. Será criado `relatorio_apuracao.csv` na pasta oficial, que pode ser aberto no Excel.

**Não apague a pasta de dados nem a substitua durante a eleição.** O arquivo `votos_privados.json` é a fonte para reconstruir o histórico se necessário. Após a eleição, faça uma cópia de segurança dos arquivos privados e restrinja o acesso.

## Lista de assinaturas

Imprima a lista abrindo **http://127.0.0.1:8765/lista_assinaturas.html** quando estiver na urna oficial (ou porta **8766** durante o teste).

**ATENÇÃO AO SIGILO:** a ordem das assinaturas, quando cruzada com `historico_votos.csv`, **permite identificar a chapa de cada estudante**. Isso é especialmente sensível por se tratar de alunos. Explique o procedimento à comissão eleitoral, mantenha os registros separados e restritos, e informe os estudantes de que a votação não é secreta nesse formato. Para voto secreto, use apenas totais por chapa, sem o histórico de escolhas em ordem.

## Arquivos principais

- `Iniciar_Teste.bat` — inicia o modo de ensaio (porta 8766, arquivos separados).
- `Iniciar_Urna.bat` — inicia a votação oficial (porta 8765).
- `servidor_urna.py` — salva a sequência e gera os arquivos, sem banco externo.
- `Gerar_Relatorio.bat` — gera a soma final por chapa.
- `lista_assinaturas.html` — lista numerada imprimível.
- `test_servidor_urna.py` e `Testar_Urna.bat` — testes automáticos opcionais.

Se o programa mostrar **VOTO NÃO CONFIRMADO**, não feche a página. Aperte CONFIRMA novamente; o sistema usa um identificador único para não somar a mesma confirmação duas vezes.

**Não foi feita certificação ou auditoria independente:** a comissão precisa testar o sistema e definir como lidar com repetição de alunos, falhas de energia e eventuais divergências antes da eleição.
