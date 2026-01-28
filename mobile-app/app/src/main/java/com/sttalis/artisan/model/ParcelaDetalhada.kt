package com.sttalis.artisan.model

import java.io.Serializable

data class ParcelaDetalhada(
    val id: Long = 0,
    val cliente: String = "",      
    val projeto: String = "",      
    val descricao: String = "",    
    val valorRestante: Double = 0.0,
    val valorPago: Double = 0.0,
    val dataVencimento: String? = null,
    val dataPagamento: String? = null
) : Serializable {

    fun isPaga(): Boolean = valorPago > 0 && valorRestante <= 0.01

    val nome: String get() = cliente
    val clienteNome: String get() = cliente
    val projetoNome: String get() = projeto
    val nomeParcela: String get() = descricao

    val valorParcela: Double get() = valorRestante + valorPago
    val numParcela: Int get() = try { descricao.filter { it.isDigit() }.toInt() } catch(e:Exception){0}
    val dataRecebimento: String? get() = dataPagamento
    val valorRecebido: Double get() = valorPago
}