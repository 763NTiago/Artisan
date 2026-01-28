package com.sttalis.artisan.model
import com.google.gson.annotations.SerializedName
import java.io.Serializable

data class Cliente(
    val id: Long = 0,
    val nome: String = "",
    val telefone: String? = "",
    val email: String? = "",
    val endereco: String? = "",
    @SerializedName("cpf_cnpj") val cpfCnpj: String? = ""
) : Serializable {
    override fun toString() = nome

    val cpf_cnpj: String? get() = cpfCnpj
}