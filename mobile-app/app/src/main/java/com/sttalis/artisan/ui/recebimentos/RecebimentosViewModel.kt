package com.sttalis.artisan.ui.recebimentos

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.sttalis.artisan.data.ArtisanRepository
import com.sttalis.artisan.model.Agenda
import com.sttalis.artisan.model.ParcelaDetalhada
import kotlinx.coroutines.launch

class RecebimentosViewModel(application: Application) : AndroidViewModel(application) {
    private val repository = ArtisanRepository()

    private val _listaPendentes = MutableLiveData<List<ParcelaDetalhada>>()
    val listaPendentes: LiveData<List<ParcelaDetalhada>> = _listaPendentes

    private val _listaHistorico = MutableLiveData<List<ParcelaDetalhada>>()
    val listaHistorico: LiveData<List<ParcelaDetalhada>> = _listaHistorico

    private val _listaAgenda = MutableLiveData<List<Agenda>>()
    val listaAgenda: LiveData<List<Agenda>> = _listaAgenda

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    fun carregarDados() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val pendentes = repository.getParcelasDetalhadas(apenasPagas = false)
                _listaPendentes.postValue(pendentes)

                val historico = repository.getParcelasDetalhadas(apenasPagas = true)
                _listaHistorico.postValue(historico)

                val agenda = repository.getAgenda()
                _listaAgenda.postValue(agenda)
            } catch (e: Exception) {
                e.printStackTrace()
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun realizarBaixa(parcela: ParcelaDetalhada, valorPagoAgora: Double, dataPagamento: String) {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val novoTotalAcumulado = parcela.valorPago + valorPagoAgora
                repository.baixarParcela(parcela.id, novoTotalAcumulado, dataPagamento)
                carregarDados()
            } catch (e: Exception) {
                e.printStackTrace()
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun salvarNovoLancamento(
        cliente: Any?, agenda: Agenda?, valorTotal: Double, tipoPagamento: String,
        entrada: Double, numParcelas: Int, dataPrimeiroVenc: String
    ) {
        if (agenda == null) return
        viewModelScope.launch {
            try {
                val valorParcelado = valorTotal - entrada
                val valorPorParcela = if (numParcelas > 0) valorParcelado / numParcelas else 0.0

                val dados = mapOf(
                    "cliente" to agenda.clienteId,
                    "agenda" to agenda.id,
                    "tipo_pagamento" to tipoPagamento,
                    "valor_total" to valorTotal,
                    "valor_entrada" to entrada,
                    "num_parcelas" to numParcelas,
                    "valor_parcela" to valorPorParcela,
                    "data_1_venc" to dataPrimeiroVenc
                )
                repository.lancarRecebimento(dados)
                carregarDados()
            } catch (e: Exception) { e.printStackTrace() }
        }
    }
}