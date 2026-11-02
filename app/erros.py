"""Erros de regra de negócio, traduzidos em respostas HTTP pela aplicação."""


class ErroDeNegocio(Exception):
    status_code = 400

    def __init__(self, mensagem: str):
        super().__init__(mensagem)
        self.mensagem = mensagem


class NaoEncontrado(ErroDeNegocio):
    status_code = 404


class Conflito(ErroDeNegocio):
    status_code = 409


class RegraViolada(ErroDeNegocio):
    status_code = 422


class NaoAutorizado(ErroDeNegocio):
    status_code = 401


class Proibido(ErroDeNegocio):
    status_code = 403
