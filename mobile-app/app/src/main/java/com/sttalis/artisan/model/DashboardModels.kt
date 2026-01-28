package com.sttalis.artisan.model

import com.google.gson.annotations.SerializedName
import java.io.Serializable

data class DashboardFinanceiro(
    @SerializedName("total_a_receber") val totalAReceber: Double = 0.0,
    @SerializedName("total_a_receber_30d") val totalAReceber30d: Double = 0.0,
    @SerializedName("total_recebido_geral") val totalRecebidoGeral: Double = 0.0,
    @SerializedName("total_comissoes_ja_pagas") val totalComissoesPagas: Double = 0.0,
    @SerializedName("total_comissoes_pendentes") val totalComissoesPendentes: Double = 0.0,
    @SerializedName("ativos") val projetosAtivos: Int = 0
) : Serializable

data class EventoDia(
    val tipo: String = "",
    val cliente: String = "",
    val descricao: String = "",
    val valor: Double = 0.0,

    val data: String? = ""
) : Serializable