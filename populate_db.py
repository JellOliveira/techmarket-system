#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados de exemplo
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db
from src.models.financial import Conta, Transacao
from src.main import app
from decimal import Decimal
from datetime import datetime, timedelta
import uuid

def criar_dados_exemplo():
    """Criar dados de exemplo para demonstração"""

    with app.app_context():
        # Limpar dados existentes
        db.drop_all()
        db.create_all()

        print("Criando contas de exemplo...")

        # LISTA DE CONTAS – ADICIONE MAIS AQUI SE DESEJAR!
        contas = [
            {
                'numero_conta': '000001',
                'titular': 'Maria Silva Santos',
                'cpf': '12345678901',
                'saldo': Decimal('15000.00')
            },
            {
                'numero_conta': '000002',
                'titular': 'João Pedro Oliveira',
                'cpf': '98765432109',
                'saldo': Decimal('8500.50')
            },
            {
                'numero_conta': '000003',
                'titular': 'Ana Carolina Ferreira',
                'cpf': '11122233344',
                'saldo': Decimal('25000.75')
            },
            {
                'numero_conta': '000004',
                'titular': 'Carlos Eduardo Lima',
                'cpf': '55566677788',
                'saldo': Decimal('3200.00')
            },
            {
                'numero_conta': '000005',
                'titular': 'Fernanda Costa Alves',
                'cpf': '99988877766',
                'saldo': Decimal('12750.25')
            },
            # Novas contas – adicione abaixo nesse formato:
            {
                'numero_conta': '000006',
                'titular': 'Lucas Neves Souza',
                'cpf': '22233344455',
                'saldo': Decimal('5400.80')
            },
            {
                'numero_conta': '000007',
                'titular': 'Bruna Martins dos Reis',
                'cpf': '77788899900',
                'saldo': Decimal('10000.00')
            },
            # Sempre seguindo o padrão acima!
        ]

        contas_criadas = []
        for conta_data in contas:
            conta = Conta(**conta_data)
            db.session.add(conta)
            contas_criadas.append(conta)

        db.session.commit()
        print(f"✅ {len(contas_criadas)} contas criadas com sucesso!")

        print("Criando transações de exemplo...")

        # Criar transações de exemplo
        transacoes = []

        # Transações dos últimos 30 dias
        base_date = datetime.now()

        # Depósitos iniciais
        for i, conta in enumerate(contas_criadas):
            transacao = Transacao(
                codigo_unico=str(uuid.uuid4()),
                conta_destino_id=conta.id,
                tipo='deposito',
                valor=conta.saldo,
                descricao='Depósito inicial',
                data_transacao=base_date - timedelta(days=30-i),
                status='concluida'
            )
            transacoes.append(transacao)

        # Transferências entre contas (ajustar caso adicione muitas contas!)
        transferencias_exemplo = [
            {
                'origem': 0, 'destino': 1, 'valor': 1500.00, 'dias_atras': 25,
                'descricao': 'Pagamento de serviços'
            },
            {
                'origem': 2, 'destino': 0, 'valor': 2800.50, 'dias_atras': 20,
                'descricao': 'Transferência para investimento'
            },
            {
                'origem': 1, 'destino': 3, 'valor': 750.00, 'dias_atras': 18,
                'descricao': 'Pagamento de aluguel'
            },
            {
                'origem': 4, 'destino': 2, 'valor': 6200.00, 'dias_atras': 15,
                'descricao': 'Pagamento de fornecedor - VALOR ALTO'
            },
            {
                'origem': 0, 'destino': 4, 'valor': 450.75, 'dias_atras': 12,
                'descricao': 'Reembolso de despesas'
            },
            {
                'origem': 3, 'destino': 1, 'valor': 8900.00, 'dias_atras': 10,
                'descricao': 'Pagamento de contrato - VALOR ALTO'
            },
            {
                'origem': 2, 'destino': 0, 'valor': 320.00, 'dias_atras': 8,
                'descricao': 'Divisão de conta'
            },
            {
                'origem': 1, 'destino': 4, 'valor': 1200.00, 'dias_atras': 5,
                'descricao': 'Pagamento de consultoria'
            },
            {
                'origem': 4, 'destino': 3, 'valor': 15000.00, 'dias_atras': 3,
                'descricao': 'Aquisição de equipamentos - VALOR ALTO'
            },
            {
                'origem': 0, 'destino': 2, 'valor': 680.25, 'dias_atras': 1,
                'descricao': 'Transferência para poupança'
            }
        ]

        for tf in transferencias_exemplo:
            # Só gera transferência se existirem contas nas posições indicadas
            if tf['origem'] < len(contas_criadas) and tf['destino'] < len(contas_criadas):
                conta_origem = contas_criadas[tf['origem']]
                conta_destino = contas_criadas[tf['destino']]
                valor = Decimal(str(tf['valor']))

                if conta_origem.saldo >= valor:
                    conta_origem.saldo -= valor
                    conta_destino.saldo += valor

                    transacao = Transacao(
                        codigo_unico=str(uuid.uuid4()),
                        conta_origem_id=conta_origem.id,
                        conta_destino_id=conta_destino.id,
                        tipo='transferencia',
                        valor=valor,
                        descricao=tf['descricao'],
                        data_transacao=base_date - timedelta(days=tf['dias_atras']),
                        status='concluida'
                    )
                    transacoes.append(transacao)

        # Adicionar algumas transações recentes (últimos 3 dias)
        transacoes_recentes = [
            {
                'origem': 2, 'destino': 1, 'valor': 250.00, 'horas_atras': 48,
                'descricao': 'Pagamento de jantar'
            },
            {
                'origem': 0, 'destino': 3, 'valor': 125.50, 'horas_atras': 24,
                'descricao': 'Divisão de combustível'
            },
            {
                'origem': 4, 'destino': 0, 'valor': 890.00, 'horas_atras': 12,
                'descricao': 'Reembolso de viagem'
            },
            {
                'origem': 1, 'destino': 2, 'valor': 75.25, 'horas_atras': 6,
                'descricao': 'Pagamento de aplicativo'
            },
            {
                'origem': 3, 'destino': 4, 'valor': 1850.00, 'horas_atras': 2,
                'descricao': 'Pagamento de freelance'
            }
        ]

        for tf in transacoes_recentes:
            if tf['origem'] < len(contas_criadas) and tf['destino'] < len(contas_criadas):
                conta_origem = contas_criadas[tf['origem']]
                conta_destino = contas_criadas[tf['destino']]
                valor = Decimal(str(tf['valor']))

                if conta_origem.saldo >= valor:
                    conta_origem.saldo -= valor
                    conta_destino.saldo += valor

                    transacao = Transacao(
                        codigo_unico=str(uuid.uuid4()),
                        conta_origem_id=conta_origem.id,
                        conta_destino_id=conta_destino.id,
                        tipo='transferencia',
                        valor=valor,
                        descricao=tf['descricao'],
                        data_transacao=base_date - timedelta(hours=tf['horas_atras']),
                        status='concluida'
                    )
                    transacoes.append(transacao)

        for transacao in transacoes:
            db.session.add(transacao)

        db.session.commit()
        print(f"✅ {len(transacoes)} transações criadas com sucesso!")

        # Mostrar resumo
        print('\n' + '='*50)
        print('RESUMO DOS DADOS CRIADOS')
        print('='*50)

        for conta in contas_criadas:
            print(f"Conta {conta.numero_conta} - {conta.titular}")
            print(f"  CPF: {conta.cpf}")
            print(f"  Saldo: R$ {conta.saldo:,.2f}")

            total_transacoes = Transacao.query.filter(
                (Transacao.conta_origem_id == conta.id) |
                (Transacao.conta_destino_id == conta.id)
            ).count()
            print(f"  Transações: {total_transacoes}")
            print()

        print(f"Total de contas: {len(contas_criadas)}")
        print(f"Total de transações: {len(transacoes)}")
        print("\n✅ Banco de dados populado com sucesso!")

if __name__ == '__main__':
    criar_dados_exemplo()
