package com.sttalis.artisan.data
import com.sttalis.artisan.model.Agenda

class AgendaDao {
    private val repo = ArtisanRepository()

    suspend fun listarTodos(): List<Agenda> = repo.getAgenda()

    suspend fun inserir(a: Agenda) {
        repo.criarAgenda(
            cId = a.clienteId ?: 0,
            dIni = a.dataInicio ?: "",
            dFim = a.dataPrevisaoTermino ?: "",
            desc = a.descricao ?: "",
            valor = a.valorFinal,
            status = a.status ?: "Pendente"
        )
    }

    suspend fun atualizar(a: Agenda) { inserir(a) }

    suspend fun deletar(a: Agenda) { repo.deleteAgenda(a.id) }
}