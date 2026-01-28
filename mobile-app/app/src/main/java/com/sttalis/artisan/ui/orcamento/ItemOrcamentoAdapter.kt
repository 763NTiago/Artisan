package com.sttalis.artisan.ui.orcamento

import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.sttalis.artisan.R
import com.sttalis.artisan.model.ItemOrcamento
import java.text.NumberFormat
import java.util.Locale

class ItemOrcamentoAdapter(
    private val onItemSelected: (ItemOrcamento) -> Unit
) : RecyclerView.Adapter<ItemOrcamentoAdapter.ItemViewHolder>() {

    private val listaItens = mutableListOf<ItemOrcamento>()
    private var selectedPos = RecyclerView.NO_POSITION

    fun atualizarLista(novaLista: List<ItemOrcamento>) {
        listaItens.clear()
        listaItens.addAll(novaLista)
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ItemViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_cria_orcamento, parent, false)
        return ItemViewHolder(view)
    }

    override fun onBindViewHolder(holder: ItemViewHolder, position: Int) {
        holder.bind(listaItens[position], position == selectedPos)
    }

    override fun getItemCount(): Int = listaItens.size

    inner class ItemViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val txtDesc: TextView = itemView.findViewById(R.id.txtDescricao)
        private val txtMedidas: TextView = itemView.findViewById(R.id.txtMedidas)
        private val txtPreco: TextView = itemView.findViewById(R.id.txtPrecoTotal)
        private val btnDel: View = itemView.findViewById(R.id.btnRemover)

        fun bind(item: ItemOrcamento, isSelected: Boolean) {
            btnDel.visibility = View.GONE

            val formatador = NumberFormat.getCurrencyInstance(Locale("pt", "BR"))

            val qtdDisplay = if (item.quantidade % 1.0 == 0.0)
                item.quantidade.toInt().toString()
            else
                item.quantidade.toString()

            txtDesc.text = item.descricao

            txtMedidas.text = "$qtdDisplay un - ${item.ambiente}"

            txtPreco.text = formatador.format(item.valorTotal)

            if (isSelected) {
                itemView.setBackgroundColor(Color.parseColor("#E3F2FD"))
            } else {
                itemView.setBackgroundColor(Color.WHITE)
            }

            itemView.setOnClickListener {
                val previousPos = selectedPos
                val currentPos = adapterPosition

                if (currentPos != RecyclerView.NO_POSITION) {
                    selectedPos = currentPos
                    notifyItemChanged(previousPos)
                    notifyItemChanged(selectedPos)
                    onItemSelected(item)
                }
            }
        }
    }
}