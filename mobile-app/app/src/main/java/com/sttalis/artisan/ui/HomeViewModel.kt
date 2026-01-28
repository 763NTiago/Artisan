package com.sttalis.artisan.ui

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sttalis.artisan.data.ArtisanRepository
import com.sttalis.artisan.model.DashboardFinanceiro
import com.sttalis.artisan.model.EventoDia
import kotlinx.coroutines.launch
import java.util.Date

class HomeViewModel : ViewModel() {

    private val repository = ArtisanRepository()

    private val _resumoFinanceiro = MutableLiveData<DashboardFinanceiro>()
    val resumoFinanceiro: LiveData<DashboardFinanceiro> = _resumoFinanceiro

    private val _datasEventos = MutableLiveData<List<Date>>()
    val datasEventos: LiveData<List<Date>> = _datasEventos

    private val _eventosDoDia = MutableLiveData<List<EventoDia>>()
    val eventosDoDia: LiveData<List<EventoDia>> = _eventosDoDia

    private val _proximoEvento = MutableLiveData<EventoDia?>()
    val proximoEvento: LiveData<EventoDia?> = _proximoEvento

    fun carregarDadosDashboard() {
        viewModelScope.launch {
            try {
                _resumoFinanceiro.postValue(repository.getDashData())

                _datasEventos.postValue(repository.getDashDatas())

                _proximoEvento.postValue(repository.getProximoEventoUnificado())

            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun carregarEventosDoDia(data: Date) {
        viewModelScope.launch {
            _eventosDoDia.postValue(repository.getDashEventos(data))
        }
    }
}