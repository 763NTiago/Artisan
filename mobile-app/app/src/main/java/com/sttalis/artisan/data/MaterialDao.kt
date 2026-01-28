package com.sttalis.artisan.data
import com.sttalis.artisan.model.Material

class MaterialDao {
    private val repo = ArtisanRepository()
    suspend fun listarTodos() = repo.getMateriais()
    suspend fun inserir(m: Material) { repo.criarMaterial(m.nome, m.descricao?:"") }
    suspend fun atualizar(m: Material) { inserir(m) }
    suspend fun deletar(m: Material) { repo.deletarMaterial(m.id) }
}