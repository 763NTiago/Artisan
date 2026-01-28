package com.sttalis.artisan.ui.comissao

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.sttalis.artisan.data.ArtisanRepository
import com.sttalis.artisan.model.*
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

class ComissoesViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = ArtisanRepository()

    private val _listaArquitetos = MutableLiveData<List<Arquiteto>>()
    val listaArquitetos: LiveData<List<Arquiteto>> = _listaArquitetos

    private val _listaRecebimentos = MutableLiveData<List<Recebimento>>()
    val listaRecebimentos: LiveData<List<Recebimento>> = _listaRecebimentos

    private val _listaComissoesPendentes = MutableLiveData<List<Comissao>>()
    val listaComissoesPendentes: LiveData<List<Comissao>> = _listaComissoesPendentes

    private val _listaComissoesPagas = MutableLiveData<List<Comissao>>()
    val listaComissoesPagas: LiveData<List<Comissao>> = _listaComissoesPagas

    val listaClientes = MutableLiveData<List<Cliente>>()
    val listaAgenda = MutableLiveData<List<Agenda>>()

    init {
        carregarDados()
    }

    fun carregarDados() {
        viewModelScope.launch {
            try {
                _listaArquitetos.postValue(repository.getArquitetos())
                _listaRecebimentos.postValue(repository.getRecebimentos())
                listaClientes.postValue(repository.getClientes())
                listaAgenda.postValue(repository.getAgenda())

                val todasComissoes = repository.getComissoes()

                _listaComissoesPendentes.postValue(todasComissoes.filter { it.status == "Pendente" })
                _listaComissoesPagas.postValue(todasComissoes.filter { it.status == "Pago" })
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun calcularDataSugerida(arquiteto: Arquiteto): String {
        val c = Calendar.getInstance()
        c.add(Calendar.MONTH, 1)
        val maxDay = c.getActualMaximum(Calendar.DAY_OF_MONTH)

        val diaPref = if (arquiteto.diaPagamentoPreferencial > 0) arquiteto.diaPagamentoPreferencial else 10
        val diaFinal = if (diaPref > maxDay) maxDay else diaPref

        c.set(Calendar.DAY_OF_MONTH, diaFinal)
        return SimpleDateFormat("dd/MM/yyyy", Locale("pt", "BR")).format(c.time)
    }

    fun salvarArquiteto(nome: String, dia: Int, pct: Double) {
        viewModelScope.launch {
            val c = Calendar.getInstance()
            c.set(Calendar.DAY_OF_MONTH, dia)
            val dataFormatada = SimpleDateFormat("yyyy-MM-dd", Locale.US).format(c.time)

            val mapa = mapOf(
                "nome" to nome,
                "data_pagamento" to dataFormatada,
                "porcentagem_padrao" to pct
            )

            repository.criarArquitetoMap(mapa)
            carregarDados()
        }
    }

    fun deletarArquiteto(arquiteto: Arquiteto) {
        viewModelScope.launch {
            repository.deletarArquiteto(arquiteto.id)
            carregarDados()
        }
    }

    fun salvarComissao(arq: Arquiteto, rec: Recebimento, nomeDisplay: String, base: Double, pct: Double, data: String) {
        val valorCalculado = base * (pct / 100.0)

        val mapa = mapOf(
            "recebimento" to rec.id,
            "cliente" to (rec.clienteId ?: 0),
            "beneficiario" to arq.nome,
            "descricao" to nomeDisplay,
            "valor_base" to base,
            "porcentagem" to pct,
            "valor" to valorCalculado,
            "data" to data
        )

        viewModelScope.launch {
            repository.criarComissao(mapa)
            carregarDados()
        }
    }

    fun pagarComissao(c: Comissao) {
        viewModelScope.launch {
            val hoje = SimpleDateFormat("dd/MM/yyyy", Locale("pt", "BR")).format(Date())

            val mapaCompleto = mapOf(
                "data" to hoje,
                "beneficiario" to (c.beneficiario ?: ""),
                "valor" to c.valor,
                "recebimento" to (c.recebimentoId ?: "")
            )

            repository.atualizarComissao(c.id, mapaCompleto)
            carregarDados()
        }
    }

    fun deletarComissao(c: Comissao) {
        viewModelScope.launch {
            repository.deletarComissao(c.id)
            carregarDados()
        }
    }
}