package com.sttalis.artisan.data
import com.sttalis.artisan.model.Cliente

class ClienteDao {
    private val repo = ArtisanRepository()
    suspend fun listarTodos(): List<Cliente> = repo.getClientes()
    suspend fun inserir(c: Cliente) { repo.criarCliente(c.nome) }

    suspend fun atualizar(c: Cliente) { repo.atualizarClienteCompleto(c) }

    suspend fun deletar(c: Cliente) {} 
    suspend fun getAll() = listarTodos() 
}