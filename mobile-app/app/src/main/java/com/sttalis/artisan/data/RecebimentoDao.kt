package com.sttalis.artisan.data
import com.sttalis.artisan.model.Recebimento

class RecebimentoDao {
    private val repo = ArtisanRepository()
    suspend fun listarTodos() = repo.getRecebimentos() 
    suspend fun getById(id: Long): Recebimento? = null

    suspend fun insert(
        clienteId: Long, agendaId: Long?, tipoPagamento: String, valorTotal: Double,
        valorEntrada: Double, numParcelas: Int, valorParcela: Double, dataPrimeiroVenc: String
    ) {
        repo.lancarRecebimento(mapOf(
            "cliente" to clienteId, "agenda" to agendaId, "tipo_pagamento" to tipoPagamento,
            "valor_total" to valorTotal, "valor_entrada" to valorEntrada, "num_parcelas" to numParcelas,
            "valor_parcela" to valorParcela, "data_1_venc" to dataPrimeiroVenc
        ))
    }

    suspend fun update(id: Long, valorRecebido: Double, dataRecebimento: String) {
        repo.baixarParcela(id, valorRecebido, dataRecebimento)
    }
}