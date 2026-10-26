#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Urna local simples: aberta para votar, sem PIN, sem cadastro, sem MySQL.

Registra a ordem e a escolha em um CSV privado. ATENÇÃO: cruzar esse
arquivo com assinaturas numeradas permite identificar o voto dos estudantes.
A escola deve informar essa característica e restringir o acesso ao arquivo.
"""
import argparse
import csv
import io
import json
import os
import sys
import tempfile
import threading
import uuid
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

PROJETO = Path(__file__).resolve().parent
DADOS = PROJETO.parent / "Urna_Gremio_Dados_Privados"
BANCO = DADOS / "votos_privados.json"
HISTORICO = DADOS / "historico_votos.csv"
RELATORIO = DADOS / "relatorio_apuracao.csv"
CHAPAS = {"13": "Menos Bullying mais Inclusão", "33": "Ao Infinito e Além"}
OPCOES = frozenset((*CHAPAS, "BRANCO", "NULO"))
TRAVA = threading.RLock()


def zerado():
    return {"versao": 2, "anteriores": {k: 0 for k in OPCOES},
            "ids_antigos": [], "votos": []}


def carregar():
    if not BANCO.exists():
        # Atualização transparente para quem já testou a versão anterior.
        antigo = DADOS / ("apuracao_teste.json" if DADOS.name.endswith("_TESTE")
                           else "apuracao_privada.json")
        if not antigo.exists():
            return zerado()
        with antigo.open(encoding="utf-8") as f:
            anterior = json.load(f)
        if anterior.get("versao") != 1:
            raise ValueError("Arquivo antigo desconhecido; não sobrescrever")
        totais = {**anterior["chapas"], "BRANCO": anterior["brancos"],
                  "NULO": anterior["nulos"]}
        if (set(totais) != OPCOES
                or any(type(v) is not int or v < 0 for v in totais.values())
                or sum(totais.values()) != anterior["total"]):
            raise ValueError("Apuração anterior inconsistente; não sobrescrever")
        ids = anterior.get("confirmacoes_processadas", [])
        if not isinstance(ids, list) or len(ids) != anterior["total"]:
            raise ValueError("Identificadores antigos inconsistentes")
        # Votos antigos não tinham ordem/seleção individual. Preservar totais,
        # sem inventar uma associação com a lista de assinaturas.
        return {"versao": 2, "anteriores": totais, "ids_antigos": ids, "votos": []}

    with BANCO.open(encoding="utf-8") as f:
        dados = json.load(f)
    if not isinstance(dados, dict) or dados.get("versao") != 2:
        raise ValueError("Formato da apuração inválido")
    if set(dados.get("anteriores", {})) != OPCOES:
        raise ValueError("Categorias incorretas")
    if any(type(v) is not int or v < 0 for v in dados["anteriores"].values()):
        raise ValueError("Totais incorretos")
    if not isinstance(dados.get("votos"), list):
        raise ValueError("Histórico incorreto")
    if not isinstance(dados.get("ids_antigos"), list):
        raise ValueError("Confirmações antigas incorretas")
    usados = set(dados["ids_antigos"])
    for voto in dados["votos"]:
        if (not isinstance(voto, dict) or voto.get("escolha") not in OPCOES
                or not isinstance(voto.get("id"), str) or voto["id"] in usados):
            raise ValueError("Registro inconsistente")
        usados.add(voto["id"])
    return dados


def salvar_texto_atomico(caminho, texto):
    DADOS.mkdir(parents=True, exist_ok=True)
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", newline="", dir=DADOS,
                prefix=".urna-", suffix=".tmp", delete=False) as arquivo:
            temporario = Path(arquivo.name)
            arquivo.write(texto)
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(temporario, caminho)
    finally:
        if temporario is not None and temporario.exists():
            temporario.unlink()


def salvar(dados):
    salvar_texto_atomico(BANCO, json.dumps(dados, ensure_ascii=False, indent=2) + "\n")


def totais(dados):
    resultado = dict(dados["anteriores"])
    for voto in dados["votos"]:
        resultado[voto["escolha"]] += 1
    return resultado


def descricao(escolha):
    if escolha in CHAPAS:
        return f"Chapa {escolha} - {CHAPAS[escolha]}"
    return "Branco" if escolha == "BRANCO" else "Nulo"


def gerar_historico(dados):
    """CSV privado, atualizado após cada voto; nunca exposto no site."""
    conteudo = io.StringIO()
    escritor = csv.writer(conteudo, delimiter=";")
    escritor.writerow(["Ordem", "Número/Tipo", "Escolha"])
    offset = sum(dados["anteriores"].values())
    for indice, voto in enumerate(dados["votos"], start=offset + 1):
        escritor.writerow([f"{indice}º voto", voto["escolha"],
                           descricao(voto["escolha"])])
    if offset:
        escritor.writerow(["Votos da versão anterior (sem sequência)", offset,
                           "Foram preservados nos totais, sem associação individual"])
    salvar_texto_atomico(HISTORICO, conteudo.getvalue().lstrip("\ufeff"))


def gerar_relatorio():
    with TRAVA:
        dados = carregar()
        valores = totais(dados)
        linhas = io.StringIO()
        escritor = csv.writer(linhas, delimiter=";")
        escritor.writerow(["APURAÇÃO - GRÊMIO ESTUDANTIL", "Quantidade"])
        for numero, nome in CHAPAS.items():
            escritor.writerow([f"Chapa {numero} - {nome}", valores[numero]])
        escritor.writerow(["Brancos", valores["BRANCO"]])
        escritor.writerow(["Nulos", valores["NULO"]])
        escritor.writerow(["TOTAL", sum(valores.values())])
        escritor.writerow(["Assinaturas em papel (preencher)", ""])
        escritor.writerow(["Diferença (conferir)", ""])
        salvar_texto_atomico(RELATORIO, "\ufeff" + linhas.getvalue())
        gerar_historico(dados)
        return valores


class ServidorLocal(ThreadingHTTPServer):
    daemon_threads = True


class Rotas(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJETO), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def responder(self, codigo, objeto):
        corpo = json.dumps(objeto, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        caminho = urlsplit(self.path).path
        if caminho == "/api/status":
            self.responder(200, {"servidor_local": True, "liberada": True})
            return
        if caminho.startswith("/api/"):
            self.responder(404, {"erro": "Página não encontrada"})
            return
        partes = Path(caminho).parts
        if (any(p.startswith(".") for p in partes if p not in ("/", ""))
                or caminho.endswith((".py", ".bat", ".json", ".csv", ".txt"))
                or "Urna_Gremio_Dados_Privados" in partes
                or "Urna_Gremio_Dados_TESTE" in partes):
            self.send_error(403)
            return
        super().do_GET()

    def do_POST(self):
        if urlsplit(self.path).path != "/api/voto":
            self.responder(404, {"erro": "Página não encontrada"})
            return
        origem = self.headers.get("Origin", "")
        if origem and origem != f"http://{self.headers.get('Host', '')}":
            self.responder(403, {"erro": "Origem não autorizada"})
            return
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
            self.responder(415, {"erro": "Formato não aceito"})
            return
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            if not 0 < tamanho <= 4096:
                raise ValueError()
            entrada = json.loads(self.rfile.read(tamanho))
            if not isinstance(entrada, dict):
                raise ValueError()
            escolha, identificador = entrada.get("escolha"), entrada.get("identificador")
            if (not isinstance(escolha, str) or escolha not in OPCOES
                    or not isinstance(identificador, str)
                    or len(identificador) != 36):
                raise ValueError()
            uuid.UUID(identificador)
        except (ValueError, TypeError, AttributeError, json.JSONDecodeError):
            self.responder(400, {"erro": "Voto inválido"})
            return

        with TRAVA:
            try:
                dados = carregar()
                if identificador in dados["ids_antigos"] or any(
                        v["id"] == identificador for v in dados["votos"]):
                    # Pode ter sido registrado antes de o navegador receber a resposta.
                    gerar_historico(dados)
                    self.responder(200, {"ok": True})
                    return
                dados["votos"].append({"id": identificador, "escolha": escolha})
                salvar(dados)
                gerar_historico(dados)
            except (OSError, ValueError, KeyError) as erro:
                print("ERRO AO SALVAR VOTO:", erro, file=sys.stderr)
                self.responder(500, {
                    "erro": "Não foi possível confirmar o salvamento. Tente CONFIRMA novamente."
                })
                return
        self.responder(200, {"ok": True})


def iniciar(porta):
    with TRAVA:
        dados = carregar()
        gerar_historico(dados)
    servidor = ServidorLocal(("127.0.0.1", porta), Rotas)
    endereco = f"http://127.0.0.1:{porta}/"
    print("\n" + "=" * 55)
    print("URNA DO GRÊMIO - " + ("TESTE" if DADOS.name.endswith("_TESTE") else "ELEIÇÃO"))
    print("A urna está SEMPRE LIBERADA; não há PIN ou mesário eletrônico.")
    print("Endereço:", endereco)
    print("Os votos são gravados na pasta:", DADOS)
    print("Arquivo sequencial:", HISTORICO.name)
    print("Não feche esta janela enquanto estiver votando.")
    print("=" * 55 + "\n")
    webbrowser.open(endereco)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nUrna encerrada. Os votos já registrados continuam salvos.")
    finally:
        servidor.server_close()


def main():
    global DADOS, BANCO, HISTORICO, RELATORIO
    parser = argparse.ArgumentParser(description="Urna simples do Grêmio")
    parser.add_argument("--porta", type=int, default=8765)
    parser.add_argument("--teste", action="store_true",
                        help="Usa uma pasta separada da eleição oficial")
    parser.add_argument("--relatorio", action="store_true")
    args = parser.parse_args()
    if args.teste:
        DADOS = PROJETO.parent / "Urna_Gremio_Dados_TESTE"
        BANCO = DADOS / "votos_teste.json"
        HISTORICO = DADOS / "historico_votos_teste.csv"
        RELATORIO = DADOS / "relatorio_teste.csv"
    if args.relatorio:
        valores = gerar_relatorio()
        print("Arquivos gerados:", HISTORICO, "e", RELATORIO, sep="\n")
        print("Total:", sum(valores.values()))
    else:
        iniciar(args.porta)


if __name__ == "__main__":
    main()
