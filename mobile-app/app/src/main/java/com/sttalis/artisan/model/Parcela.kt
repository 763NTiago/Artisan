package com.sttalis.artisan.model
import com.google.gson.annotations.SerializedName
import java.io.Serializable


data class Parcela(
    val id: Long = 0,
    @SerializedName("cliente_nome") val clienteNome: String? = null,
    @SerializedName("projeto_nome") val projetoNome: String? = null,
    @SerializedName("num_parcela") val numParcela: Int = 0,
    @SerializedName("valor_parcela") val valorParcela: Double? = 0.0,
    @SerializedName("valor_recebido") val valorRecebido: Double? = 0.0,
    @SerializedName("data_vencimento") val dataVencimento: String? = null,
    @SerializedName("data_recebimento") val dataRecebimento: String? = null
) : Serializable