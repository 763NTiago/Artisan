package com.sttalis.artisan.model
import java.io.Serializable

data class Material(
    val id: Long = 0,
    val nome: String = "",
    val descricao: String? = "",
    val precoUnitario: Double = 0.0,
    val unidade: String = "un"
) : Serializable