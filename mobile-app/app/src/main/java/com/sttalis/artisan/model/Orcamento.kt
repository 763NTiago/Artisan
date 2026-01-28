package com.sttalis.artisan.model

import com.google.gson.Gson
import com.google.gson.annotations.SerializedName
import com.google.gson.reflect.TypeToken
import java.io.Serializable

data class Orcamento(
    val id: Long = 0,
    @SerializedName("cliente_nome") val clienteNome: String? = "",
    @SerializedName("data_criacao") val dataCriacao: String? = null,
    @SerializedName("valor_total_final") private val _valorTotalFinal: Any? = null,
    @SerializedName("itens_json") val itensJson: String? = "[]",
    @SerializedName("condicoes_pagamento") val condicoesPagamentoAPI: String? = "",
    val observacoes: String? = "",
    @SerializedName("cliente") val clienteId: Long? = 0,
    @SerializedName("cliente_endereco") val clienteEndereco: String? = "",
    @SerializedName("cliente_cpf") val clienteCpf: String? = "",
    @SerializedName("cliente_email") val clienteEmail: String? = "",
    @SerializedName("cliente_telefone") val clienteTelefone: String? = ""
) : Serializable {

    val valorTotalFinal: Double
        get() {
            return try {
                when (_valorTotalFinal) {
                    is Number -> _valorTotalFinal.toDouble()
                    is String -> {
                        val texto = _valorTotalFinal.toString()
                        if (texto.contains(",")) {
                            val limpo = texto.replace("R$", "")
                                .replace(" ", "")
                                .replace(".", "")
                                .replace(",", ".")
                            limpo.toDoubleOrNull() ?: 0.0
                        } else {
                            val limpo = texto.replace("R$", "")
                                .replace(" ", "")
                            limpo.toDoubleOrNull() ?: 0.0
                        }
                    }
                    else -> 0.0
                }
            } catch (e: Exception) {
                0.0
            }
        }

    val itens: List<ItemOrcamento>
        get() {
            return try {
                if (itensJson.isNullOrEmpty()) return emptyList()
                val tipo = object : TypeToken<List<ItemOrcamento>>() {}.type
                Gson().fromJson(itensJson, tipo)
            } catch (e: Exception) {
                emptyList()
            }
        }

    val condicoesPagamento: String get() = condicoesPagamentoAPI ?: ""
    val cpfCnpj: String get() = clienteCpf ?: ""
}