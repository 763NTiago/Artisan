package com.sttalis.artisan.ui

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.sttalis.artisan.R
import com.sttalis.artisan.model.Cliente

class ClienteAdapter(
    private val onClick: (Cliente) -> Unit
) : ListAdapter<Cliente, ClienteAdapter.ClienteViewHolder>(ClienteDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ClienteViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_cliente, parent, false)
        return ClienteViewHolder(view, onClick)
    }

    override fun onBindViewHolder(holder: ClienteViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ClienteViewHolder(itemView: View, val onClick: (Cliente) -> Unit) :
        RecyclerView.ViewHolder(itemView) {
        
        private val txtNome: TextView = itemView.findViewById(R.id.txtNome)
        private val txtTelefone: TextView = itemView.findViewById(R.id.txtTelefone)
        private val txtEmail: TextView = itemView.findViewById(R.id.txtEmail)

        fun bind(cliente: Cliente) {
            txtNome.text = cliente.nome
            txtTelefone.text = cliente.telefone ?: "-"
            txtEmail.text = cliente.email ?: "-"
            
            itemView.setOnClickListener { onClick(cliente) }
        }
    }

    class ClienteDiffCallback : DiffUtil.ItemCallback<Cliente>() {
        override fun areItemsTheSame(oldItem: Cliente, newItem: Cliente): Boolean {
            return oldItem.id == newItem.id
        }
        override fun areContentsTheSame(oldItem: Cliente, newItem: Cliente): Boolean {
            return oldItem == newItem
        }
    }
}