# ANÁLISE E DESENVOLVIMENTO DE SISTEMAS

**JÉSSICA OLIVEIRA MEIRA**

**PROJETO INTEGRADO INTERDISCIPLINAR – ANÁLISE E DESENVOLVIMENTO DE SISTEMAS**

**Desenvolvimento de um Sistema Web para a TechMarket**

**VITÓRIA DA CONQUISTA - BA**

**2025**

## 1 INTRODUÇÃO

Este trabalho apresenta o desenvolvimento de um sistema web abrangente para a TechMarket, uma empresa de e-commerce em rápido crescimento. O projeto foi concebido para resolver cinco desafios críticos que impactavam diretamente o desempenho, a escalabilidade e a experiência do usuário da plataforma. Os desafios incluíam falhas em horários de pico, alta latência em transações, arquitetura monolítica, frontend não responsivo e falta de validações robustas. A solução proposta e implementada visa transformar a infraestrutura da TechMarket em um sistema robusto, escalável e confiável, utilizando as melhores práticas de desenvolvimento de software e computação em nuvem.

O objetivo principal foi aplicar conhecimentos adquiridos em diversas disciplinas para criar uma solução integrada que abordasse desde o escalonamento em nuvem até a otimização de banco de dados e validações de formulário, culminando em uma experiência de usuário aprimorada e maior eficiência operacional. O desenvolvimento seguiu uma abordagem iterativa, focando na implementação de APIs seguras, interfaces responsivas e mecanismos de validação em tempo real.

## 2 DESENVOLVIMENTO

O desenvolvimento do sistema TechMarket foi estruturado em cinco passos principais, cada um abordando um desafio específico e aplicando soluções técnicas integradas. Cada passo foi projetado para construir sobre o anterior, garantindo uma arquitetura coesa e funcional.

### 2.1 Passo 1: Computação em Nuvem (Escalonamento)

**Problema**: A TechMarket enfrentava instabilidades e falhas durante picos de demanda devido à sua arquitetura monolítica e escalonamento vertical limitado. Isso resultava em prejuízos significativos e perda de vendas.

**Solução Implementada**: Foi proposta e implementada uma migração para uma arquitetura de microsserviços com auto-scaling na Google Cloud Platform (GCP). Esta abordagem permite a distribuição eficiente da carga de trabalho entre servidores, aumentando a disponibilidade e a resiliência do sistema.

**Escalonamento Vertical vs. Horizontal**:

*   **Escalonamento Vertical**: Aumentar os recursos (CPU, RAM) de um único servidor. Possui limites físicos e de custo, sendo menos flexível para picos de demanda.
*   **Escalonamento Horizontal**: Adicionar mais instâncias de servidores para distribuir a carga. Oferece maior flexibilidade, resiliência e custo-benefício, ideal para ambientes com demanda variável. 

**Configuração de Auto-scaling na GCP (Exemplo com Google Cloud Run)**:

Para configurar a aplicação horizontalmente, utilizamos serviços como o Google Cloud Run, que permite o deploy de contêineres sem servidor com auto-scaling automático. A configuração envolve definir limites mínimos e máximos de instâncias, bem como recursos de CPU e memória por instância, para que o sistema possa escalar de acordo com a demanda.

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: techmarket-api
  annotations:
    run.googleapis.com/cpu-throttling: "false"
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "100"
        run.googleapis.com/cpu: "2"
        run.googleapis.com/memory: "2Gi"
    spec:
      containerConcurrency: 80
      containers:
      - image: gcr.io/project/techmarket-api
        resources:
          limits:
            cpu: "2"
            memory: "2Gi"
```

Esta configuração permite que a API da TechMarket escale de 1 a 100 instâncias automaticamente, garantindo que a capacidade seja ajustada conforme a necessidade, otimizando custos e mantendo a performance.

### 2.2 Passo 2: Frameworks para Desenvolvimento de Software (API Financeira)

**Problema**: A TechMarket necessitava de uma API de transações financeiras segura, validada e com retorno confiável, para evitar problemas como latência elevada e transferências duplicadas, comuns em sistemas sem validações robustas.

**Solução Implementada**: Foi desenvolvida uma API RESTful utilizando Python Flask, focada em segurança, validação de saldo, registro de transações e geração de códigos únicos para cada operação. A API expõe endpoints para listagem de contas, extrato, transferência e depósito.

**Endpoint de Transferência Financeira (Exemplo)**:

Um dos endpoints críticos é o de transferência, que inclui validações de saldo e registro detalhado da transação:

```python
@financial_bp.route('/transferencia', methods=['POST'])
def realizar_transferencia():
    data = request.get_json()
    conta_origem_id = data.get('conta_origem_id')
    conta_destino_id = data.get('conta_destino_id')
    valor = data.get('valor')
    descricao = data.get('descricao')

    if not all([conta_origem_id, conta_destino_id, valor, descricao]):
        return jsonify({'message': 'Dados incompletos'}), 400

    try:
        transferencia = Transacao.realizar_transferencia(conta_origem_id, conta_destino_id, valor, descricao)
        return jsonify({
            'message': 'Transferência realizada com sucesso',
            'transacao_id': transferencia.id,
            'codigo_unico': transferencia.codigo_unico
        }), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return jsonify({'message': 'Erro interno do servidor'}), 500
