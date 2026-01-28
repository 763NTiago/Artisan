package com.sttalis.artisan.ui.cartao

import androidx.lifecycle.ViewModel
import java.text.SimpleDateFormat
import java.util.*

class CartaoViewModel : ViewModel() {

    fun gerarCodigoPadrao(porcentagem: String): String {
        val ano = Calendar.getInstance().get(Calendar.YEAR)
        return "${ano}Artisan${porcentagem}"
    }

    fun getDataValidadePadrao(): String {
        val cal = Calendar.getInstance()
        cal.add(Calendar.DAY_OF_MONTH, 30) 
        return SimpleDateFormat("dd/MM/yyyy", Locale("pt", "BR")).format(cal.time)
    }
}