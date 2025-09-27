from flask import Blueprint, request, jsonify
from src.models.financial import db, Conta, Transacao
from decimal import Decimal
import uuid
from datetime import datetime, timedelta
from sqlalchemy import desc, and_

financial_bp = Blueprint('financial', __name__)

@financial_bp.route('/contas', methods=['POST'])
def criar_conta():
    """Criar uma nova conta bancária"""
    try:
        data = request.get_json()
        
        # Validações básicas
        if not data.get('titular') or not data.get('cpf'):
            return jsonify({'erro': 'Titular e CPF são obrigatórios'}), 400
        
        # Verificar se CPF já existe
        conta_existente = Conta.query.filter_by(cpf=data['cpf']).first()
        if conta_existente:
            return jsonify({'erro': 'CPF já cadastrado'}), 400
        
        # Gerar número da conta único
        numero_conta = f"{len(Conta.query.all()) + 1:06d}"
        
        nova_conta = Conta(
            numero_conta=numero_conta,
            titular=data['titular'],
            cpf=data['cpf'],
            saldo=Decimal(str(data.get('saldo_inicial', 0)))
        )
        
        db.session.add(nova_conta)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'conta': nova_conta.to_dict(),
            'mensagem': 'Conta criada com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@financial_bp.route('/contas', methods=['GET'])
