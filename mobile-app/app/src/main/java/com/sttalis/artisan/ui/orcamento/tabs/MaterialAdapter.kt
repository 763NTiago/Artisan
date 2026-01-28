package com.sttalis.artisan.ui.orcamento.tabs

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageButton
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.sttalis.artisan.R
import com.sttalis.artisan.model.Material

class MaterialAdapter(
    private val onClick: (Material) -> Unit,
    private val onDelete: (Material) -> Unit
) : RecyclerView.Adapter<MaterialAdapter.VH>() {

    var lista = emptyList<Material>()

    class VH(v: View) : RecyclerView.ViewHolder(v)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val v = LayoutInflater.from(parent.context).inflate(R.layout.item_material, parent, false)
        return VH(v)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        val item = lista[position]
        val v = holder.itemView

        v.findViewById<TextView>(R.id.txtNomeMat).text = item.nome
        v.findViewById<TextView>(R.id.txtDescMat).text = item.descricao ?: ""

        v.setOnClickListener { onClick(item) }

        v.findViewById<ImageButton>(R.id.btnDeletarMat).setOnClickListener {
            onDelete(item)
        }
    }

    override fun getItemCount() = lista.size
}