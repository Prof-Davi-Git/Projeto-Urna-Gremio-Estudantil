#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Servidor local da urna escolar: Python puro, sem MySQL e sem cadastro de alunos.

Os votos são guardados APENAS como totais. Não existe registro de "voto 1 -> chapa X".
A lista de assinaturas deve permanecer em papel, separada do arquivo de apuração.
Execute com: py -3 servidor_urna.py (Windows) ou python3 servidor_urna.py.
"""
import argparse
import csv
import io
import json
import os
import secrets
import sys
import tempfile
import threading
import uuid
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

PASTA_PROJETO = Path(__file__).resolve().parent
# Fora da pasta pública e fora do GitHub: nem Pages nem o servidor servem esses dados.
PASTA_PRIVADA = PASTA_PROJETO.parent / "Urna_Gremio_Dados_Privados"
ARQUIVO_VOTOS = PASTA_PRIVADA / "apuracao_privada.json"
ARQUIVO_RELATORIO = PASTA_PRIVADA / "relatorio_apuracao.csv"
CHAPAS = {"13": "Menos Bullying mais Inclusão", "33": "Ao Infinito e Além"}
CATEGORIAS = {"13", "33", "BRANCO", "NULO"}
TRAVA = threading.RLock()


def dados_iniciais():
    return {
        "versao": 1, "total": 0,
        "chapas": {"13": 0, "33": 0},
        "brancos": 0, "nulos": 0,
        # IDs aleatórios, sem nomes e sem indicação da chapa, somente para evitar
        # que uma retransmissão da mesma requisição conte duas vezes.
        "confirmacoes_processadas": []
    }


def ler_dados():
    if not ARQUIVO_VOTOS.exists():
        return dados_iniciais()
    with ARQUIVO_VOTOS.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, dict) or dados.get("versao") != 1:
        raise ValueError("Arquivo de apuração inválido. Sistema interrompido por segurança.")
    if set(dados.get("chapas", {})) != set(CHAPAS):
        raise ValueError("Chapas inconsistentes no arquivo de apuração.")
    valores = [dados.get("total"), dados.get("brancos"), dados.get("nulos")]
    valores += list(dados["chapas"].values())
    if any(type(v) is not int or v < 0 for v in valores):
        raise ValueError("Apuração com contadores inválidos.")
    if dados["total"] != (sum(dados["chapas"].values()) + dados["brancos"] + dados["nulos"]):
        raise ValueError("Apuração inconsistente. Não foi realizado novo registro.")
    ids = dados.get("confirmacoes_processadas")
    if not isinstance(ids, list) or len(ids) != dados["total"] or len(set(ids)) != len(ids):
        raise ValueError("Histórico de confirmações inconsistente.")
    return dados


def gravar_atomicamente(dados):
    """Não deixar JSON parcialmente gravado em queda de energia ou do aplicativo."""
    PASTA_PRIVADA.mkdir(parents=True, exist_ok=True)
    arquivo_tmp = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=PASTA_PRIVADA,
            prefix=".gravacao-", suffix=".tmp", delete=False
        ) as arquivo:
            arquivo_tmp = Path(arquivo.name)
            json.dump(dados, arquivo, ensure_ascii=False, indent=2, sort_keys=True)
            arquivo.write("\n")
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(arquivo_tmp, ARQUIVO_VOTOS)
    finally:
        if arquivo_tmp and arquivo_tmp.exists():
            arquivo_tmp.unlink()


def criar_relatorio():
    with TRAVA:
        dados = ler_dados()
        PASTA_PRIVADA.mkdir(parents=True, exist_ok=True)
        with ARQUIVO_RELATORIO.open("w", encoding="utf-8-sig", newline="") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(["APURAÇÃO - GRÊMIO ESTUDANTIL", "Quantidade"])
            for numero, nome in CHAPAS.items():
                escritor.writerow([f"Chapa {numero} - {nome}", dados["chapas"][numero]])
            escritor.writerow(["Votos brancos", dados["brancos"]])
            escritor.writerow(["Votos nulos", dados["nulos"]])
            escritor.writerow(["TOTAL DE VOTOS", dados["total"]])
            escritor.writerow(["TOTAL DE ASSINATURAS EM PAPEL (preencher)", ""])
            escritor.writerow(["DIFERENÇA (conferir manualmente)", ""])
        return dados


class EstadoUrna:
    def __init__(self):
        self.pin_mesario = f"{secrets.randbelow(1000000):06d}"
        self.liberada = False


class ServidorUrna(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, endereco, classe):
        super().__init__(endereco, classe)
        self.estado = EstadoUrna()


class Rotas(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PASTA_PROJETO), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        super().end_headers()

    def responder(self, codigo, dados):
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        caminho = urlsplit(self.path).path
        if caminho == "/api/status":
            with TRAVA:
                self.responder(200, {
                    "servidor_local": True, "liberada": self.server.estado.liberada
                })
            return
        if caminho.startswith("/api/"):
            self.responder(404, {"erro": "Rota não encontrada"})
            return
        # Não servir arquivo Python, pastas ocultas ou dados, mesmo localmente.
        partes = Path(caminho).parts
        if (any(p.startswith(".") for p in partes if p not in ("/", ""))
                or caminho.endswith((".py", ".bat", ".json", ".csv", ".txt"))
                or "Urna_Gremio_Dados_Privados" in partes):
            self.send_error(403)
            return
        return super().do_GET()

    def do_POST(self):
        caminho = urlsplit(self.path).path
        if caminho not in ("/api/liberar", "/api/voto"):
            self.responder(404, {"erro": "Rota não encontrada"})
            return
        origem = self.headers.get("Origin", "")
        destino = self.headers.get("Host", "")
        if origem and origem != f"http://{destino}":
            self.responder(403, {"erro": "Origem não autorizada"})
            return
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
            self.responder(415, {"erro": "Use JSON"})
            return
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            if tamanho <= 0 or tamanho > 4096:
                raise ValueError("Tamanho inválido")
            dados = json.loads(self.rfile.read(tamanho))
            if not isinstance(dados, dict):
                raise ValueError("Formato inválido")
        except (ValueError, TypeError, json.JSONDecodeError):
            self.responder(400, {"erro": "Requisição inválida"})
            return

        with TRAVA:
            if caminho == "/api/liberar":
                pin = str(dados.get("pin", ""))
                if not secrets.compare_digest(pin, self.server.estado.pin_mesario):
                    self.responder(403, {"erro": "Senha do mesário incorreta"})
                    return
                if self.server.estado.liberada:
                    self.responder(409, {"erro": "Já existe uma votação liberada"})
                    return
                self.server.estado.liberada = True
                self.responder(200, {"ok": True, "liberada": True})
                return

            escolha = dados.get("escolha")
            identificador = dados.get("identificador")
            if escolha not in CATEGORIAS:
                self.responder(400, {"erro": "Escolha inválida"})
                return
            try:
                if not isinstance(identificador, str):
                    raise ValueError("Identificador inválido")
                uuid.UUID(identificador)
                if len(identificador) != 36:
                    raise ValueError("Identificador inválido")
            except (ValueError, TypeError, AttributeError):
                self.responder(400, {"erro": "Identificador inválido"})
                return

            try:
                apuracao = ler_dados()
                # Requisição repetida após perda de conexão: nunca contar duas vezes.
                if identificador in apuracao["confirmacoes_processadas"]:
                    self.responder(200, {"ok": True})
                    return
                if not self.server.estado.liberada:
                    self.responder(409, {"erro": "Aguarde a liberação do mesário"})
                    return
                proximo = dict(apuracao)
                proximo["chapas"] = dict(apuracao["chapas"])
                proximo["confirmacoes_processadas"] = sorted(
                    apuracao["confirmacoes_processadas"] + [identificador]
                )
                proximo["total"] += 1
                if escolha in CHAPAS:
                    proximo["chapas"][escolha] += 1
                elif escolha == "BRANCO":
                    proximo["brancos"] += 1
                else:
                    proximo["nulos"] += 1
                gravar_atomicamente(proximo)
                self.server.estado.liberada = False
            except (OSError, ValueError) as erro:
                print("ERRO AO GRAVAR VOTO:", erro, file=sys.stderr)
                self.responder(500, {
                    "erro": "Não foi possível salvar. Chame o mesário e não reinicie a urna."
                })
                return
            self.responder(200, {"ok": True})


def iniciar(porta):
    # Não sobrescrever arquivo com estrutura inesperada ou danificada.
    with TRAVA:
        ler_dados()
    servidor = ServidorUrna(("127.0.0.1", porta), Rotas)
    endereco = f"http://127.0.0.1:{porta}"
    print("\n" + "=" * 60)
    print("URNA DO GRÊMIO - SERVIDOR LOCAL")
    print("Não fecha esta janela enquanto estiver votando.")
    print("Urna:", endereco)
    print("Mesário:", endereco + "/mesario.html")
    print("PIN DO MESÁRIO:", servidor.estado.pin_mesario)
    print("Dados PRIVADOS:", PASTA_PRIVADA)
    print("Atenção: assine a lista em papel ANTES de liberar cada voto.")
    print("=" * 60 + "\n")
    webbrowser.open(endereco + "/mesario.html")
    webbrowser.open_new_tab(endereco + "/")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado. Dados permanecem salvos.")
    finally:
        servidor.server_close()


def main():
    parser = argparse.ArgumentParser(description="Urna local do Grêmio Estudantil")
    parser.add_argument("--porta", type=int, default=8765, help="Padrão: 8765")
    parser.add_argument("--relatorio", action="store_true", help="Gerar relatório após encerrar a votação")
    args = parser.parse_args()
    if args.relatorio:
        dados = criar_relatorio()
        print("Relatório gerado:", ARQUIVO_RELATORIO)
        print("Total de votos:", dados["total"])
    else:
        iniciar(args.porta)


if __name__ == "__main__":
    main()
