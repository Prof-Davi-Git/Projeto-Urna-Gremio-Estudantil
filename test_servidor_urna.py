"""Testes automáticos em arquivos temporários (não usam votos de alunos)."""
import csv
import io
import json
import tempfile
import threading
import unittest
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import servidor_urna as urna


class TesteUrnaSimples(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.antigos = (urna.DADOS, urna.BANCO, urna.HISTORICO, urna.RELATORIO)
        urna.DADOS = Path(self.temp.name)
        urna.BANCO = urna.DADOS / "votos.json"
        urna.HISTORICO = urna.DADOS / "historico.csv"
        urna.RELATORIO = urna.DADOS / "relatorio.csv"
        self.servidor = urna.ServidorLocal(("127.0.0.1", 0), urna.Rotas)
        self.thread = threading.Thread(target=self.servidor.serve_forever, daemon=True)
        self.thread.start()
        self.url = "http://127.0.0.1:" + str(self.servidor.server_address[1])

    def tearDown(self):
        self.servidor.shutdown()
        self.servidor.server_close()
        self.thread.join(timeout=3)
        (urna.DADOS, urna.BANCO, urna.HISTORICO, urna.RELATORIO) = self.antigos
        self.temp.cleanup()

    def post(self, escolha, chave):
        corpo = json.dumps({"escolha": escolha, "identificador": chave}).encode()
        request = Request(self.url + "/api/voto", data=corpo, method="POST",
                          headers={"Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=3) as resp:
                return resp.status, json.load(resp)
        except HTTPError as error:
            return error.code, json.load(error)

    def test_sequencia_sem_mesario_e_repeticao(self):
        with urlopen(self.url + "/api/status", timeout=3) as response:
            self.assertTrue(json.load(response)["liberada"])
        escolhas = ["13", "33", "BRANCO", "NULO"]
        primeiro_id = str(uuid.uuid4())
        self.assertEqual(200, self.post("13", primeiro_id)[0])
        self.assertEqual(200, self.post("13", primeiro_id)[0])
        for escolha in escolhas[1:]:
            self.assertEqual(200, self.post(escolha, str(uuid.uuid4()))[0])
        dados = urna.carregar()
        self.assertEqual(escolhas, [v["escolha"] for v in dados["votos"]])
        self.assertEqual(4, len(dados["votos"]))
        self.assertTrue(urna.HISTORICO.exists())
        with urna.HISTORICO.open(encoding="utf-8-sig", newline="") as f:
            registros = list(csv.reader(f, delimiter=";"))
        self.assertEqual(["1º voto", "13"], registros[1][:2])
        self.assertEqual(["2º voto", "33"], registros[2][:2])
        self.assertEqual(["3º voto", "BRANCO"], registros[3][:2])
        self.assertEqual(["4º voto", "NULO"], registros[4][:2])
        self.assertEqual(200, self.post("13", str(uuid.uuid4()))[0])
        self.assertEqual(5, len(urna.carregar()["votos"]))
        valores = urna.gerar_relatorio()
        self.assertEqual({"13": 2, "33": 1, "BRANCO": 1, "NULO": 1}, valores)

    def test_bloqueia_dados_invalidos_e_arquivos_locais(self):
        self.assertEqual(400, self.post("14", str(uuid.uuid4()))[0])
        self.assertEqual(400, self.post("13", "invalido")[0])
        self.assertEqual(0, len(urna.carregar()["votos"]))
        with self.assertRaises(HTTPError) as ctx:
            urlopen(self.url + "/servidor_urna.py", timeout=3)
        self.assertEqual(403, ctx.exception.code)

    def test_totais_antigos_preservados(self):
        legado = {
            "versao": 1, "total": 2,
            "chapas": {"13": 1, "33": 1},
            "brancos": 0, "nulos": 0,
            "confirmacoes_processadas": [str(uuid.uuid4()), str(uuid.uuid4())]
        }
        (urna.DADOS / "apuracao_privada.json").write_text(
            json.dumps(legado), encoding="utf-8"
        )
        self.assertEqual(2, sum(urna.totais(urna.carregar()).values()))
        self.assertEqual(200, self.post("BRANCO", str(uuid.uuid4()))[0])
        with urna.HISTORICO.open(encoding="utf-8-sig", newline="") as f:
            registros = list(csv.reader(f, delimiter=";"))
        self.assertEqual("3º voto", registros[1][0])
        self.assertEqual(3, sum(urna.totais(urna.carregar()).values()))

    def test_arquivo_invalido_nao_e_zerado(self):
        urna.BANCO.write_text('{"versao":2,"anteriores": {}}', encoding="utf-8")
        with self.assertRaises(ValueError):
            urna.carregar()


if __name__ == "__main__":
    unittest.main()