def listar_contas():
    """Listar todas as contas"""
    try:
        contas = Conta.query.filter_by(ativo=True).all()
        return jsonify({
            'contas': [conta.to_dict() for conta in contas]
        }), 200
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@financial_bp.route('/contas/<int:conta_id>', methods=['GET'])
def obter_conta(conta_id):
    """Obter detalhes de uma conta específica"""
    try:
        conta = Conta.query.get(conta_id)
        if not conta:
            return jsonify({'erro': 'Conta não encontrada'}), 404
        
        return jsonify({
            'conta': conta.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@financial_bp.route('/transferencia', methods=['POST'])
def realizar_transferencia():
    """Realizar transferência financeira entre contas"""
    try:
        data = request.get_json()
        
        # Validações de entrada
        campos_obrigatorios = ['conta_origem_id', 'conta_destino_id', 'valor']
        for campo in campos_obrigatorios:
            if campo not in data:
                return jsonify({'erro': f'Campo {campo} é obrigatório'}), 400
        
        valor = Decimal(str(data['valor']))
        if valor <= 0:
            return jsonify({'erro': 'Valor deve ser maior que zero'}), 400
        
        # Buscar contas
        conta_origem = Conta.query.get(data['conta_origem_id'])
        conta_destino = Conta.query.get(data['conta_destino_id'])
        
        if not conta_origem:
            return jsonify({'erro': 'Conta de origem não encontrada'}), 404
        if not conta_destino:
            return jsonify({'erro': 'Conta de destino não encontrada'}), 404
        
        if not conta_origem.ativo or not conta_destino.ativo:
            return jsonify({'erro': 'Uma das contas está inativa'}), 400
        
        # Validação de saldo
        if conta_origem.saldo < valor:
            return jsonify({
                'erro': 'Saldo insuficiente',
                'saldo_disponivel': float(conta_origem.saldo)
            }), 400
        
        # Gerar código único para a transação
        codigo_unico = str(uuid.uuid4())
        
        # Iniciar transação no banco de dados
        try:
            # Atualizar saldos
            conta_origem.saldo -= valor
            conta_destino.saldo += valor
            
            # Registrar a transação
            nova_transacao = Transacao(
                codigo_unico=codigo_unico,
                conta_origem_id=conta_origem.id,
                conta_destino_id=conta_destino.id,
                tipo='transferencia',
                valor=valor,
                descricao=data.get('descricao', f'Transferência de {conta_origem.titular} para {conta_destino.titular}'),
                status='concluida'
            )
            
            db.session.add(nova_transacao)
            db.session.commit()
            
            return jsonify({
                'sucesso': True,
                'codigo_transacao': codigo_unico,
                'valor': float(valor),
                'conta_origem': {
                    'id': conta_origem.id,
                    'numero': conta_origem.numero_conta,
                    'saldo_atual': float(conta_origem.saldo)
                },
                'conta_destino': {
                    'id': conta_destino.id,
                    'numero': conta_destino.numero_conta,
                    'saldo_atual': float(conta_destino.saldo)
                },
                'data_transacao': nova_transacao.data_transacao.isoformat(),
                'mensagem': 'Transferência realizada com sucesso'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'erro': f'Erro ao processar transferência: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@financial_bp.route('/extrato/<int:conta_id>', methods=['GET'])
def obter_extrato(conta_id):
    """Obter extrato de uma conta com as últimas transações"""
    try:
        conta = Conta.query.get(conta_id)
        if not conta:
            return jsonify({'erro': 'Conta não encontrada'}), 404
        
        # Parâmetros de consulta
        limite = request.args.get('limite', 10, type=int)
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        # Query base para transações
        query = Transacao.query.filter(
            (Transacao.conta_origem_id == conta_id) | 
            (Transacao.conta_destino_id == conta_id)
        )
        
        # Filtros de data
        if data_inicio:
            try:
                data_inicio_obj = datetime.fromisoformat(data_inicio)
                query = query.filter(Transacao.data_transacao >= data_inicio_obj)
            except ValueError:
                return jsonify({'erro': 'Formato de data_inicio inválido. Use ISO format (YYYY-MM-DD)'}), 400
        
        if data_fim:
            try:
                data_fim_obj = datetime.fromisoformat(data_fim)
                query = query.filter(Transacao.data_transacao <= data_fim_obj)
            except ValueError:
                return jsonify({'erro': 'Formato de data_fim inválido. Use ISO format (YYYY-MM-DD)'}), 400
        
        # Ordenar por data decrescente e limitar
        transacoes = query.order_by(desc(Transacao.data_transacao)).limit(limite).all()
        
        # Processar transações para o extrato
        extrato_transacoes = []
        for transacao in transacoes:
            transacao_dict = transacao.to_dict()
            
            # Determinar se é entrada ou saída para esta conta
            if transacao.conta_destino_id == conta_id:
                transacao_dict['tipo_movimento'] = 'entrada'
                transacao_dict['conta_relacionada'] = transacao.conta_origem.numero_conta if transacao.conta_origem else 'N/A'
            else:
                transacao_dict['tipo_movimento'] = 'saida'
                transacao_dict['conta_relacionada'] = transacao.conta_destino.numero_conta if transacao.conta_destino else 'N/A'
            
            # Destacar transações acima de R$ 5.000
            transacao_dict['valor_alto'] = float(transacao.valor) > 5000.0
            
            extrato_transacoes.append(transacao_dict)
        
        return jsonify({
            'conta': conta.to_dict(),
            'saldo_atual': float(conta.saldo),
            'transacoes': extrato_transacoes,
            'total_transacoes': len(extrato_transacoes),
            'periodo': {
                'data_inicio': data_inicio,
                'data_fim': data_fim
            }
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@financial_bp.route('/transacoes/<codigo_unico>', methods=['GET'])
def obter_transacao(codigo_unico):
    """Obter detalhes de uma transação específica pelo código único"""
    try:
        transacao = Transacao.query.filter_by(codigo_unico=codigo_unico).first()
        if not transacao:
            return jsonify({'erro': 'Transação não encontrada'}), 404
        
        return jsonify({
            'transacao': transacao.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@financial_bp.route('/deposito', methods=['POST'])
def realizar_deposito():
    """Realizar depósito em uma conta"""
    try:
        data = request.get_json()
        
        if not data.get('conta_id') or not data.get('valor'):
            return jsonify({'erro': 'conta_id e valor são obrigatórios'}), 400
        
        valor = Decimal(str(data['valor']))
        if valor <= 0:
            return jsonify({'erro': 'Valor deve ser maior que zero'}), 400
        
        conta = Conta.query.get(data['conta_id'])
        if not conta:
            return jsonify({'erro': 'Conta não encontrada'}), 404
        
        if not conta.ativo:
            return jsonify({'erro': 'Conta está inativa'}), 400
        
        # Gerar código único
        codigo_unico = str(uuid.uuid4())
        
        # Atualizar saldo
        conta.saldo += valor
        
        # Registrar transação
        nova_transacao = Transacao(
            codigo_unico=codigo_unico,
            conta_destino_id=conta.id,
            tipo='deposito',
            valor=valor,
            descricao=data.get('descricao', 'Depósito em conta'),
            status='concluida'
        )
        
        db.session.add(nova_transacao)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'codigo_transacao': codigo_unico,
            'valor': float(valor),
            'saldo_atual': float(conta.saldo),
            'mensagem': 'Depósito realizado com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500
