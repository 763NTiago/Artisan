package com.sttalis.artisan.ui.comissao

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.sttalis.artisan.R
import com.sttalis.artisan.model.Arquiteto

class ArquitetoAdapter(
    private val onDelete: (Arquiteto) -> Unit
) : RecyclerView.Adapter<ArquitetoAdapter.VH>() {

    var lista = emptyList<Arquiteto>()

    class VH(v: View) : RecyclerView.ViewHolder(v)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val v = LayoutInflater.from(parent.context).inflate(R.layout.item_arquiteto, parent, false)
        return VH(v)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        val item = lista[position]

        holder.itemView.findViewById<TextView>(R.id.txtNomeArqItem).text = item.nome

        val pctFmt = if (item.porcentagemPadrao % 1.0 == 0.0)
            item.porcentagemPadrao.toInt()
        else
            item.porcentagemPadrao

        holder.itemView.findViewById<TextView>(R.id.txtDiaPagItem).text =
            "Pagamento dia ${item.diaPagamentoPreferencial} | Comissão: $pctFmt%"

        holder.itemView.findViewById<View>(R.id.btnDeleteArq).setOnClickListener {
            onDelete(item)
        }
    }

    override fun getItemCount() = lista.size
}