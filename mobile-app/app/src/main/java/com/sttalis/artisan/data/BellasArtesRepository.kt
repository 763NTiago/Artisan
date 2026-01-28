package com.sttalis.artisan.data

import android.util.Log
import com.sttalis.artisan.api.RetrofitClient
import com.sttalis.artisan.model.*
import java.text.SimpleDateFormat
import java.util.*

class ArtisanRepository {
    private val api = RetrofitClient.api

    private fun criarMapaSeguro(vararg pares: Pair<String, Any?>): Map<String, Any> {
        val mapa = mutableMapOf<String, Any>()
        for ((chave, valor) in pares) {
            if (valor != null) mapa[chave] = valor
        }
        return mapa
    }

    private fun getIsoFmt() = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
    private fun getBrFmt() = SimpleDateFormat("dd/MM/yyyy", Locale.getDefault())

    private fun toIso(brDate: String?): String? {
        if (brDate.isNullOrEmpty()) return null
        return try {
            val date = getBrFmt().parse(brDate)
            getIsoFmt().format(date!!)
        } catch (e: Exception) { null }
    }

    private fun toBr(isoDate: String?): String? {
        if (isoDate.isNullOrEmpty()) return null
        return try {
            val date = getIsoFmt().parse(isoDate)
            getBrFmt().format(date!!)
        } catch (e: Exception) { isoDate }
    }

    suspend fun login(user: String, pass: String): LoginResponse? {
        return try {
            val resp = api.login(LoginRequest(user, pass))
            if (resp.isSuccessful) resp.body() else null
        } catch (e: Exception) {
            Log.e("REPO", "Erro login", e)
            null
        }
    }

    suspend fun atualizarUsuario(id: Long, nome: String, email: String, pass: String?): Boolean {
        return try {
            val resp = api.atualizarUsuario(id, UserUpdate(nome, email, pass))
            resp.isSuccessful
        } catch (e: Exception) { false }
    }

    suspend fun getClientes(): List<Cliente> = try {
        api.getClientes()
    } catch(e:Exception) { emptyList() }

    suspend fun criarCliente(nome: String): Cliente? {
        return try {
            val dados = criarMapaSeguro("nome" to nome)
            api.criarCliente(dados as Map<String, String>)
        } catch(e:Exception) { null }
    }

    suspend fun atualizarClienteCompleto(c: Cliente): Boolean {
        return try { api.atualizarCliente(c.id, c).isSuccessful } catch(e:Exception) { false }
    }

    suspend fun getAgenda(): List<Agenda> {
        return try {
            api.getAgenda().map {
                it.copy(
                    dataInicio = toBr(it.dataInicio),
                    dataPrevisaoTermino = toBr(it.dataPrevisaoTermino)
                )
            }
        } catch(e:Exception) { emptyList() }
    }

    suspend fun criarAgenda(cId: Long, dIni: String, dFim: String, desc: String, valor: Double = 0.0, status: String = "Pendente") {
        try {
            val dados = criarMapaSeguro(
                "cliente" to cId,
                "descricao" to desc,
                "valor" to valor,
                "status" to status,
                "data_inicio" to toIso(dIni),
                "data_previsao_termino" to toIso(dFim)
            )
            api.criarAgenda(dados)
        } catch(e: Exception) { e.printStackTrace() }
    }

    suspend fun deleteAgenda(id: Long) {
        try { api.deletarAgenda(id) } catch(e:Exception){}
    }

    suspend fun getOrcamentos(): List<Orcamento> = try { api.getOrcamentos() } catch(e:Exception){ emptyList() }

    suspend fun criarOrcamento(map: Map<String, Any?>) {
        try {
            val dados = map.filterValues { it != null } as Map<String, Any>
            api.criarOrcamento(dados)
        } catch(e:Exception){ e.printStackTrace() }
    }

    suspend fun updateOrcamento(id: Long, map: Map<String, Any?>) {
        try {
            val dados = map.filterValues { it != null } as Map<String, Any>
            api.atualizarOrcamento(id, dados)
        } catch(e:Exception){ e.printStackTrace() }
    }

