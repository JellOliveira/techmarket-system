from flask import Blueprint, request, jsonify
import re
from datetime import datetime, date

validation_bp = Blueprint('validation', __name__)

def validar_cpf(cpf):
    """Validar CPF brasileiro"""
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False, "CPF deve conter exatamente 11 dígitos"
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False, "CPF inválido - todos os dígitos são iguais"
    
    # Validação do algoritmo do CPF
    def calcular_digito(cpf_parcial, peso_inicial):
        soma = sum(int(cpf_parcial[i]) * (peso_inicial - i) for i in range(len(cpf_parcial)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto
    
    # Calcula o primeiro dígito verificador
    primeiro_digito = calcular_digito(cpf[:9], 10)
    if int(cpf[9]) != primeiro_digito:
        return False, "CPF inválido - primeiro dígito verificador incorreto"
    
    # Calcula o segundo dígito verificador
    segundo_digito = calcular_digito(cpf[:10], 11)
    if int(cpf[10]) != segundo_digito:
        return False, "CPF inválido - segundo dígito verificador incorreto"
    
    return True, "CPF válido"

def validar_data_nascimento(data_nascimento):
    """Validar data de nascimento"""
    try:
        # Tenta diferentes formatos de data
        formatos = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
        data_obj = None
        
        for formato in formatos:
            try:
                data_obj = datetime.strptime(data_nascimento, formato).date()
                break
            except ValueError:
                continue
        
        if data_obj is None:
            return False, "Formato de data inválido. Use DD/MM/AAAA ou AAAA-MM-DD"
        
        # Verifica se a data não é futura
        hoje = date.today()
        if data_obj > hoje:
            return False, "Data de nascimento não pode ser futura"
        
        # Verifica idade mínima (18 anos)
        idade = hoje.year - data_obj.year - ((hoje.month, hoje.day) < (data_obj.month, data_obj.day))
        if idade < 18:
            return False, f"Idade mínima é 18 anos. Idade atual: {idade} anos"
        
        # Verifica idade máxima razoável (120 anos)
        if idade > 120:
            return False, f"Idade muito alta: {idade} anos"
        
        return True, f"Data válida. Idade: {idade} anos"
        
    except Exception as e:
        return False, f"Erro ao validar data: {str(e)}"

def validar_telefone(telefone):
    """Validar número de telefone brasileiro"""
    # Remove caracteres não numéricos
    telefone_limpo = re.sub(r'[^0-9]', '', telefone)
    
    # Verifica se tem 10 ou 11 dígitos (com ou sem 9 no celular)
    if len(telefone_limpo) not in [10, 11]:
        return False, "Telefone deve ter 10 ou 11 dígitos"
    
    # Padrões válidos para telefone brasileiro
    # Celular: (XX) 9XXXX-XXXX ou (XX) XXXXX-XXXX
    # Fixo: (XX) XXXX-XXXX
    
    if len(telefone_limpo) == 11:
        # Celular com 9 dígitos
        if not telefone_limpo[2] == '9':
            return False, "Para celular com 11 dígitos, o terceiro dígito deve ser 9"
        
        # Verifica DDD válido (11-99)
        ddd = int(telefone_limpo[:2])
        if ddd < 11 or ddd > 99:
            return False, "DDD inválido"
        
        return True, "Telefone celular válido"
    
    elif len(telefone_limpo) == 10:
        # Telefone fixo ou celular antigo
        ddd = int(telefone_limpo[:2])
        if ddd < 11 or ddd > 99:
            return False, "DDD inválido"
        
        # Se começar com 9, é celular antigo
        if telefone_limpo[2] == '9':
            return True, "Telefone celular (formato antigo) válido"
        else:
            return True, "Telefone fixo válido"
    
    return False, "Formato de telefone inválido"

@validation_bp.route('/validar-cpf', methods=['POST'])
def validar_cpf_endpoint():
    """Endpoint para validar CPF"""
    try:
        data = request.get_json()
        print(f"[DEBUG] Recebido para validar-cpf: {data}")
        cpf = data.get("cpf", "")
        
        if not cpf:
            return jsonify({
                'valido': False,
                'erro': 'CPF é obrigatório'
            }), 400
        
        valido, mensagem = validar_cpf(cpf)
        
        return jsonify({
            'valido': valido,
            'mensagem': mensagem,
            'cpf_formatado': re.sub(r'[^0-9]', '', cpf) if valido else None
        }), 200
        
    except Exception as e:
        return jsonify({
            'valido': False,
            'erro': f'Erro interno: {str(e)}'
        }), 500

@validation_bp.route('/validar-data-nascimento', methods=['POST'])
def validar_data_nascimento_endpoint():
    """Endpoint para validar data de nascimento"""
    try:
        data = request.get_json()
        print(f"[DEBUG] Recebido para validar-data-nascimento: {data}")
        data_nascimento = data.get("data_nascimento", "")


        
        if not data_nascimento:
            return jsonify({
                'valido': False,
                'erro': 'Data de nascimento é obrigatória'
            }), 400
        
        valido, mensagem = validar_data_nascimento(data_nascimento)
        
        return jsonify({
            'valido': valido,
            'mensagem': mensagem
        }), 200
        
    except Exception as e:
        return jsonify({
            'valido': False,
            'erro': f'Erro interno: {str(e)}'
        }), 500

@validation_bp.route('/validar-telefone', methods=['POST'])
def validar_telefone_endpoint():
    """Endpoint para validar telefone"""
    try:
        data = request.get_json()
        print(f"[DEBUG] Recebido para validar-telefone: {data}")
        telefone = data.get("telefone", "")
        
        if not telefone:
            return jsonify({
                'valido': False,
                'erro': 'Telefone é obrigatório'
            }), 400
        
        valido, mensagem = validar_telefone(telefone)
        
        # Formatar telefone se válido
        telefone_formatado = None
        if valido:
            telefone_limpo = re.sub(r'[^0-9]', '', telefone)
            if len(telefone_limpo) == 11:
                telefone_formatado = f"({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}"
            elif len(telefone_limpo) == 10:
                telefone_formatado = f"({telefone_limpo[:2]}) {telefone_limpo[2:6]}-{telefone_limpo[6:]}"
        
        return jsonify({
            'valido': valido,
            'mensagem': mensagem,
            'telefone_formatado': telefone_formatado
        }), 200
        
    except Exception as e:
        return jsonify({
            'valido': False,
            'erro': f'Erro interno: {str(e)}'
        }), 500

@validation_bp.route('/validar-formulario', methods=['POST'])
def validar_formulario_completo():
    """Endpoint para validar formulário completo"""
    try:
        data = request.get_json()
        print(f"[DEBUG] Recebido para validar-formulario: {data}")
        
        resultados = {
            'valido_geral': True,
            'validacoes': {}
        }
        
        # Validar CPF
        if 'cpf' in data:
            valido_cpf, msg_cpf = validar_cpf(data['cpf'])
            resultados['validacoes']['cpf'] = {
                'valido': valido_cpf,
                'mensagem': msg_cpf
            }
            if not valido_cpf:
                resultados['valido_geral'] = False
        
        # Validar data de nascimento
        if 'data_nascimento' in data:

            print(f"[DEBUG] Data de nascimento recebida no validar-formulario (antes da função): {data['data_nascimento']}")
            valido_data, msg_data = validar_data_nascimento(data['data_nascimento'])
            resultados['validacoes']['data_nascimento'] = {
                'valido': valido_data,
                'mensagem': msg_data
            }
            if not valido_data:
                resultados['valido_geral'] = False
        
        # Validar telefone
        if 'telefone' in data:
            valido_tel, msg_tel = validar_telefone(data['telefone'])
            resultados['validacoes']['telefone'] = {
                'valido': valido_tel,
                'mensagem': msg_tel
            }
            if not valido_tel:
                resultados['valido_geral'] = False
        
        return jsonify(resultados), 200
        
    except Exception as e:
        return jsonify({
            'valido_geral': False,
            'erro': f'Erro interno: {str(e)}'
        }), 500
