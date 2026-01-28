from django.db import models

class Cliente(models.Model):
    """
    Representa um cliente da marcenaria Artisan.
    Armazena informações básicas de identificação.
    """
    nome = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nome


class Arquiteto(models.Model):
    """
    Gerencia os parceiros (arquitetos/designers) que indicam obras.
    Usado para controle de comissionamento.
    """
    nome = models.CharField(max_length=255, unique=True)
    data_pagamento = models.DateField(null=True, blank=True)
    porcentagem_padrao = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return self.nome


class Agenda(models.Model):
    """
    Cronograma de produção. Define quando um projeto inicia e quando deve ser entregue.
    """
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    data_inicio = models.DateField(null=True, blank=True)
    data_previsao_termino = models.DateField(null=True, blank=True)
    descricao = models.TextField(blank=True, null=True, help_text="Descrição breve do projeto (ex: Cozinha e Sala)")

    def __str__(self):
        return f"{self.descricao} - {self.cliente}"


class Orcamento(models.Model):
    """
    Registro técnico e financeiro do orçamento apresentado ao cliente.
    O campo 'itens_json' armazena a lista flexível de móveis/ambientes.
    """
    data_criacao = models.CharField(max_length=50, blank=True)
    cliente_nome = models.CharField(max_length=255)
    cliente_endereco = models.TextField(blank=True)
    cliente_cpf = models.CharField(max_length=50, blank=True)
    cliente_email = models.CharField(max_length=255, blank=True)
    cliente_telefone = models.CharField(max_length=50, blank=True)
    
    # Armazena lista de itens como JSON string para flexibilidade (ex: lista de ambientes)
    itens_json = models.TextField(default="[]") 
    
    valor_total_final = models.CharField(max_length=50, blank=True)
    observacoes = models.TextField(blank=True)
    condicoes_pagamento = models.TextField(blank=True)
    
    # Vínculo opcional com a agenda se o orçamento virar projeto
    agenda = models.ForeignKey(Agenda, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Orçamento {self.id} - {self.cliente_nome}"


class Recebimento(models.Model):
    """
    Cabeçalho financeiro de um projeto fechado.
    Define o valor total contratado e as condições gerais.
    """
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    agenda = models.ForeignKey(Agenda, on_delete=models.SET_NULL, null=True)
    tipo_pagamento = models.CharField(max_length=100)  # Ex: Cartão, Cheque, Boleto
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_entrada = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    num_parcelas = models.IntegerField(default=0)
    valor_parcela = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_1_venc = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Recebimento {self.id} - {self.cliente}"


class Parcela(models.Model):
    """
    Parcelas individuais geradas a partir de um Recebimento.
    Controla o status financeiro mês a mês.
    """
    recebimento = models.ForeignKey(Recebimento, on_delete=models.CASCADE)
    num_parcela = models.IntegerField(help_text="0 para entrada, 1+ para parcelas normais")
    valor_parcela = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_vencimento = models.DateField(null=True, blank=True)
    
    # Controle de baixa (pagamento realizado)
    data_recebimento = models.DateField(null=True, blank=True)
    valor_recebido = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)

    def __str__(self):
        status = "Pago" if self.valor_recebido else "Pendente"
        return f"Parcela {self.num_parcela} - {status}"


class Comissao(models.Model):
    """
    Registro de comissões devidas a arquitetos ou vendedores parceiros.
    Calcula automaticamente o valor com base na porcentagem.
    """
    data = models.DateField(null=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    recebimento = models.ForeignKey(Recebimento, on_delete=models.SET_NULL, null=True)
    arquiteto = models.ForeignKey(Arquiteto, on_delete=models.SET_NULL, null=True, blank=True)
    beneficiario = models.CharField(max_length=255, blank=True)
    descricao = models.TextField(blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    porcentagem = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    valor_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        """
        Automatização: Ao salvar, calcula o valor da comissão se houver porcentagem definida.
        Também define o nome do beneficiário baseado no arquiteto selecionado.
        """
        if self.recebimento:
            self.valor_base = self.recebimento.valor_total
            if self.porcentagem and self.porcentagem > 0:
                self.valor = (self.valor_base * self.porcentagem) / 100
        
        if self.arquiteto and not self.beneficiario:
            self.beneficiario = self.arquiteto.nome
            
        super(Comissao, self).save(*args, **kwargs)
        
class Material(models.Model):
    """
    Catálogo de materiais disponíveis para uso nos projetos.
    """
    nome = models.CharField(max_length=255, unique=True)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome