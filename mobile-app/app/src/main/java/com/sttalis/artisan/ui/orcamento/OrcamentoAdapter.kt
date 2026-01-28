package com.sttalis.artisan.ui.orcamento

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.sttalis.artisan.R
import com.sttalis.artisan.model.Orcamento
import java.text.NumberFormat
import java.util.Locale

class OrcamentoAdapter(
    private val onClick: (Orcamento) -> Unit
) : ListAdapter<Orcamento, OrcamentoAdapter.OrcamentoViewHolder>(DiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): OrcamentoViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_orcamento, parent, false)
        return OrcamentoViewHolder(view, onClick)
    }

    override fun onBindViewHolder(holder: OrcamentoViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class OrcamentoViewHolder(itemView: View, val onClick: (Orcamento) -> Unit) :
        RecyclerView.ViewHolder(itemView) {

        fun bind(orcamento: Orcamento) {
            itemView.findViewById<TextView>(R.id.txtClienteNome).text = orcamento.clienteNome
            itemView.findViewById<TextView>(R.id.txtData).text = orcamento.dataCriacao

            val formatador = NumberFormat.getCurrencyInstance(Locale("pt", "BR"))
            itemView.findViewById<TextView>(R.id.txtValor).text = formatador.format(orcamento.valorTotalFinal)

            itemView.setOnClickListener { onClick(orcamento) }
        }
    }

    class DiffCallback : DiffUtil.ItemCallback<Orcamento>() {
        override fun areItemsTheSame(oldItem: Orcamento, newItem: Orcamento) = oldItem.id == newItem.id
        override fun areContentsTheSame(oldItem: Orcamento, newItem: Orcamento) = oldItem == newItem
    }
}