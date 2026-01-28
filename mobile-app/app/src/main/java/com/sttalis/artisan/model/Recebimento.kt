package com.sttalis.artisan.model
import com.google.gson.annotations.SerializedName
import java.io.Serializable

data class Recebimento(
    val id: Long = 0,
    @SerializedName("cliente") val clienteId: Long? = 0, 
    @SerializedName("cliente_nome") val clienteNome: String? = null,
    @SerializedName("agenda") val agendaId: Long? = null, 
    val valor_total: Double? = 0.0,
    val tipo_pagamento: String? = "",
    val valor_entrada: Double? = 0.0,
    val num_parcelas: Int = 0,
    @SerializedName("data_1_venc") val dataPrimeiroVenc: String? = ""
) : Serializable {
    val valorTotal: Double get() = valor_total ?: 0.0
    val valorEntrada: Double get() = valor_entrada ?: 0.0
    val tipoPagamento: String get() = tipo_pagamento ?: ""
    val numParcelas: Int get() = num_parcelas
}