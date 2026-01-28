package com.sttalis.artisan.ui.relatorios

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.sttalis.artisan.data.RelatorioDao
import com.sttalis.artisan.model.RelatorioItem
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Locale

class RelatoriosViewModel(application: Application) : AndroidViewModel(application) {

    private val relatorioDao = RelatorioDao()
    private var listaCompleta: List<RelatorioItem> = emptyList()

    private val _relatorioProcessado = MutableLiveData<List<RelatorioItem>>()
    val relatorioProcessado: LiveData<List<RelatorioItem>> = _relatorioProcessado

    val listaClientes = MutableLiveData<List<String>>()
    val listaProjetos = MutableLiveData<List<String>>()
    val listaArquitetos = MutableLiveData<List<String>>()

    val filtroCliente = MutableLiveData<String?>()
    val filtroProjeto = MutableLiveData<String?>()
    val filtroArquiteto = MutableLiveData<String?>()
    val filtroDataInicio = MutableLiveData<String?>()
    val filtroDataFim = MutableLiveData<String?>()

    init {
        carregarRelatorio()
    }

    fun carregarRelatorio() {
        viewModelScope.launch {
            try {
                listaCompleta = relatorioDao.getRelatorioCompleto()
                preencherFiltrosDinamicos()
                aplicarFiltros()
            } catch (e: Exception) {
                e.printStackTrace()
                _relatorioProcessado.postValue(emptyList())
            }
        }
    }

    private fun preencherFiltrosDinamicos() {
        val clientes = listaCompleta.map { it.cliente }.distinct().filter { it.isNotEmpty() }.sorted()
        listaClientes.postValue(listOf("Todos") + clientes)

        val projetos = listaCompleta.map { it.projeto }.distinct().filter { it.isNotEmpty() }.sorted()
        listaProjetos.postValue(listOf("Todos") + projetos)

        val arquitetos = listaCompleta.mapNotNull { it.arquiteto }.distinct().filter { it.isNotEmpty() }.sorted()
        listaArquitetos.postValue(listOf("Todos") + arquitetos)
    }

    fun aplicarFiltros() {
        var lista = listaCompleta
        val sdfBr = SimpleDateFormat("dd/MM/yyyy", Locale("pt", "BR"))
        val sdfIso = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())

        val cli = filtroCliente.value
        if (!cli.isNullOrEmpty() && cli != "Todos") {
            lista = lista.filter { it.cliente.equals(cli, ignoreCase = true) }
        }

        val proj = filtroProjeto.value
        if (!proj.isNullOrEmpty() && proj != "Todos") {
            lista = lista.filter { it.projeto.equals(proj, ignoreCase = true) }
        }

        val arq = filtroArquiteto.value
        if (!arq.isNullOrEmpty() && arq != "Todos") {
            lista = lista.filter { (it.arquiteto ?: "").equals(arq, ignoreCase = true) }
        }

        val iniStr = filtroDataInicio.value
        val fimStr = filtroDataFim.value

        if (!iniStr.isNullOrEmpty() && !fimStr.isNullOrEmpty()) {
            try {
                val dtIniFiltro = sdfBr.parse(iniStr)
                val dtFimFiltro = sdfBr.parse(fimStr)

                if (dtIniFiltro != null && dtFimFiltro != null) {
                    lista = lista.filter { item ->
                        val dataItemStr = item.dataInicio ?: item.dataTermino

                        if (dataItemStr.isNullOrEmpty()) {
                            false
                        } else {
                            val dataRef = try {
                                if (dataItemStr.contains("-")) sdfIso.parse(dataItemStr)
                                else sdfBr.parse(dataItemStr)
                            } catch (e: Exception) {
                                null
                            }

                            if (dataRef != null) {
                                !dataRef.before(dtIniFiltro) && !dataRef.after(dtFimFiltro)
                            } else {
                                false
                            }
                        }
                    }
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }

        _relatorioProcessado.postValue(lista)
    }
}