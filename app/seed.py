"""Dados de demonstração (idempotente). Tudo simulado — nenhum dado real de paciente."""
from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.acesso.servico import criar_funcionario
from app.estoque.servico import criar_medicamento
from app.models import ClasseControle, Funcionario, Perfil
from app.movimentacoes.servico import registrar_entrada, registrar_retirada

SENHA_DEMO = "demo12345"

FUNCIONARIOS = [
    ("Ana Administradora", "admin@hospital.demo", Perfil.ADMINISTRADOR),
    ("Fábio Farmacêutico", "farmaceutico@hospital.demo", Perfil.FARMACEUTICO),
    ("Elisa Enfermeira", "enfermeiro@hospital.demo", Perfil.ENFERMEIRO),
]

# (nome, apresentação, classe, estoque mínimo, [(lote, dias para vencer, quantidade)])
MEDICAMENTOS = [
    ("Dipirona", "500 mg comprimido", ClasseControle.COMUM, 100,
     [("DIP-2401", 20, 60), ("DIP-2405", 240, 200)]),
    ("Paracetamol", "750 mg comprimido", ClasseControle.COMUM, 80, [("PAR-2410", 300, 50)]),
    ("Soro fisiológico", "0,9% 500 mL", ClasseControle.COMUM, 40, [("SF-2499", 400, 120)]),
    ("Amoxicilina", "500 mg cápsula", ClasseControle.COMUM, 30, [("AMX-2407", 12, 40)]),
    ("Morfina", "10 mg/mL injetável", ClasseControle.CONTROLADO, 10, [("MOR-2402", 180, 25)]),
    ("Diazepam", "10 mg comprimido", ClasseControle.CONTROLADO, 20, [("DZP-2403", 25, 15)]),
]


def popular(SessionLocal: sessionmaker[Session], hoje: date) -> bool:
    """Cria os dados se o banco estiver vazio. Devolve True se criou algo."""
    with SessionLocal() as s:
        if s.scalar(select(Funcionario).limit(1)):
            return False
        pessoas = {email: criar_funcionario(s, nome=n, email=email, senha=SENHA_DEMO, perfil=p)
                   for n, email, p in FUNCIONARIOS}
        farm = pessoas["farmaceutico@hospital.demo"]
        enf = pessoas["enfermeiro@hospital.demo"]
        momento = datetime.combine(hoje, time(8, 0))
        ids = {}
        for nome, apres, classe, minimo, lotes in MEDICAMENTOS:
            m = criar_medicamento(s, nome=nome, apresentacao=apres, classe=classe, estoque_minimo=minimo)
            ids[nome] = m.id
            for codigo, dias, qtd in lotes:
                registrar_entrada(s, funcionario=farm, agora=momento, medicamento_id=m.id,
                                  codigo_lote=codigo, validade=hoje + timedelta(days=dias), quantidade=qtd)
        registrar_retirada(s, funcionario=enf, agora=momento + timedelta(hours=1),
                           medicamento_id=ids["Dipirona"], quantidade=30, setor="UTI")
        registrar_retirada(s, funcionario=farm, agora=momento + timedelta(hours=2),
                           medicamento_id=ids["Morfina"], quantidade=2, setor="Centro Cirúrgico",
                           paciente="Paciente simulado 0042")
        return True
