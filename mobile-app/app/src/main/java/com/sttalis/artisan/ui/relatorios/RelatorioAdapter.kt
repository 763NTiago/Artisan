package com.sttalis.artisan.ui.relatorios

import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.sttalis.artisan.R
import com.sttalis.artisan.model.RelatorioItem
import java.text.NumberFormat
import java.text.SimpleDateFormat
import java.util.Locale

class RelatorioAdapter : RecyclerView.Adapter<RelatorioAdapter.VH>() {

    var lista = emptyList<RelatorioItem>()

    class VH(v: View) : RecyclerView.ViewHolder(v) {
        val txtDataIni: TextView = v.findViewById(R.id.colDataIni)
        val txtDataFim: TextView = v.findViewById(R.id.colDataFim)
        val txtCliente: TextView = v.findViewById(R.id.colCliente)
        val txtProjeto: TextView = v.findViewById(R.id.colProjeto)
        val txtArquiteto: TextView = v.findViewById(R.id.colArquiteto)
        val txtTotal: TextView = v.findViewById(R.id.colTotal)
        val txtComissao: TextView = v.findViewById(R.id.colComissao)
        val txtRecebido: TextView = v.findViewById(R.id.colRecebido)
        val txtPendente: TextView = v.findViewById(R.id.colPendente)
        val txtLucro: TextView = v.findViewById(R.id.colLucro)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val v = LayoutInflater.from(parent.context).inflate(R.layout.item_relatorio, parent, false)
        return VH(v)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        val item = lista[position]
        val fmt = NumberFormat.getCurrencyInstance(Locale("pt", "BR"))

        if (position % 2 == 0) {
            holder.itemView.setBackgroundColor(Color.parseColor("#FFFFFF"))
        } else {
            holder.itemView.setBackgroundColor(Color.parseColor("#E3F2FD"))
        }

        holder.txtDataIni.text = formatData(item.dataInicio)
        holder.txtDataFim.text = formatData(item.dataTermino)
        holder.txtCliente.text = item.cliente
        holder.txtProjeto.text = item.projeto
        holder.txtArquiteto.text = item.arquiteto ?: "-"

        holder.txtTotal.text = fmt.format(item.totalProjeto)
        holder.txtComissao.text = fmt.format(item.comissao)
        holder.txtRecebido.text = fmt.format(item.valorPago)
        holder.txtPendente.text = fmt.format(item.aReceber)
        holder.txtLucro.text = fmt.format(item.lucro)

        if (item.aReceber > 0.01) {
            holder.txtPendente.setTextColor(Color.parseColor("#D32F2F")) 
        } else {
            holder.txtPendente.setTextColor(Color.parseColor("#28A745")) 
        }
    }

    private fun formatData(dt: String?): String {
        if (dt.isNullOrEmpty()) return "--/--"
        return try {
            val parser = if (dt.contains("-")) SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
            else SimpleDateFormat("dd/MM/yyyy", Locale.getDefault())
            val date = parser.parse(dt)
            SimpleDateFormat("dd/MM/yyyy", Locale("pt", "BR")).format(date!!)
        } catch (e: Exception) { dt }
    }

    override fun getItemCount() = lista.size
}