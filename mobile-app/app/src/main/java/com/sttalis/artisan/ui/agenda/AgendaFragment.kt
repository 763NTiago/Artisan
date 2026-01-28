package com.sttalis.artisan.ui.agenda

import android.app.DatePickerDialog
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.widget.*
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.sttalis.artisan.R
import com.sttalis.artisan.model.Agenda
import com.sttalis.artisan.model.Cliente
import com.sttalis.artisan.model.Orcamento
import com.sttalis.artisan.utils.MoneyTextWatcher
import kotlinx.coroutines.launch
import java.text.NumberFormat
import java.util.Calendar
import java.util.Locale

class AgendaFragment : Fragment(R.layout.fragment_agenda) {

    private val viewModel: AgendaViewModel by viewModels()
    private lateinit var adapter: AgendaAdapter
    private var projetoSelecionado: Agenda? = null

    private var listaClientesCache: List<Cliente> = emptyList()
    private var listaOrcamentosCache: List<Orcamento> = emptyList()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val recycler = view.findViewById<RecyclerView>(R.id.recyclerAgenda)

        adapter = AgendaAdapter { selecionado -> projetoSelecionado = selecionado }
        recycler.layoutManager = LinearLayoutManager(context)
        recycler.adapter = adapter

        viewModel.listaAgenda.observe(viewLifecycleOwner) { adapter.submitList(it) }
        viewModel.listaClientes.observe(viewLifecycleOwner) { listaClientesCache = it }
        viewModel.listaOrcamentos.observe(viewLifecycleOwner) { listaOrcamentosCache = it }

        view.findViewById<Button>(R.id.btnNovoProjeto).setOnClickListener { abrirDialogFormulario(null) }
        view.findViewById<Button>(R.id.btnEditarProjeto).setOnClickListener {
            if (projetoSelecionado != null) abrirDialogFormulario(projetoSelecionado)
            else Toast.makeText(context, "Selecione um projeto.", Toast.LENGTH_SHORT).show()
        }
        view.findViewById<Button>(R.id.btnRemoverProjeto).setOnClickListener { removerProjeto() }

        view.findViewById<Button>(R.id.btnFiltroTodos).setOnClickListener { viewModel.carregarDados() }
    }

    private fun abrirDialogFormulario(projetoExistente: Agenda?) {
        val dialogView = LayoutInflater.from(requireContext()).inflate(R.layout.dialog_agenda_projeto, null)

        val spinOrcamento = dialogView.findViewById<Spinner>(R.id.spinnerOrcamentoAgenda)
        val autoCliente = dialogView.findViewById<AutoCompleteTextView>(R.id.autoCompleteClienteAgenda)
        val edtAmbiente = dialogView.findViewById<EditText>(R.id.inputItemAmbiente)
        val edtDescricao = dialogView.findViewById<EditText>(R.id.inputDescricaoDetalhada)
        val edtValor = dialogView.findViewById<EditText>(R.id.inputValorProjeto)
        val edtInicio = dialogView.findViewById<EditText>(R.id.inputDataInicio)
        val edtEntrega = dialogView.findViewById<EditText>(R.id.inputDataEntrega)

        edtValor.addTextChangedListener(MoneyTextWatcher(edtValor))
        val fmtMoeda = NumberFormat.getCurrencyInstance(Locale("pt", "BR"))

        val nomesClientes = listaClientesCache.map { it.nome }
        val adapterCli = ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, nomesClientes)
        autoCliente.setAdapter(adapterCli)

        val orcamentosDisplay = mutableListOf("Puxar de Orçamento (Opcional)")
        orcamentosDisplay.addAll(listaOrcamentosCache.map { "ID ${it.id} - ${it.clienteNome} (${fmtMoeda.format(it.valorTotalFinal)})" })
        val adapterOrc = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, orcamentosDisplay)
        spinOrcamento.adapter = adapterOrc

        spinOrcamento.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                if (position > 0) {
                    val orcamento = listaOrcamentosCache[position - 1]

                    autoCliente.setText(orcamento.clienteNome)
                    autoCliente.dismissDropDown()

                    edtValor.setText(fmtMoeda.format(orcamento.valorTotalFinal))

                    val resumoItens = StringBuilder()
                    orcamento.itens.forEach { item ->
                        if (resumoItens.isNotEmpty()) resumoItens.append("; ")
                        resumoItens.append("${item.ambiente}: ${item.descricao}")
                    }
                    val textoResumo = resumoItens.toString()
                    if (textoResumo.length > 50) {
                        edtAmbiente.setText(textoResumo.substring(0, 47) + "...")
                        edtDescricao.setText(textoResumo) 
                    } else {
                        edtAmbiente.setText(textoResumo)
                    }
                }
            }
            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }

        configurarDatePicker(edtInicio)
        configurarDatePicker(edtEntrega)

        if (projetoExistente != null) {
            autoCliente.setText(projetoExistente.clienteNome)
            edtInicio.setText(projetoExistente.dataInicio ?: "")
            edtEntrega.setText(projetoExistente.dataEntrega ?: "")
            edtAmbiente.setText(projetoExistente.descricao)
            edtValor.setText(fmtMoeda.format(projetoExistente.valorFinal))
        }

        AlertDialog.Builder(requireContext())
            .setView(dialogView)
            .setPositiveButton("Salvar") { _, _ ->
                lifecycleScope.launch {
                    val nomeCliente = autoCliente.text.toString()
                    val valorProj = MoneyTextWatcher.parseCurrency(edtValor.text.toString())

                    var clienteId = listaClientesCache.find { it.nome.equals(nomeCliente, true) }?.id
                    if (clienteId == null) {
                        clienteId = viewModel.criarClienteRapido(nomeCliente)
                    }

                    val descFinal = if (edtDescricao.text.isNotEmpty()) {
                        "${edtAmbiente.text} - ${edtDescricao.text}"
                    } else {
                        edtAmbiente.text.toString()
                    }

                    val novoProjeto = Agenda(
                        id = projetoExistente?.id ?: 0,
                        clienteId = clienteId,
                        clienteNome = nomeCliente,
                        descricao = descFinal,
                        dataInicio = edtInicio.text.toString(),
                        dataPrevisaoTermino = edtEntrega.text.toString(),
                        valor = valorProj 
                    )

                    viewModel.salvarProjeto(novoProjeto)
                    Toast.makeText(context, "Projeto Salvo!", Toast.LENGTH_SHORT).show()
                }
            }
            .setNegativeButton("Cancelar", null)
            .show()
    }

    private fun removerProjeto() {
        projetoSelecionado?.let {
            viewModel.deletarProjeto(it)
            Toast.makeText(context, "Removido.", Toast.LENGTH_SHORT).show()
        }
    }

    private fun configurarDatePicker(editText: EditText) {
        editText.setOnClickListener {
            val cal = Calendar.getInstance()
            DatePickerDialog(requireContext(), { _, y, m, d ->
                editText.setText(String.format("%02d/%02d/%04d", d, m + 1, y))
            }, cal.get(Calendar.YEAR), cal.get(Calendar.MONTH), cal.get(Calendar.DAY_OF_MONTH)).show()
        }
    }
}