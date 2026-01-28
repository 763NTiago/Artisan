package com.sttalis.artisan.model
import com.google.gson.annotations.SerializedName
import java.io.Serializable

data class Agenda(
    val id: Long = 0,
    @SerializedName("cliente") val clienteId: Long? = null,
    @SerializedName("cliente_nome") val clienteNome: String? = null,
    @SerializedName("data_inicio") val dataInicio: String? = null,
    @SerializedName("data_previsao_termino") val dataPrevisaoTermino: String? = null,
    val descricao: String? = "",

    val valor: Double? = 0.0,
    val status: String? = "Pendente"
) : Serializable {
    val dataEntrega: String? get() = dataPrevisaoTermino
    val valorFinal: Double get() = valor ?: 0.0
}