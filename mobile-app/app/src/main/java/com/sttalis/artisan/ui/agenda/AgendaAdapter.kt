package com.sttalis.artisan.ui.agenda

import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.card.MaterialCardView
import com.sttalis.artisan.R
import com.sttalis.artisan.model.Agenda
import java.text.NumberFormat
import java.util.Locale

class AgendaAdapter(
    private val onItemSelected: (Agenda?) -> Unit
) : ListAdapter<Agenda, AgendaAdapter.AgendaViewHolder>(AgendaDiffCallback()) {

    private var selectedPos = RecyclerView.NO_POSITION

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): AgendaViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_agenda, parent, false)
        return AgendaViewHolder(view)
    }

    override fun onBindViewHolder(holder: AgendaViewHolder, position: Int) {
        holder.bind(getItem(position), position == selectedPos)
    }

    inner class AgendaViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val card: MaterialCardView = itemView.findViewById(R.id.cardContainer)
        private val txtDesc: TextView = itemView.findViewById(R.id.txtDescricaoProj)
        private val txtCliente: TextView = itemView.findViewById(R.id.txtClienteProj)
        private val txtDatas: TextView = itemView.findViewById(R.id.txtDatasProj)
        private val txtValor: TextView = itemView.findViewById(R.id.txtValorProj)
        private val txtStatus: TextView = itemView.findViewById(R.id.txtStatusProj)

        fun bind(item: Agenda, isSelected: Boolean) {
            txtDesc.text = item.descricao ?: "Sem Descrição"
            txtCliente.text = "Cliente: ${item.clienteNome ?: "Desconhecido"}"
            txtDatas.text = "Início: ${item.dataInicio ?: "--"} - Entrega: ${item.dataEntrega ?: "--"}"

            val formatador = NumberFormat.getCurrencyInstance(Locale("pt", "BR"))
            txtValor.text = formatador.format(item.valorFinal)

            val statusTexto = item.status ?: "Pendente"
            txtStatus.text = statusTexto
            definirCorStatus(statusTexto, txtStatus)

            if (isSelected) {
                card.strokeColor = Color.parseColor("#007BFF")
                card.strokeWidth = 4
                card.setCardBackgroundColor(Color.parseColor("#E3F2FD"))
            } else {
                card.strokeColor = Color.parseColor("#E0E0E0")
                card.strokeWidth = 1
                card.setCardBackgroundColor(Color.WHITE)
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

        private fun definirCorStatus(status: String, view: TextView) {
            val color = when (status) {
                "Pendente" -> "#FFC107"
                "Em Andamento" -> "#17A2B8"
                "Concluído" -> "#28A745"
                "Cancelado" -> "#DC3545"
                else -> "#6C757D"
            }
            view.setTextColor(Color.parseColor(color))
        }
    }

    class AgendaDiffCallback : DiffUtil.ItemCallback<Agenda>() {
        override fun areItemsTheSame(oldItem: Agenda, newItem: Agenda) = oldItem.id == newItem.id
        override fun areContentsTheSame(oldItem: Agenda, newItem: Agenda) = oldItem == newItem
    }
}