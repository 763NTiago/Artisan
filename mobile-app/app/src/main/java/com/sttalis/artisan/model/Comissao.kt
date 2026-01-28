package com.sttalis.artisan.model
import com.google.gson.annotations.SerializedName
import java.io.Serializable
import java.text.SimpleDateFormat
import java.util.*

data class Comissao(
    val id: Long = 0,
    val data: String? = null, 
    @SerializedName("cliente_nome") val clienteNome: String? = null,
    @SerializedName("projeto_nome") val projetoNome: String? = null,
    val beneficiario: String? = "",
    val descricao: String? = "",
    val valor: Double = 0.0,
    val porcentagem: Double = 0.0,
    @SerializedName("valor_base") val valorBase: Double = 0.0,
    @SerializedName("recebimento") val recebimentoId: Long? = null
) : Serializable {

    val arquitetoNome: String get() = beneficiario ?: ""
    val valorComissao: Double get() = valor
    val dataPrevisao: String? get() = data

    val status: String get() {
        if (data.isNullOrEmpty()) return "Pendente"

        return try {
            val sdf = SimpleDateFormat("dd/MM/yyyy", Locale("pt", "BR"))
            val dataComissao = sdf.parse(data)

            val hojeCal = Calendar.getInstance()
            hojeCal.set(Calendar.HOUR_OF_DAY, 0)
            hojeCal.set(Calendar.MINUTE, 0)
            hojeCal.set(Calendar.SECOND, 0)
            hojeCal.set(Calendar.MILLISECOND, 0)
            val hoje = hojeCal.time

            if (dataComissao != null && (dataComissao.before(hoje) || dataComissao.equals(hoje))) {
                "Pago"
            } else {
                "Pendente"
            }
        } catch (e: Exception) {
            "Pendente"
        }
    }
}