package com.sttalis.artisan.data
import com.sttalis.artisan.model.RelatorioItem

class RelatorioDao {
    private val repo = ArtisanRepository()

    suspend fun getRelatorioCompleto(): List<RelatorioItem> {
        return repo.getRelatorioCompleto()
    }
}