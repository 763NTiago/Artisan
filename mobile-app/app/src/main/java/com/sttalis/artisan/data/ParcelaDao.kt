package com.sttalis.artisan.data
import com.sttalis.artisan.model.ParcelaDetalhada

class ParcelaDao {
    private val repo = ArtisanRepository()
    suspend fun listarTodas() = repo.getParcelasDetalhadas(false)
    suspend fun getPendentesDetalhadas() = repo.getParcelasDetalhadas(false)
    suspend fun getHistoricoDetalhado() = repo.getParcelasDetalhadas(true)
    suspend fun baixar(id: Long, valor: Double, data: String) = repo.baixarParcela(id, valor, data)
    suspend fun getById(id: Long): ParcelaDetalhada? = null
}