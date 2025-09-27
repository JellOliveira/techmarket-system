from src.models.user import db
from datetime import datetime
import uuid

class Conta(db.Model):
    __tablename__ = 'contas'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_conta = db.Column(db.String(20), unique=True, nullable=False)
    titular = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    saldo = db.Column(db.Numeric(15, 2), default=0.00, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamento com transações
    transacoes_origem = db.relationship('Transacao', foreign_keys='Transacao.conta_origem_id', backref='conta_origem', lazy='dynamic')
    transacoes_destino = db.relationship('Transacao', foreign_keys='Transacao.conta_destino_id', backref='conta_destino', lazy='dynamic')
    
    def __repr__(self):
        return f'<Conta {self.numero_conta} - {self.titular}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_conta': self.numero_conta,
            'titular': self.titular,
            'cpf': self.cpf,
            'saldo': float(self.saldo),
            'data_criacao': self.data_criacao.isoformat(),
            'ativo': self.ativo
        }

class Transacao(db.Model):
    __tablename__ = 'transacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo_unico = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    conta_origem_id = db.Column(db.Integer, db.ForeignKey('contas.id'), nullable=True)
    conta_destino_id = db.Column(db.Integer, db.ForeignKey('contas.id'), nullable=True)
    tipo = db.Column(db.String(20), nullable=False)  # 'transferencia', 'deposito', 'saque'
    valor = db.Column(db.Numeric(15, 2), nullable=False)
    descricao = db.Column(db.String(200))
    data_transacao = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='concluida')  # 'pendente', 'concluida', 'cancelada'
    
    def __repr__(self):
        return f'<Transacao {self.codigo_unico} - {self.tipo} - R$ {self.valor}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'codigo_unico': self.codigo_unico,
            'conta_origem_id': self.conta_origem_id,
            'conta_destino_id': self.conta_destino_id,
            'tipo': self.tipo,
            'valor': float(self.valor),
            'descricao': self.descricao,
            'data_transacao': self.data_transacao.isoformat(),
            'status': self.status
        }
