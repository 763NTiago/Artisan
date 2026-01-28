package com.sttalis.artisan.ui.orcamento.tabs

import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.sttalis.artisan.model.MaterialIncluso

class MaterialInclusoAdapter(
    private val onClick: (MaterialIncluso) -> Unit
) : RecyclerView.Adapter<MaterialInclusoAdapter.VH>() {

    val lista = mutableListOf<MaterialIncluso>()
    var selecionado: MaterialIncluso? = null

    inner class VH(v: View) : RecyclerView.ViewHolder(v) {
        val txtNome: TextView = v.findViewById(android.R.id.text1)
        val txtDesc: TextView = v.findViewById(android.R.id.text2)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val v = LayoutInflater.from(parent.context)
            .inflate(android.R.layout.simple_list_item_2, parent, false)
        return VH(v)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        val item = lista[position]
        holder.txtNome.text = item.nome
        holder.txtDesc.text = item.descricao

        if (item == selecionado) {
            holder.itemView.setBackgroundColor(Color.parseColor("#E3F2FD"))
        } else {
            holder.itemView.setBackgroundColor(Color.TRANSPARENT)
        }

        holder.itemView.setOnClickListener {
            selecionado = item
            notifyDataSetChanged()
            onClick(item)
        }
    }

    override fun getItemCount() = lista.size
}