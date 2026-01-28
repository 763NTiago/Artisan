package com.sttalis.artisan.ui.relatorios

import android.app.DatePickerDialog
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.core.content.FileProvider
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.sttalis.artisan.R
import com.sttalis.artisan.model.RelatorioItem
import java.io.File
import java.io.FileOutputStream
import java.text.NumberFormat
import java.util.Calendar
import java.util.Locale

class RelatoriosFragment : Fragment(R.layout.fragment_relatorios) {

    private val viewModel: RelatoriosViewModel by viewModels()
    private lateinit var adapter: RelatorioAdapter
    private var dadosAtuais: List<RelatorioItem> = emptyList()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val spinCli = view.findViewById<Spinner>(R.id.spinFiltroCliente)
        val spinProj = view.findViewById<Spinner>(R.id.spinFiltroProjeto)
        val spinArq = view.findViewById<Spinner>(R.id.spinFiltroArquiteto)

        val btnIni = view.findViewById<Button>(R.id.btnDataInicio)
        val btnFim = view.findViewById<Button>(R.id.btnDataFim)
        val btnFiltrar = view.findViewById<Button>(R.id.btnFiltrarAgora)
        val btnLimpar = view.findViewById<Button>(R.id.btnLimparFiltros)
        val btnExportar = view.findViewById<Button>(R.id.btnExportarExcel)
        val recycler = view.findViewById<RecyclerView>(R.id.recyclerRelatorios)

        val lblTotal = view.findViewById<TextView>(R.id.lblTotal)
        val lblComissao = view.findViewById<TextView>(R.id.lblComissao)
        val lblRecebido = view.findViewById<TextView>(R.id.lblRecebido)
        val lblPendente = view.findViewById<TextView>(R.id.lblPendente)
        val lblLucro = view.findViewById<TextView>(R.id.lblLucro)

        adapter = RelatorioAdapter()
        recycler.layoutManager = LinearLayoutManager(context)
        recycler.adapter = adapter

        viewModel.relatorioProcessado.observe(viewLifecycleOwner) { lista ->
            dadosAtuais = lista
            adapter.lista = lista
            adapter.notifyDataSetChanged()

            val fmt = NumberFormat.getCurrencyInstance(Locale("pt", "BR"))
            lblTotal.text = "Total: ${fmt.format(lista.sumOf { it.totalProjeto })}"
            lblComissao.text = "Saiu: ${fmt.format(lista.sumOf { it.comissao })}"
            lblRecebido.text = "Entrou: ${fmt.format(lista.sumOf { it.valorPago })}"
            lblPendente.text = "Falta: ${fmt.format(lista.sumOf { it.aReceber })}"
            lblLucro.text = "Líquido: ${fmt.format(lista.sumOf { it.lucro })}"
        }

        viewModel.listaClientes.observe(viewLifecycleOwner) { lista ->
            spinCli.adapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, lista)
        }
        viewModel.listaProjetos.observe(viewLifecycleOwner) { lista ->
            spinProj.adapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, lista)
        }
        viewModel.listaArquitetos.observe(viewLifecycleOwner) { lista ->
            spinArq.adapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, lista)
        }

        spinCli.onItemSelectedListener = createListener { viewModel.filtroCliente.value = it }
        spinProj.onItemSelectedListener = createListener { viewModel.filtroProjeto.value = it }
        spinArq.onItemSelectedListener = createListener { viewModel.filtroArquiteto.value = it }

        val cal = Calendar.getInstance()

        btnIni.setOnClickListener {
            DatePickerDialog(requireContext(), { _, y, m, d ->
                val s = String.format("%02d/%02d/%04d", d, m + 1, y)
                btnIni.text = s
                viewModel.filtroDataInicio.value = s
            }, cal.get(Calendar.YEAR), cal.get(Calendar.MONTH), cal.get(Calendar.DAY_OF_MONTH)).show()
        }

        btnFim.setOnClickListener {
            DatePickerDialog(requireContext(), { _, y, m, d ->
                val s = String.format("%02d/%02d/%04d", d, m + 1, y)
                btnFim.text = s
                viewModel.filtroDataFim.value = s
            }, cal.get(Calendar.YEAR), cal.get(Calendar.MONTH), cal.get(Calendar.DAY_OF_MONTH)).show()
        }

        btnFiltrar.setOnClickListener {
            viewModel.aplicarFiltros()
            Toast.makeText(context, "Filtros Aplicados", Toast.LENGTH_SHORT).show()
        }

        btnLimpar.setOnClickListener {
            viewModel.filtroDataInicio.value = null
            viewModel.filtroDataFim.value = null
            viewModel.filtroCliente.value = null
            viewModel.filtroProjeto.value = null
            viewModel.filtroArquiteto.value = null

            spinCli.setSelection(0)
            spinProj.setSelection(0)
            spinArq.setSelection(0)
            btnIni.text = "Data Início"
            btnFim.text = "Data Fim"

            viewModel.aplicarFiltros()
        }

        btnExportar.setOnClickListener { exportarCSV() }
    }

    private fun createListener(onSelected: (String?) -> Unit): AdapterView.OnItemSelectedListener {
        return object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(p0: AdapterView<*>?, p1: View?, pos: Int, id: Long) {
                val item = p0?.getItemAtPosition(pos).toString()
                onSelected(if (pos == 0) null else item)
            }
            override fun onNothingSelected(p0: AdapterView<*>?) {}
        }
    }

    private fun exportarCSV() {
        if (dadosAtuais.isEmpty()) return
        try {
            val sb = StringBuilder()
            sb.append("Inicio;Fim;Cliente;Projeto;Arquiteto;Total;Comissao;Recebido;Pendente;Lucro\n")
            dadosAtuais.forEach {
                sb.append("${it.dataInicio};${it.dataTermino};${it.cliente};${it.projeto};${it.arquiteto ?: ""};" +
                        "${it.totalProjeto};${it.comissao};${it.valorPago};${it.aReceber};${it.lucro}\n")
            }
            val file = File(requireContext().cacheDir, "Relatorio_Detalhado.csv")
            FileOutputStream(file).use { it.write(sb.toString().toByteArray()) }
            val uri = FileProvider.getUriForFile(requireContext(), "${requireContext().packageName}.provider", file)
            val intent = Intent(Intent.ACTION_SEND)
            intent.type = "text/csv"
            intent.putExtra(Intent.EXTRA_STREAM, uri)
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            startActivity(Intent.createChooser(intent, "Exportar"))
        } catch (e: Exception) {
            Toast.makeText(context, "Erro ao exportar", Toast.LENGTH_SHORT).show()
        }
    }
}