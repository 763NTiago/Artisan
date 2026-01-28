package com.sttalis.artisan.ui.orcamento

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.gson.Gson
import com.sttalis.artisan.data.ArtisanRepository
import com.sttalis.artisan.model.Cliente
import com.sttalis.artisan.model.ItemOrcamento
import com.sttalis.artisan.model.Orcamento
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class OrcamentoViewModel : ViewModel() {

    private val repository = ArtisanRepository()

    private val _listaHistorico = MutableLiveData<List<Orcamento>>()
    val listaHistorico: LiveData<List<Orcamento>> = _listaHistorico

    private val _orcamentoEmEdicaoId = MutableLiveData<Long?>(null)
    val orcamentoEmEdicaoId: LiveData<Long?> = _orcamentoEmEdicaoId

    private val _cliente = MutableLiveData<Cliente?>()
    val cliente: LiveData<Cliente?> = _cliente

    private val _itens = MutableLiveData<MutableList<ItemOrcamento>>(mutableListOf())
    val itens: LiveData<MutableList<ItemOrcamento>> = _itens

    private val _observacoes = MutableLiveData<String>("")
    val observacoes: LiveData<String> = _observacoes

    private val _condicoesPagamento = MutableLiveData<String>("")
    val condicoesPagamento: LiveData<String> = _condicoesPagamento

    private val _statusSalvamento = MutableLiveData<StatusSalvamento>()
    val statusSalvamento: LiveData<StatusSalvamento> = _statusSalvamento

    val tabParaSelecionar = MutableLiveData<Int?>()

    init {
        carregarHistorico()
    }

    fun carregarHistorico() {
        viewModelScope.launch {
            try {
                val lista = repository.getOrcamentos()
                _listaHistorico.postValue(lista)
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun mudarAba(index: Int) {
        tabParaSelecionar.value = index
    }

    fun limparComandoAba() {
        tabParaSelecionar.value = null
    }

    fun setCliente(c: Cliente?) { _cliente.value = c }
    fun setObservacoes(t: String) { _observacoes.value = t }
    fun setCondicoesPagamento(t: String) { _condicoesPagamento.value = t }

    fun adicionarItem(item: ItemOrcamento) {
        val lista = _itens.value ?: mutableListOf()
        lista.add(item)
        _itens.value = lista
    }

    fun removerItem(item: ItemOrcamento) {
        val lista = _itens.value ?: mutableListOf()
        lista.remove(item)
        _itens.value = lista
    }

    fun getValorTotal(): Double {
        return _itens.value?.sumOf { it.valorTotal } ?: 0.0
    }

    fun carregarOrcamento(orcamento: Orcamento) {
        _orcamentoEmEdicaoId.value = orcamento.id

        val cli = Cliente(
            id = orcamento.clienteId ?: 0,
            nome = orcamento.clienteNome ?: "",
            endereco = orcamento.clienteEndereco,
            cpfCnpj = orcamento.clienteCpf,
            email = orcamento.clienteEmail,
            telefone = orcamento.clienteTelefone
        )
        _cliente.value = cli
        _itens.value = orcamento.itens.toMutableList()
        _observacoes.value = orcamento.observacoes ?: ""
        _condicoesPagamento.value = orcamento.condicoesPagamento ?: ""
    }

    fun limparEstado() {
        _orcamentoEmEdicaoId.value = null
        _cliente.value = null
        _itens.value = mutableListOf()
        _observacoes.value = ""
        _condicoesPagamento.value = ""
        _statusSalvamento.value = StatusSalvamento.Ocioso
    }

    fun salvarOrcamentoAtual() {
        val clienteAtual = _cliente.value
        val itensAtuais = _itens.value

        if (clienteAtual == null || clienteAtual.nome.isBlank()) {
            _statusSalvamento.value = StatusSalvamento.Erro("Selecione um cliente.")
            return
        }
        if (itensAtuais.isNullOrEmpty()) {
            _statusSalvamento.value = StatusSalvamento.Erro("Adicione itens ao orçamento.")
            return
        }

        _statusSalvamento.value = StatusSalvamento.Carregando

        viewModelScope.launch {
            try {
                var clienteIdFinal = clienteAtual.id
                val clienteApi = repository.criarCliente(clienteAtual.nome)
                if (clienteApi != null) {
                    clienteIdFinal = clienteApi.id
                }

                val dataHoje = SimpleDateFormat("dd/MM/yyyy", Locale("pt", "BR")).format(Date())
                val total = getValorTotal()
                val idOrcamento = _orcamentoEmEdicaoId.value ?: 0L

                val dadosMap = mapOf(
                    "cliente" to clienteIdFinal,
                    "cliente_nome" to clienteAtual.nome,
                    "cliente_endereco" to (clienteAtual.endereco ?: ""),
                    "cliente_cpf" to (clienteAtual.cpfCnpj ?: ""),
                    "cliente_email" to (clienteAtual.email ?: ""),
                    "cliente_telefone" to (clienteAtual.telefone ?: ""),
                    "data_criacao" to dataHoje,
                    "valor_total_final" to total,
                    "itens_json" to Gson().toJson(itensAtuais),
                    "observacoes" to (_observacoes.value ?: ""),
                    "condicoes_pagamento" to (_condicoesPagamento.value ?: "")
                )

                if (idOrcamento == 0L) {
                    repository.criarOrcamento(dadosMap)
                } else {
                    repository.updateOrcamento(idOrcamento, dadosMap)
                }

                carregarHistorico()
                _statusSalvamento.value = StatusSalvamento.Sucesso

            } catch (e: Exception) {
                e.printStackTrace()
                _statusSalvamento.value = StatusSalvamento.Erro("Erro ao salvar: ${e.message}")
            }
        }
    }

    fun deletarOrcamento(orcamento: Orcamento) {
        viewModelScope.launch {
            try {
                repository.deleteOrcamento(orcamento.id)
                carregarHistorico()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
}

sealed class StatusSalvamento {
    object Ocioso : StatusSalvamento()
    object Carregando : StatusSalvamento()
    object Sucesso : StatusSalvamento()
    data class Erro(val msg: String) : StatusSalvamento()
}