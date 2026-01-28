package com.sttalis.artisan.ui

import android.app.AlertDialog
import android.graphics.Color
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.sttalis.artisan.R
import java.text.NumberFormat
import java.text.SimpleDateFormat
import java.util.*

class HomeFragment : Fragment(R.layout.fragment_home) {

    private val viewModel: HomeViewModel by viewModels()
    private val calendarAtual = Calendar.getInstance()
    private lateinit var txtMesAno: TextView
    private lateinit var recyclerCalendar: RecyclerView
    private var mapaEventosCache: MutableMap<String, List<com.sttalis.artisan.ui.EventoCalendario>> = mutableMapOf()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val dataHoje = SimpleDateFormat("dd 'de' MMMM 'de' yyyy", Locale("pt", "BR")).format(Date())
        view.findViewById<TextView>(R.id.txtDataHoje).text = dataHoje

        val fmt = NumberFormat.getCurrencyInstance(Locale("pt", "BR"))

        viewModel.resumoFinanceiro.observe(viewLifecycleOwner) { dados ->
            if (dados != null) {
                atualizarCard(view.findViewById(R.id.kpiReceberGeral), "A Receber (Geral)", fmt.format(dados.totalAReceber))
                atualizarCard(view.findViewById(R.id.kpiReceber30d), "A Receber (30 dias)", fmt.format(dados.totalAReceber30d))
                atualizarCard(view.findViewById(R.id.kpiTotalRecebido), "Total Recebido", fmt.format(dados.totalRecebidoGeral))
                atualizarCard(view.findViewById(R.id.kpiComissoesPagas), "Comissões Pagas", fmt.format(dados.totalComissoesPagas))
                atualizarCard(view.findViewById(R.id.kpiComissoesFuturas), "Comissões a Pagar", fmt.format(dados.totalComissoesPendentes))
            }
        }

        viewModel.proximoEvento.observe(viewLifecycleOwner) { evento ->
            val card = view.findViewById<View>(R.id.kpiProximoEvento)
            if (evento != null) {
                val dataFmt = try {
                    val date = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).parse(evento.data ?: "")
                    SimpleDateFormat("dd/MM", Locale.getDefault()).format(date!!)
                } catch (e: Exception) { evento.data ?: "--/--" }

                atualizarCard(card, "Próximo: ${dataFmt}", "${evento.tipo}: ${evento.cliente}")

                val tvValor = card.findViewById<TextView>(R.id.tv_card_valor)
                tvValor.textSize = 16f 
                when(evento.tipo) {
                    "Receber" -> tvValor.setTextColor(Color.parseColor("#28A745")) 
                    "Entrega" -> tvValor.setTextColor(Color.parseColor("#17A2B8")) 
                    "Início" -> tvValor.setTextColor(Color.parseColor("#007BFF")) 
                    else -> tvValor.setTextColor(Color.parseColor("#FFC107")) 
                }
            } else {
                atualizarCard(card, "Próximo Evento", "Sem eventos")
            }
        }

        viewModel.datasEventos.observe(viewLifecycleOwner) { listaDatas ->
            if (listaDatas != null) {
                mapaEventosCache.clear()
                val sdf = SimpleDateFormat("dd/MM/yyyy", Locale("pt", "BR"))
                for (data in listaDatas) {
                    val dataStr = sdf.format(data)
                    val eventosDia = mapaEventosCache[dataStr]?.toMutableList() ?: mutableListOf()
                    if (eventosDia.isEmpty()) eventosDia.add(EventoCalendario(TipoEvento.ENTREGA, "Evento"))
                    mapaEventosCache[dataStr] = eventosDia
                }
                atualizarVisualCalendario()
            }
        }

        txtMesAno = view.findViewById(R.id.txtMesAno)
        recyclerCalendar = view.findViewById(R.id.recyclerCalendar)
        val btnAnt = view.findViewById<Button>(R.id.btnMesAnterior)
        val btnProx = view.findViewById<Button>(R.id.btnMesProximo)

        recyclerCalendar.layoutManager = GridLayoutManager(context, 7)

        btnAnt.setOnClickListener {
            calendarAtual.add(Calendar.MONTH, -1)
            atualizarVisualCalendario()
        }
        btnProx.setOnClickListener {
            calendarAtual.add(Calendar.MONTH, 1)
            atualizarVisualCalendario()
        }

        atualizarVisualCalendario()
        viewModel.carregarDadosDashboard()
    }

    private fun atualizarVisualCalendario() {
        val fmtMes = SimpleDateFormat("MMMM yyyy", Locale("pt", "BR"))
        txtMesAno.text = fmtMes.format(calendarAtual.time).replaceFirstChar { it.uppercase() }

        val dias = ArrayList<Date?>()
        val calClone = calendarAtual.clone() as Calendar
        calClone.set(Calendar.DAY_OF_MONTH, 1)
        val primeiroDiaSemana = calClone.get(Calendar.DAY_OF_WEEK)
        val maxDias = calClone.getActualMaximum(Calendar.DAY_OF_MONTH)

        for (i in 1 until primeiroDiaSemana) dias.add(null)
        for (i in 1..maxDias) {
            dias.add(calClone.time)
            calClone.add(Calendar.DAY_OF_MONTH, 1)
        }

        val adapter = CalendarAdapter(dias, mapaEventosCache) { dataClicada ->
            viewModel.carregarEventosDoDia(dataClicada)
            viewModel.eventosDoDia.observe(viewLifecycleOwner) { eventos ->
                if (eventos.isNotEmpty()) {
                    val sb = StringBuilder()
                    eventos.forEach { e -> sb.append("• ${e.tipo}: ${e.cliente} - ${e.descricao}\n") }
                    AlertDialog.Builder(requireContext())
                        .setTitle("Eventos do Dia")
                        .setMessage(sb.toString())
                        .setPositiveButton("OK", null)
                        .show()
                    viewModel.eventosDoDia.removeObservers(viewLifecycleOwner)
                }
            }
        }
        recyclerCalendar.adapter = adapter
    }

    private fun atualizarCard(card: View, titulo: String, valor: String) {
        val tvTitulo = card.findViewById<TextView>(R.id.tv_card_titulo)
        val tvValor = card.findViewById<TextView>(R.id.tv_card_valor)

        tvTitulo.text = titulo
        tvValor.text = valor

        if (titulo.contains("Geral")) tvValor.setTextColor(Color.parseColor("#FFC107"))
        else if (titulo.contains("30 dias")) tvValor.setTextColor(Color.parseColor("#007BFF"))
        else if (titulo.contains("Recebido")) tvValor.setTextColor(Color.parseColor("#28A745"))
        else if (titulo.contains("Pagas")) tvValor.setTextColor(Color.parseColor("#6C757D"))
        else if (titulo.contains("Pagar")) tvValor.setTextColor(Color.parseColor("#DC3545"))
    }

    override fun onResume() {
        super.onResume()
        viewModel.carregarDadosDashboard()
    }
}