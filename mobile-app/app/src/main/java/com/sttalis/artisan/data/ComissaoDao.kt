package com.sttalis.artisan.data
import com.sttalis.artisan.model.Comissao
import com.sttalis.artisan.api.RetrofitClient

class ComissaoDao {
    private val repo = ArtisanRepository()
    private val api = RetrofitClient.api

    suspend fun listarTodas(): List<Comissao> = repo.getComissoes()
    suspend fun listarTodos() = listarTodas()

    suspend fun inserir(c: Comissao) {
        val dados = mapOf(
            "beneficiario" to c.beneficiario,
            "valor" to c.valor,
            "data" to c.data,
            "porcentagem" to c.porcentagem,
            "valor_base" to c.valorBase,
            "descricao" to (c.descricao ?: ""),
            "recebimento" to c.recebimentoId
        )
        repo.criarComissao(dados)
    }

    suspend fun atualizar(c: Comissao) {
        val dados = mapOf(
            "beneficiario" to c.beneficiario,
            "valor" to c.valor,
            "data" to c.data,
            "porcentagem" to c.porcentagem,
            "valor_base" to c.valorBase,
            "descricao" to (c.descricao ?: ""),
            "recebimento" to c.recebimentoId
        )
        repo.atualizarComissao(c.id, dados)
    }

    suspend fun deletar(c: Comissao) { repo.deletarComissao(c.id) }
}