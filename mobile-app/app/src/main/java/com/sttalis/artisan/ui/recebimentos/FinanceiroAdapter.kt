package com.sttalis.artisan.ui.recebimentos

import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.sttalis.artisan.R
import com.sttalis.artisan.model.ParcelaDetalhada
import java.text.NumberFormat
import java.util.Locale

class FinanceiroAdapter(
    private val isHistorico: Boolean, 
    private val onClick: (ParcelaDetalhada) -> Unit
) : RecyclerView.Adapter<FinanceiroAdapter.ViewHolder>() {

    private var lista: List<ParcelaDetalhada> = emptyList()

    fun atualizarLista(novaLista: List<ParcelaDetalhada>) {
        lista = novaLista
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_financeiro, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(lista[position])
    }

    override fun getItemCount(): Int = lista.size

    inner class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val txtId: TextView = itemView.findViewById(R.id.txtId)
        val txtData: TextView = itemView.findViewById(R.id.txtData)
        val txtCliente: TextView = itemView.findViewById(R.id.txtCliente)
        val txtValor: TextView = itemView.findViewById(R.id.txtValor)

        fun bind(item: ParcelaDetalhada) {
            val fmt = NumberFormat.getCurrencyInstance(Locale("pt", "BR"))

            txtId.text = item.id.toString()
            txtCliente.text = "${item.cliente} (${item.projeto})"

            if (isHistorico) {
                txtData.text = item.dataPagamento ?: "---"
                txtValor.text = fmt.format(item.valorPago) 
                txtValor.setTextColor(Color.parseColor("#2E7D32")) 
            } else {
                txtData.text = item.dataVencimento ?: "---"
                txtValor.text = fmt.format(item.valorRestante) 
                txtValor.setTextColor(Color.parseColor("#C62828")) 
            }

            itemView.setOnClickListener { onClick(item) }
        }
    }
}