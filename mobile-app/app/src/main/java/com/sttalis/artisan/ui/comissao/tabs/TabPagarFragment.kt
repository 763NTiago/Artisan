package com.sttalis.artisan.ui.comissao.tabs

import android.app.AlertDialog
import android.app.DatePickerDialog
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.floatingactionbutton.FloatingActionButton
import com.sttalis.artisan.R
import com.sttalis.artisan.model.Agenda
import com.sttalis.artisan.model.Arquiteto
import com.sttalis.artisan.model.Cliente
import com.sttalis.artisan.model.Recebimento
import com.sttalis.artisan.ui.comissao.ComissaoAdapter
import com.sttalis.artisan.ui.comissao.ComissoesViewModel
import java.text.NumberFormat
import java.util.Calendar
import java.util.Locale

class TabPagarFragment : Fragment() {

    private lateinit var viewModel: ComissoesViewModel
    private lateinit var adapter: ComissaoAdapter

    private var listaArquitetos: List<Arquiteto> = emptyList()
    private var listaRecebimentos: List<Recebimento> = emptyList()
    private var listaClientes: List<Cliente> = emptyList()
    private var listaAgenda: List<Agenda> = emptyList()

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.fragment_tab_comissoes_pagar, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        viewModel = ViewModelProvider(requireParentFragment())[ComissoesViewModel::class.java]

        val recycler = view.findViewById<RecyclerView>(R.id.recyclerComissoes)
        val fab = view.findViewById<FloatingActionButton>(R.id.fabLancarComissao)

        adapter = ComissaoAdapter { item ->
            AlertDialog.Builder(requireContext())
                .setTitle("Ações")
                .setItems(arrayOf("Pagar (Dar Baixa)", "Excluir")) { _, which ->
                    if (which == 0) {
                        viewModel.pagarComissao(item)
                        Toast.makeText(context, "Pago!", Toast.LENGTH_SHORT).show()
                    }
                    else viewModel.deletarComissao(item)
                }
                .show()
        }

        recycler.layoutManager = LinearLayoutManager(context)
        recycler.adapter = adapter

        viewModel.listaComissoesPendentes.observe(viewLifecycleOwner) { adapter.lista = it; adapter.notifyDataSetChanged() }
        viewModel.listaArquitetos.observe(viewLifecycleOwner) { listaArquitetos = it }
        viewModel.listaRecebimentos.observe(viewLifecycleOwner) { listaRecebimentos = it }
        viewModel.listaClientes.observe(viewLifecycleOwner) { listaClientes = it }
        viewModel.listaAgenda.observe(viewLifecycleOwner) { listaAgenda = it }

