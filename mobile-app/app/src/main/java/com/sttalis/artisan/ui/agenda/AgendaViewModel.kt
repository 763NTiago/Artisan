package com.sttalis.artisan.ui.agenda

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.sttalis.artisan.data.AppDatabase
import com.sttalis.artisan.model.Agenda
import com.sttalis.artisan.model.Cliente
import com.sttalis.artisan.model.Orcamento
import kotlinx.coroutines.launch

class AgendaViewModel(application: Application) : AndroidViewModel(application) {
    private val db = AppDatabase.getDatabase(application)

    private val _listaAgenda = MutableLiveData<List<Agenda>>()
    val listaAgenda: LiveData<List<Agenda>> = _listaAgenda

    private val _listaClientes = MutableLiveData<List<Cliente>>()
    val listaClientes: LiveData<List<Cliente>> = _listaClientes

    private val _listaOrcamentos = MutableLiveData<List<Orcamento>>()
    val listaOrcamentos: LiveData<List<Orcamento>> = _listaOrcamentos

    init {
        carregarDados()
    }

    fun carregarDados() {
        viewModelScope.launch {
            _listaAgenda.postValue(db.agendaDao().listarTodos())
            _listaClientes.postValue(db.clienteDao().listarTodos())
            _listaOrcamentos.postValue(db.orcamentoDao().listarTodos())
        }
    }

    fun filtrarTodos() = carregarDados()
    fun filtrarHoje() { /* Implementar filtro local ou API */ }
    fun filtrarSemana() { /* Implementar filtro local ou API */ }
    fun filtrarMes() { /* Implementar filtro local ou API */ }

    fun salvarProjeto(agenda: Agenda) {
        viewModelScope.launch {
            db.agendaDao().inserir(agenda)
            carregarDados()
        }
    }

    fun deletarProjeto(agenda: Agenda) {
        viewModelScope.launch {
            db.agendaDao().deletar(agenda)
            carregarDados()
        }
    }

    suspend fun criarClienteRapido(nome: String): Long {
        db.clienteDao().inserir(Cliente(nome = nome))
        val clientes = db.clienteDao().listarTodos()
        return clientes.find { it.nome == nome }?.id ?: 0L
    }
}