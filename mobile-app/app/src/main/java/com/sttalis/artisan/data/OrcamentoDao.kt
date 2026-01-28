package com.sttalis.artisan.data
import com.sttalis.artisan.model.Orcamento
import com.google.gson.Gson

class OrcamentoDao {
    private val repo = ArtisanRepository()

    suspend fun listarTodos() = repo.getOrcamentos()

    suspend fun inserir(o: Orcamento) {
        val map = mapOf(
            "cliente_nome" to o.clienteNome,
            "cliente_endereco" to o.clienteEndereco,
            "cliente_cpf" to o.clienteCpf,
            "cliente_email" to o.clienteEmail,
            "cliente_telefone" to o.clienteTelefone,
            "itens_json" to Gson().toJson(o.itens),
            "valor_total_final" to o.valorTotalFinal,
            "observacoes_brutas" to o.observacoes,
            "condicoes_pagamento" to o.condicoesPagamento,
            "data_criacao" to o.dataCriacao
        )

        if (o.id == 0L) {
            repo.criarOrcamento(map)
        } else {
            repo.updateOrcamento(o.id, map)
        }
    }

    suspend fun atualizar(o: Orcamento) { inserir(o) }

    suspend fun deletar(o: Orcamento) {
        repo.deleteOrcamento(o.id)
    }
}