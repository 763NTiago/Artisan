package com.sttalis.artisan.ui

import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.sttalis.artisan.R
import java.util.*

class CalendarAdapter(
    private val diasDoMes: List<Date?>,
    private val eventos: Map<String, List<EventoCalendario>>,
    private val onClick: (Date) -> Unit
) : RecyclerView.Adapter<CalendarAdapter.CalendarViewHolder>() {

    val hojeStr = android.text.format.DateFormat.format("dd/MM/yyyy", Date()).toString()

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CalendarViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_calendar_day, parent, false)
        return CalendarViewHolder(view)
    }

    override fun onBindViewHolder(holder: CalendarViewHolder, position: Int) {
        val data = diasDoMes[position]
        holder.bind(data)
    }

    override fun getItemCount(): Int = diasDoMes.size

    inner class CalendarViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val txtDia: TextView = itemView.findViewById(R.id.txtDiaNumero)
        private val container: View = itemView

        fun bind(data: Date?) {
            if (data == null) {
                txtDia.text = ""
                txtDia.background = null
                container.setOnClickListener(null)
                return
            }

            val cal = Calendar.getInstance()
            cal.time = data
            val dia = cal.get(Calendar.DAY_OF_MONTH)
            val dataStr = android.text.format.DateFormat.format("dd/MM/yyyy", data).toString()

            txtDia.text = dia.toString()

            val listaEventos = eventos[dataStr] ?: emptyList()

            val background = itemView.context.getDrawable(R.drawable.bg_calendar_circle) as GradientDrawable

            var corFundo = Color.TRANSPARENT
            var corTexto = Color.BLACK

            if (listaEventos.isNotEmpty()) {
                val temVencimento = listaEventos.any { it.tipo == TipoEvento.VENCIMENTO }
                val temEntrega = listaEventos.any { it.tipo == TipoEvento.ENTREGA }
                val temInicio = listaEventos.any { it.tipo == TipoEvento.INICIO }

                if (temVencimento) {
                    corFundo = Color.parseColor("#dc3545")
                    corTexto = Color.WHITE
                } else if (temEntrega) {
                    corFundo = Color.parseColor("#28a745")
                    corTexto = Color.WHITE
                } else if (temInicio) {
                    corFundo = Color.parseColor("#17a2b8")
                    corTexto = Color.WHITE
                }
            }

            if (dataStr == hojeStr) {
                if (corFundo == Color.TRANSPARENT) {
                    corFundo = Color.parseColor("#ffc107")
                    corTexto = Color.BLACK
                }
            }

            background.setColor(corFundo)
            txtDia.background = background
            txtDia.setTextColor(corTexto)

            container.setOnClickListener { onClick(data) }
        }
    }
}

enum class TipoEvento { INICIO, ENTREGA, VENCIMENTO }
data class EventoCalendario(val tipo: TipoEvento, val descricao: String)