    suspend fun deleteOrcamento(id: Long) {
        try { api.deletarOrcamento(id) } catch(e:Exception){ }
    }

    suspend fun getMateriais(): List<Material> = try { api.getMateriais() } catch(e:Exception){ emptyList() }

    suspend fun criarMaterial(nome: String, desc: String) {
        try {
            val dados = criarMapaSeguro("nome" to nome, "descricao" to desc)
            api.criarMaterial(dados as Map<String, String>)
        } catch(e:Exception){ }
    }

    suspend fun atualizarMaterial(id: Long, nome: String, desc: String) {
        try {
            val dados = criarMapaSeguro("nome" to nome, "descricao" to desc)
            api.atualizarMaterial(id, dados as Map<String, String>)
        } catch(e:Exception){ }
    }

    suspend fun deletarMaterial(id: Long) {
        try { api.deletarMaterial(id) } catch(e:Exception){ }
    }

    suspend fun getRecebimentos(): List<Recebimento> {
        return try { api.getRecebimentos() } catch(e:Exception){ emptyList() }
    }

    suspend fun lancarRecebimento(dados: Map<String, Any?>) {
        try {
            val dadosLimpos = dados.filterValues { it != null } as Map<String, Any>
            val rec = api.criarRecebimento(dadosLimpos)

            val parcelas = (dados["num_parcelas"] as Int)
            val valorP = (dados["valor_parcela"] as Double)
            val d1 = dados["data_1_venc"] as String
            val cal = Calendar.getInstance()
            try { cal.time = getBrFmt().parse(d1)!! } catch(e:Exception){}

            if ((dados["valor_entrada"] as Double) > 0) {
                val hoje = getIsoFmt().format(Date())
                val dadosEntrada = criarMapaSeguro(
                    "recebimento" to rec.id,
                    "num_parcela" to 0,
                    "valor_parcela" to dados["valor_entrada"],
                    "data_vencimento" to hoje,
                    "valor_recebido" to dados["valor_entrada"],
                    "data_recebimento" to hoje
                )
                api.criarParcela(dadosEntrada)
            }

            for (i in 1..parcelas) {
                val dadosParcela = criarMapaSeguro(
                    "recebimento" to rec.id,
                    "num_parcela" to i,
                    "valor_parcela" to valorP,
                    "data_vencimento" to getIsoFmt().format(cal.time),
                    "valor_recebido" to 0.0
                )
                api.criarParcela(dadosParcela)
                cal.add(Calendar.DAY_OF_MONTH, 30)
            }
        } catch(e:Exception) { Log.e("REPO", "Erro lancar recebimento", e) }
    }

    suspend fun getParcelasDetalhadas(apenasPagas: Boolean): List<ParcelaDetalhada> {
        return try {
            val all = api.getParcelas()
            all.filter {
                val pago = it.valorRecebido ?: 0.0
                val total = it.valorParcela ?: 0.0
                val saldo = total - pago

                if (apenasPagas) {
                    pago > 0.01
                } else {
                    saldo > 0.01
                }
            }.map {
                val saldo = (it.valorParcela ?: 0.0) - (it.valorRecebido ?: 0.0)

                ParcelaDetalhada(
                    id = it.id,
                    cliente = it.clienteNome ?: "N/A",
                    projeto = it.projetoNome ?: "Geral",
                    descricao = "Parcela ${it.numParcela}",
                    valorRestante = saldo,
                    valorPago = it.valorRecebido ?: 0.0,
                    dataVencimento = toBr(it.dataVencimento),
                    dataPagamento = toBr(it.dataRecebimento)
                )
            }
        } catch(e:Exception){
            Log.e("REPO", "Erro getParcelas", e)
            emptyList()
        }
    }

