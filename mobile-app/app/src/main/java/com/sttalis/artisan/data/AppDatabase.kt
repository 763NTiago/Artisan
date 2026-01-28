package com.sttalis.artisan.data
import android.content.Context

class AppDatabase private constructor() {
    companion object {
        @Volatile private var INSTANCE: AppDatabase? = null
        fun getInstance(context: Context): AppDatabase = INSTANCE ?: synchronized(this){ INSTANCE = AppDatabase(); INSTANCE!! }
        fun getDatabase(context: Context): AppDatabase = getInstance(context)
    }
    fun clienteDao() = ClienteDao()
    fun agendaDao() = AgendaDao()
    fun orcamentoDao() = OrcamentoDao()
    fun recebimentoDao() = RecebimentoDao()
    fun comissaoDao() = ComissaoDao()
    fun materialDao() = MaterialDao()
    fun arquitetoDao() = ArquitetoDao()
    fun parcelaDao() = ParcelaDao()
    fun relatorioDao() = RelatorioDao()
}