```

**Validações e Segurança**:

*   **Validação de Saldo**: Antes de qualquer transferência, o saldo da conta de origem é verificado para garantir que há fundos suficientes.
*   **Registro da Transação**: Cada transação é registrada no banco de dados com detalhes como conta de origem, conta de destino, valor, descrição e data/hora.
*   **Código Único**: Um UUID (Universally Unique Identifier) é gerado para cada transação, garantindo rastreabilidade e prevenindo duplicidades.
*   **Tratamento de Erros**: A API inclui tratamento de exceções para lidar com cenários como saldo insuficiente ou dados inválidos, retornando mensagens claras ao cliente.

### 2.3 Passo 3: Programação Web (Extrato Bancário Responsivo)

**Problema**: O frontend da TechMarket não era responsivo, resultando em má experiência para usuários móveis e dificuldade na visualização de informações críticas, como o extrato bancário.

**Solução Implementada**: Foi desenvolvida uma interface de extrato bancário responsiva, utilizando HTML, CSS (com foco em mobile-first) e JavaScript, integrada ao backend Flask. O objetivo foi garantir que o extrato fosse facilmente visualizável em diferentes tamanhos de tela, com destaque para transações de alto valor.

**Design Responsivo e Destaque de Transações**:

O extrato bancário foi projetado para se adaptar a dispositivos móveis, garantindo que as informações sejam apresentadas de forma clara e organizada. Transações acima de R$ 5.000,00 são destacadas visualmente para chamar a atenção do usuário. A performance de carregamento foi otimizada através de um frontend leve e chamadas assíncronas à API.

### 2.4 Passo 4: Programação e Desenvolvimento de Banco de Dados (Otimização de Consultas SQL)

**Problema**: O banco de dados da TechMarket estava sobrecarregado por consultas não otimizadas, causando lentidão e travamentos, especialmente ao calcular saldos e listar transações. Isso poderia levar a prejuízos por erros nos valores apresentados.

**Solução Implementada**: Foram implementadas estratégias de otimização de queries SQL e indexação de banco de dados para garantir consultas rápidas e precisas. Isso incluiu a criação de índices e a otimização de procedures para cálculo de saldo e listagem de transações recentes.

**Estratégias de Otimização**:

*   **Indexação**: Criação de índices em colunas frequentemente consultadas (ex: `conta_id`, `data_transacao`, `numero_conta`) para acelerar a recuperação de dados. 
*   **Connection Pooling**: Configuração de um pool de conexões para gerenciar e reutilizar conexões com o banco de dados, reduzindo a sobrecarga de abertura e fechamento de novas conexões. 
*   **Consultas Otimizadas**: Reescrita de queries para utilizar `JOINs` eficientes, paginação (`LIMIT` e `OFFSET`) e `lazy loading` em ORMs (Object-Relational Mappers) como SQLAlchemy, minimizando a quantidade de dados transferidos e processados.

**Exemplo de Query Otimizada para Extrato**:

```python
def obter_extrato_otimizado(conta_id, limite=10, offset=0):
    return db.session.query(Transacao)\
        .filter(Transacao.conta_id == conta_id)\
        .order_by(Transacao.data_transacao.desc())\
        .limit(limite)\
        .offset(offset)\
        .options(joinedload(Transacao.conta))\
        .all()
```

Essas otimizações resultaram em uma redução significativa no tempo de resposta das consultas e aumentaram a capacidade do sistema de lidar com um grande volume de transações simultâneas.

### 2.5 Passo 5: Desenvolvimento em JavaScript (Validação de Formulário)

**Problema**: A TechMarket enfrentava problemas com dados inconsistentes no processo de abertura de conta devido à falta de validações de formulário, resultando em frustração do cliente e aumento da carga de trabalho manual.

**Solução Implementada**: Foi implementado um sistema de validação de formulário robusto em tempo real, utilizando JavaScript, para verificar a correção de CPF, data de nascimento e número de telefone. As validações fornecem feedback visual imediato ao usuário.

**Validações Implementadas**:

*   **CPF**: Verificação de 11 dígitos e algoritmo de validação dos dígitos verificadores. 
*   **Data de Nascimento**: Validação de formato, verificação de que a data não é futura e cálculo da idade mínima (ex: 18 anos).
*   **Telefone**: Verificação do número de dígitos (10 ou 11), formato e validação de DDD.

## 3 CONCLUSÃO

O projeto de desenvolvimento do sistema web para a TechMarket abordou e resolveu com sucesso os cinco desafios críticos identificados: escalabilidade em nuvem, desenvolvimento de API segura, responsividade web, otimização de banco de dados e validação de formulários. Através da implementação de uma arquitetura de microsserviços na Google Cloud Platform, uma API financeira robusta em Python Flask, um frontend responsivo com HTML/CSS/JavaScript, otimizações de consultas SQL e validações de formulário em tempo real, a TechMarket foi transformada em uma plataforma moderna, eficiente e resiliente.

As principais conquistas incluem uma redução drástica na latência de transações, aumento significativo na capacidade de usuários simultâneos, economia de custos de infraestrutura e uma melhoria substancial na experiência do usuário. O sistema está agora preparado para suportar o crescimento futuro da empresa, garantindo alta disponibilidade e integridade dos dados. Este projeto demonstra a aplicação prática de conceitos avançados de desenvolvimento de software e computação em nuvem para resolver problemas de negócios complexos.

---

**Desenvolvido por**: Jéssica Oliveira Meira  
**Projeto**: Integrado Interdisciplinar - Análise e Desenvolvimento de Sistemas  