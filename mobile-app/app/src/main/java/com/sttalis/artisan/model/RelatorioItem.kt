package com.sttalis.artisan.model

import com.google.gson.annotations.SerializedName
import java.io.Serializable

data class RelatorioItem(
    val id: Long = 0,
    @SerializedName("cliente") val cliente: String = "",
    @SerializedName("projeto") val projeto: String = "",
    @SerializedName("arquiteto") val arquiteto: String? = "",
    @SerializedName("data_inicio") val dataInicio: String? = null,
    @SerializedName("data") val dataTermino: String? = null,
    @SerializedName("total_projeto") val totalProjeto: Double = 0.0,
    @SerializedName("total_comissao") val comissao: Double = 0.0,
    @SerializedName("valor_pago_cliente") val valorPago: Double = 0.0,
    @SerializedName("a_receber") val aReceber: Double = 0.0,
    @SerializedName("sobrou_liquido") val lucro: Double = 0.0
) : Serializable {
    val isQuitado: Boolean get() = aReceber <= 0.01
}