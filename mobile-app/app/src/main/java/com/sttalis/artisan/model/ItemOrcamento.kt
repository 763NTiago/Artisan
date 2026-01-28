package com.sttalis.artisan.model

import com.google.gson.annotations.SerializedName
import java.io.Serializable

data class ItemOrcamento(
    val id: Long = System.currentTimeMillis(),

    @SerializedName("quantidade", alternate = ["qtd"])
    val _quantidade: Any? = null,

    val ambiente: String = "",

    @SerializedName("descricao", alternate = ["desc"])
    val descricao: String = "",

    @SerializedName("unidade")
    val unidade: String = "UN",

    @SerializedName("valor_unitario", alternate = ["valor_unit", "valorUnitario"])
    val _valorUnitario: Any? = null,

    @SerializedName("valor_total", alternate = ["valorTotal"])
    val _valorTotal: Any? = null
) : Serializable {

    val quantidade: Double
        get() = parseToDouble(_quantidade)

    val valorUnitario: Double
        get() = parseToDouble(_valorUnitario)

    val valorTotal: Double
        get() = parseToDouble(_valorTotal)

    private fun parseToDouble(value: Any?): Double {
        if (value == null) return 0.0
        return try {
            when (value) {
                is Number -> value.toDouble()
                is String -> {
                    var texto = value.toString()
                    texto = texto.replace("R$", "")
                        .replace("\\s".toRegex(), "")
                        .replace("\u00A0", "")

                    if (texto.contains(",")) {
                        texto = texto.replace(".", "")
                        texto = texto.replace(",", ".")
                    }
                    texto.toDoubleOrNull() ?: 0.0
                }
                else -> 0.0
            }
        } catch (e: Exception) { 0.0 }
    }
}