        fab.setOnClickListener {
            if (listaArquitetos.isEmpty()) {
                Toast.makeText(context, "Cadastre um Arquiteto primeiro.", Toast.LENGTH_LONG).show()
            } else {
                abrirDialogLancar()
            }
        }
    }

    private fun abrirDialogLancar() {
        val dialogView = LayoutInflater.from(requireContext()).inflate(R.layout.dialog_lancar_comissao, null)

        val spinArq = dialogView.findViewById<Spinner>(R.id.spinArquitetoCom)
        val spinRec = dialogView.findViewById<Spinner>(R.id.spinProjetoCom)
        val edtPct = dialogView.findViewById<EditText>(R.id.edtPorcentagemCom)
        val txtBase = dialogView.findViewById<TextView>(R.id.txtValorBaseCom)
        val txtFinal = dialogView.findViewById<TextView>(R.id.txtValorFinalCom)
        val edtData = dialogView.findViewById<EditText>(R.id.edtDataPrevistaCom)
        val btnSalvar = dialogView.findViewById<Button>(R.id.btnSalvarComissaoDialog)

        val nomesArq = listaArquitetos.map { it.nome }
        spinArq.adapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, nomesArq)

        val recebimentosDisplay = mutableListOf<String>()
        val recebimentosValidos = mutableListOf<Recebimento>()

        if (listaRecebimentos.isEmpty()) {
            recebimentosDisplay.add("Nenhum Recebimento")
            spinRec.isEnabled = false
        } else {
            spinRec.isEnabled = true
            listaRecebimentos.forEach { rec ->
                val nomeCliente = listaClientes.find { it.id == rec.clienteId }?.nome ?: "Cliente"

                var descProjeto = "Lançamento Manual"
                if (rec.agendaId != null) {
                    val proj = listaAgenda.find { it.id == rec.agendaId }
                    if (proj != null) descProjeto = proj.descricao ?: ""
                }

                val fmt = NumberFormat.getCurrencyInstance(Locale("pt", "BR"))
                val valorFmt = fmt.format(rec.valorTotal)

                recebimentosDisplay.add("$nomeCliente - $descProjeto ($valorFmt)")
                recebimentosValidos.add(rec)
            }
        }

        spinRec.adapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, recebimentosDisplay)

        val atualizarCalculos = {
            if (spinRec.selectedItemPosition >= 0 && recebimentosValidos.isNotEmpty()) {
                val recebimento = recebimentosValidos[spinRec.selectedItemPosition]
                val pct = edtPct.text.toString().toDoubleOrNull() ?: 0.0
                val base = recebimento.valorTotal
                val comissao = base * (pct / 100.0)
                val fmt = NumberFormat.getCurrencyInstance(Locale("pt", "BR"))
                txtBase.text = fmt.format(base)
                txtFinal.text = fmt.format(comissao)
            } else {
                txtBase.text = "R$ 0,00"
                txtFinal.text = "R$ 0,00"
            }
        }

        spinArq.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(p0: AdapterView<*>?, p1: View?, pos: Int, id: Long) {
                if (pos >= 0 && pos < listaArquitetos.size) {
                    val arq = listaArquitetos[pos]
                    edtData.setText(viewModel.calcularDataSugerida(arq))
                    if (arq.porcentagemPadrao > 0) {
                        val pctText = if (arq.porcentagemPadrao % 1.0 == 0.0) arq.porcentagemPadrao.toInt().toString() else arq.porcentagemPadrao.toString()
                        edtPct.setText(pctText)
                        atualizarCalculos()
                    }
                }
            }
            override fun onNothingSelected(p0: AdapterView<*>?) {}
        }

        spinRec.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(p0: AdapterView<*>?, p1: View?, p2: Int, p3: Long) { atualizarCalculos() }
            override fun onNothingSelected(p0: AdapterView<*>?) {}
        }

        edtPct.addTextChangedListener(object : TextWatcher {
            override fun afterTextChanged(s: Editable?) { atualizarCalculos() }
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
        })

        edtData.setOnClickListener {
            val c = Calendar.getInstance()
            DatePickerDialog(requireContext(), { _, y, m, d ->
                edtData.setText(String.format("%02d/%02d/%04d", d, m + 1, y))
            }, c.get(Calendar.YEAR), c.get(Calendar.MONTH), c.get(Calendar.DAY_OF_MONTH)).show()
        }

        val dialog = AlertDialog.Builder(requireContext()).setView(dialogView).create()

        btnSalvar.setOnClickListener {
            if (listaArquitetos.isEmpty() || recebimentosValidos.isEmpty()) return@setOnClickListener
            val arq = listaArquitetos[spinArq.selectedItemPosition]
            val recebimento = recebimentosValidos[spinRec.selectedItemPosition]
            val nomeExibicao = spinRec.selectedItem.toString()
            val pct = edtPct.text.toString().toDoubleOrNull() ?: 0.0
            val data = edtData.text.toString()

            if (pct <= 0) {
                Toast.makeText(context, "Informe a porcentagem.", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            viewModel.salvarComissao(arq, recebimento, nomeExibicao, recebimento.valorTotal, pct, data)
            Toast.makeText(context, "Salvo!", Toast.LENGTH_SHORT).show()
            dialog.dismiss()
        }

        dialog.show()
    }
}