package com.sttalis.artisan.data
import com.sttalis.artisan.model.Arquiteto

class ArquitetoDao {
    private val repo = ArtisanRepository()

    suspend fun getAll() = repo.getArquitetos()

    suspend fun insert(a: Arquiteto) {

        val dados = mapOf(
            "nome" to a.nome,
            "data_pagamento" to (a.dataPagamento ?: ""),
            "porcentagem_padrao" to a.porcentagemPadrao
        )
        repo.criarArquiteto(dados)
    }

    suspend fun delete(a: Arquiteto) { repo.deletarArquiteto(a.id) }
}