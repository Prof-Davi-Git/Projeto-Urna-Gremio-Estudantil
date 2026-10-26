"""Testes locais; usam diretório temporário e não alteram votos reais."""
import json
import tempfile
import threading
import unittest
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import servidor_urna as urna


class TesteUrna(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = (urna.PASTA_PRIVADA, urna.ARQUIVO_VOTOS, urna.ARQUIVO_RELATORIO)
        urna.PASTA_PRIVADA = Path(self.tmp.name)
        urna.ARQUIVO_VOTOS = urna.PASTA_PRIVADA / "apuracao.json"
        urna.ARQUIVO_RELATORIO = urna.PASTA_PRIVADA / "relatorio.csv"
        self.server = urna.ServidorUrna(("127.0.0.1", 0), urna.Rotas)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = "http://127.0.0.1:" + str(self.server.server_address[1])

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        (urna.PASTA_PRIVADA, urna.ARQUIVO_VOTOS, urna.ARQUIVO_RELATORIO) = self.old
        self.tmp.cleanup()

    def post(self, caminho, dados):
        corpo = json.dumps(dados).encode("utf-8")
        requisicao = Request(self.url + caminho, body=corpo,
                             headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(requisicao, timeout=3) as resposta:
                return resposta.status, json.load(resposta)
        except HTTPError as erro:
            return erro.code, json.load(erro)

    def test_gravacao_bloqueio_e_relatorio_sem_nome(self):
        with urlopen(self.url + "/api/status", timeout=3) as resposta:
            self.assertFalse(json.load(resposta)["liberada"])
        numero = str(uuid.uuid4())
        self.assertEqual(409, self.post("/api/voto", {"escolha": "13", "identificador": numero})[0])
        self.assertEqual(403, self.post("/api/liberar", {"pin": "0000000"})[0])
        self.assertEqual(200, self.post("/api/liberar", {"pin": self.server.estado.pin_mesario})[0])
        self.assertEqual(200, self.post("/api/voto", {"escolha": "13", "identificador": numero})[0])
        self.assertEqual(200, self.post("/api/voto", {"escolha": "13", "identificador": numero})[0])
        self.assertEqual(409, self.post("/api/voto", {"escolha": "33", "identificador": str(uuid.uuid4())})[0])
        self.assertEqual(200, self.post("/api/liberar", {"pin": self.server.estado.pin_mesario})[0])
        self.assertEqual(200, self.post("/api/voto", {"escolha": "BRANCO", "identificador": str(uuid.uuid4())})[0])
        apuracao = urna.ler_dados()
        self.assertEqual(2, apuracao["total"])
        self.assertEqual(1, apuracao["chapas"]["13"])
        self.assertEqual(0, apuracao["chapas"]["33"])
        self.assertEqual(1, apuracao["brancos"])
        self.assertEqual(0, apuracao["nulos"])
        self.assertEqual(2, len(apuracao["confirmacoes_processadas"]))
        self.assertNotIn("aluno", str(apuracao).lower())
        urna.criar_relatorio()
        self.assertTrue(urna.ARQUIVO_RELATORIO.exists())

    def test_voto_invalido_nao_aceito(self):
        self.assertEqual(200, self.post("/api/liberar", {"pin": self.server.estado.pin_mesario})[0])
        self.assertEqual(400, self.post("/api/voto", {"escolha": ["13"], "identificador": str(uuid.uuid4())})[0])
        self.assertEqual(400, self.post("/api/voto", {"escolha": "13", "identificador": "123"})[0])
        self.assertEqual(0, urna.ler_dados()["total"])
        with self.assertRaises(HTTPError) as ctx:
            urlopen(self.url + "/servidor_urna.py", timeout=3)
        self.assertEqual(403, ctx.exception.code)

    def test_recuperacao_contra_arquivo_corrompido(self):
        urna.ARQUIVO_VOTOS.write_text('{"versao":1,"total":99}', encoding="utf-8")
        with self.assertRaises(ValueError):
            urna.ler_dados()


if __name__ == "__main__":
    unittest.main()
