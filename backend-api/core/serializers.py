from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Cliente, Material, Arquiteto, Agenda, Orcamento, Recebimento, Parcela, Comissao

class UserSerializer(serializers.ModelSerializer):
    """Serializador para gestão de usuários do sistema."""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True, 'required': False}}

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

class ArquitetoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arquiteto
        fields = '__all__'

class AgendaSerializer(serializers.ModelSerializer):
    # Campos calculados para facilitar a exibição no Frontend
    cliente_nome = serializers.SerializerMethodField()
    nome = serializers.SerializerMethodField()
    
    class Meta:
        model = Agenda
        fields = '__all__'

    def get_cliente_nome(self, obj):
        return obj.cliente.nome if obj.cliente else "Cliente N/A"

    def get_nome(self, obj):
        return self.get_cliente_nome(obj)

class OrcamentoSerializer(serializers.ModelSerializer):
    projeto_nome = serializers.SerializerMethodField()

    class Meta:
        model = Orcamento
        fields = '__all__'

    def get_projeto_nome(self, obj):
        return obj.agenda.descricao if obj.agenda else "Sem Projeto Vinculado"

class RecebimentoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.SerializerMethodField()
    nome = serializers.SerializerMethodField()
    projeto_nome = serializers.SerializerMethodField()
    
    class Meta:
        model = Recebimento
        fields = '__all__'

    def get_cliente_nome(self, obj):
        return obj.cliente.nome if obj.cliente else "Cliente N/A"
    
    def get_nome(self, obj):
        return self.get_cliente_nome(obj)
    
    def get_projeto_nome(self, obj):
        return obj.agenda.descricao if obj.agenda else "Projeto Geral"

class ParcelaSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.SerializerMethodField()
    nome = serializers.SerializerMethodField() 
    projeto_nome = serializers.SerializerMethodField()
    nome_parcela = serializers.SerializerMethodField()

    class Meta:
        model = Parcela
        fields = '__all__'

    def get_cliente_nome(self, obj):
        if obj.recebimento and obj.recebimento.cliente:
            return obj.recebimento.cliente.nome
        return "Cliente N/A"

    def get_nome(self, obj): 
        return self.get_cliente_nome(obj)

    def get_projeto_nome(self, obj):
        if obj.recebimento and obj.recebimento.agenda:
            return obj.recebimento.agenda.descricao
        return "Geral"

    def get_nome_parcela(self, obj):
        if obj.num_parcela == 0:
            return "Entrada"
        return f"Parcela {obj.num_parcela}"

class ComissaoSerializer(serializers.ModelSerializer):
    recebimento = serializers.PrimaryKeyRelatedField(queryset=Recebimento.objects.all(), required=False, allow_null=True)
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all(), required=False, allow_null=True)
    arquiteto = serializers.PrimaryKeyRelatedField(queryset=Arquiteto.objects.all(), required=False, allow_null=True)

    cliente_nome = serializers.SerializerMethodField()
    nome = serializers.SerializerMethodField()
    projeto_nome = serializers.SerializerMethodField()
    
    class Meta:
        model = Comissao
        fields = '__all__'

    def get_cliente_nome(self, obj):
        return obj.cliente.nome if obj.cliente else "N/A"

    def get_nome(self, obj):
        return self.get_cliente_nome(obj)

    def get_projeto_nome(self, obj):
        # Tenta pegar o nome do projeto via relacionamento ou descrição
        if obj.recebimento and obj.recebimento.agenda:
            return obj.recebimento.agenda.descricao
        
        # Fallback: tenta extrair da string de descrição (ex: "Comissão de Projeto X")
        if obj.descricao and " de " in obj.descricao:
            try:
                return obj.descricao.split(" de ", 1)[1]
            except IndexError:
                pass
        return obj.descricao or "Sem Projeto"