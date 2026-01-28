package com.sttalis.artisan.model

import com.google.gson.annotations.SerializedName
import java.io.Serializable

data class Arquiteto(
    val id: Long = 0,
    val nome: String,
    @SerializedName("data_pagamento") val dataPagamento: String? = null,
    @SerializedName("porcentagem_padrao") val porcentagemPadrao: Double = 0.0
) : Serializable {

    val diaPagamentoPreferencial: Int get() {
        return if (!dataPagamento.isNullOrEmpty()) {
            try {
                val parts = dataPagamento.split("-")
                if (parts.size == 3) parts[2].toInt() else 10
            } catch (e: Exception) { 10 }
        } else {
            10
        }
    }
}