package com.sttalis.artisan.ui.comissao

import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.sttalis.artisan.R
import com.sttalis.artisan.model.Comissao
import java.text.NumberFormat
import java.util.Locale

class ComissaoAdapter(
    private val onClick: (Comissao) -> Unit
) : RecyclerView.Adapter<ComissaoAdapter.VH>() {

    var lista = emptyList<Comissao>()

    class VH(v: View) : RecyclerView.ViewHolder(v)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val v = LayoutInflater.from(parent.context).inflate(R.layout.item_comissao, parent, false)
        return VH(v)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        val item = lista[position]
        val v = holder.itemView

        val txtArq = v.findViewById<TextView>(R.id.txtComissaoArq)
        val txtProj = v.findViewById<TextView>(R.id.txtComissaoProj)
        val txtData = v.findViewById<TextView>(R.id.txtComissaoData)
        val txtValor = v.findViewById<TextView>(R.id.txtComissaoValor)
        val txtStatus = v.findViewById<TextView>(R.id.txtComissaoStatus)

        txtArq.text = "${item.arquitetoNome} (${item.porcentagem.toInt()}%)"
        txtProj.text = item.projetoNome ?: "Sem Projeto"

        val fmt = NumberFormat.getCurrencyInstance(Locale("pt", "BR"))
        txtValor.text = fmt.format(item.valorComissao)

        if (item.status == "Pago") {
            txtStatus.text = "PAGO"
            txtStatus.setTextColor(Color.parseColor("#2E7D32")) 
            txtStatus.setBackgroundColor(Color.parseColor("#E8F5E9")) 

            txtData.text = "Pago em: ${item.dataPrevisao}"
            txtData.setTextColor(Color.parseColor("#2E7D32"))

            txtValor.setTextColor(Color.GRAY) 
        } else {
            txtStatus.text = "PENDENTE"
            txtStatus.setTextColor(Color.parseColor("#C62828"))
            txtStatus.setBackgroundColor(Color.parseColor("#FFEBEE")) 

            txtData.text = "Prev: ${item.dataPrevisao}"
            txtData.setTextColor(Color.parseColor("#C62828"))

            txtValor.setTextColor(Color.parseColor("#2E7D32")) 
        }

        v.setOnClickListener { onClick(item) }
    }

    override fun getItemCount() = lista.size
}