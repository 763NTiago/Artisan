package com.sttalis.artisan.ui.orcamento.tabs

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sttalis.artisan.data.ArtisanRepository
import com.sttalis.artisan.model.Material
import kotlinx.coroutines.launch

class MateriaisViewModel : ViewModel() {

    private val repository = ArtisanRepository()

    private val _listaMateriais = MutableLiveData<List<Material>>()
    val listaMateriais: LiveData<List<Material>> = _listaMateriais

    fun carregarMateriais() {
        viewModelScope.launch {
            try {
                val lista = repository.getMateriais()
                _listaMateriais.postValue(lista)
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun salvar(material: Material) {
        viewModelScope.launch {
            try {
                if (material.id == 0L) {
                    repository.criarMaterial(material.nome, material.descricao ?: "")
                } else {
                    repository.atualizarMaterial(material.id, material.nome, material.descricao ?: "")
                }
                carregarMateriais()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun deletar(material: Material) {
        viewModelScope.launch {
            try {
                repository.deletarMaterial(material.id)
                carregarMateriais()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
}