    suspend fun baixarParcela(id: Long, valor: Double, data: String) {
        try {
            val isoData = toIso(data) ?: getIsoFmt().format(Date())
            val dados = criarMapaSeguro("valor_recebido" to valor, "data_recebimento" to isoData)
            Log.d("REPO", "Baixando parcela $id com valor $valor")
            api.atualizarParcela(id, dados)
        } catch(e:Exception) {
            Log.e("REPO", "Erro baixarParcela", e)
        }
    }

    suspend fun getArquitetos(): List<Arquiteto> = try { api.getArquitetos() } catch(e:Exception){ emptyList() }


    suspend fun criarArquiteto(dados: Map<String, Any?>) {
        try {
            val novoMap = dados.toMutableMap()

            if (novoMap["data_pagamento"] is String) {
                novoMap["data_pagamento"] = toIso(novoMap["data_pagamento"] as String)
            }

            val mapFinal = novoMap.filterValues { it != null } as Map<String, Any>
            api.criarArquiteto(mapFinal)
        } catch(e:Exception){ Log.e("REPO", "Erro criar Arquiteto", e) }
    }

    suspend fun criarArquitetoMap(dados: Map<String, Any?>) = criarArquiteto(dados)

    suspend fun atualizarArquiteto(id: Long, dados: Map<String, Any?>) {
        try {
            val mutavel = dados.toMutableMap()
            if (mutavel.containsKey("data_pagamento")) {
                val iso = toIso(mutavel["data_pagamento"] as? String)
                if(iso != null) mutavel["data_pagamento"] = iso else mutavel.remove("data_pagamento")
            }
            val dadosLimpos = mutavel.filterValues{it!=null} as Map<String, Any>
            api.atualizarArquiteto(id, dadosLimpos)
        } catch(e:Exception) { Log.e("REPO", "Erro atualizar Arquiteto", e) }
    }

    suspend fun deletarArquiteto(id: Long) { try { api.deletarArquiteto(id) } catch(e:Exception){} }

    suspend fun getComissoes(): List<Comissao> {
        return try {
            api.getComissoes().map { it.copy(data = toBr(it.data)) }
        } catch(e:Exception) { emptyList() }
    }

    suspend fun criarComissao(map: Map<String, Any?>) {
        try {
            val novoMap = map.toMutableMap()
            if(novoMap["data"] != null) novoMap["data"] = toIso(novoMap["data"] as String)
            val dados = novoMap.filterValues{it!=null} as Map<String, Any>
            api.criarComissao(dados)
        } catch(e:Exception) { Log.e("REPO", "Erro criar Comissao", e) }
    }

    suspend fun atualizarComissao(id: Long, map: Map<String, Any?>) {
        try {
            val novoMap = map.toMutableMap()
            if(novoMap["data"] != null) novoMap["data"] = toIso(novoMap["data"] as String)
            val dados = novoMap.filterValues{it!=null} as Map<String, Any>
            api.atualizarComissao(id, dados)
        } catch(e:Exception) { Log.e("REPO", "Erro atualizar Comissao", e) }
    }

    suspend fun deletarComissao(id: Long) { try { api.deletarComissao(id) } catch(e:Exception){} }

    suspend fun getDashData(): DashboardFinanceiro = try { api.getResumoFinanceiro() } catch(e:Exception) { DashboardFinanceiro() }

    suspend fun getDashDatas(): List<Date> {
        return try {
            api.getDatasAgenda().mapNotNull {
                try { getIsoFmt().parse(it) } catch(e:Exception){null}
            }
        } catch(e:Exception){ emptyList() }
    }

    suspend fun getDashEventos(d: Date): List<EventoDia> = try { api.getEventosDoDia(getIsoFmt().format(d)) } catch(e:Exception){ emptyList() }

    suspend fun getProximoEventoUnificado(): EventoDia? {
        return try {
            api.getEventosDoDia(null).firstOrNull()
        } catch(e:Exception){ null }
    }

    suspend fun getRelatorioCompleto(): List<RelatorioItem> {
        return try {
            api.getRelatorioCompleto()
        } catch (e: Exception) {
            e.printStackTrace()
            emptyList()
        }
    }
}