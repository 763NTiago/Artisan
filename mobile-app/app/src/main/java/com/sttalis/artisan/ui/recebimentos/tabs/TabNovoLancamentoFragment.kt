package com.sttalis.artisan.ui.recebimentos.tabs

import android.app.DatePickerDialog
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import com.sttalis.artisan.R
import com.sttalis.artisan.model.Agenda
import com.sttalis.artisan.ui.recebimentos.RecebimentosViewModel
import com.sttalis.artisan.utils.MoneyTextWatcher
import java.text.NumberFormat
import java.util.Calendar
import java.util.Locale

class TabNovoLancamentoFragment : Fragment() {

    private lateinit var viewModel: RecebimentosViewModel

    private var listaAgenda: List<Agenda> = emptyList()
    private var agendaSelecionada: Agenda? = null

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.fragment_tab_novo_lancamento, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        viewModel = ViewModelProvider(requireParentFragment())[RecebimentosViewModel::class.java]

        val spinAgenda = view.findViewById<Spinner>(R.id.spinAgendaRec)
        val edtCliente = view.findViewById<EditText>(R.id.edtClienteRec) 
        val edtValorTotal = view.findViewById<EditText>(R.id.edtValorTotalRec)
        val spinTipo = view.findViewById<Spinner>(R.id.spinTipoPagRec)

        val containerParcelas = view.findViewById<View>(R.id.containerParcelas)
        val containerNumParc = view.findViewById<View>(R.id.containerNumParcelas) 
        val edtEntrada = view.findViewById<EditText>(R.id.edtEntradaRec)
        val edtNumParcelas = view.findViewById<EditText>(R.id.edtNumParcelasRec)
        val edtDataVenc = view.findViewById<EditText>(R.id.edtDataVencRec)

        val btnSalvar = view.findViewById<Button>(R.id.btnSalvarRec)
        val btnLimpar = view.findViewById<Button>(R.id.btnLimparRec)

        edtValorTotal.addTextChangedListener(MoneyTextWatcher(edtValorTotal))
        edtEntrada.addTextChangedListener(MoneyTextWatcher(edtEntrada))
        val fmtMoeda = NumberFormat.getCurrencyInstance(Locale("pt", "BR"))

        val c = Calendar.getInstance()
        val hoje = String.format("%02d/%02d/%04d", c.get(Calendar.DAY_OF_MONTH), c.get(Calendar.MONTH)+1, c.get(Calendar.YEAR))
        edtDataVenc.setText(hoje)

        edtDataVenc.setOnClickListener {
            val cal = Calendar.getInstance()
            DatePickerDialog(requireContext(), { _, y, m, d ->
                edtDataVenc.setText(String.format("%02d/%02d/%04d", d, m + 1, y))
            }, cal.get(Calendar.YEAR), cal.get(Calendar.MONTH), cal.get(Calendar.DAY_OF_MONTH)).show()
        }

        viewModel.listaAgenda.observe(viewLifecycleOwner) { agenda ->
            listaAgenda = agenda
            val listaDisplay = mutableListOf("Selecione um Projeto...")
            listaDisplay.addAll(agenda.map { "ID ${it.id} - ${it.clienteNome} - ${it.descricao}" })

            val adapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, listaDisplay)
            spinAgenda.adapter = adapter
        }

        spinAgenda.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(p0: AdapterView<*>?, p1: View?, pos: Int, id: Long) {
                if (pos > 0) {
                    agendaSelecionada = listaAgenda[pos - 1]
                    edtCliente.setText(agendaSelecionada?.clienteNome)
                    edtValorTotal.setText(fmtMoeda.format(agendaSelecionada?.valor))
                } else {
                    agendaSelecionada = null
                    edtCliente.setText("")
                    edtValorTotal.setText("R$ 0,00")
                }
            }
            override fun onNothingSelected(p0: AdapterView<*>?) {}
        }

        val tipos = listOf("À Vista", "Cartão (Débito)", "Cartão (Crédito)", "Entrada + Parcelas", "Saldo Aberto (Abatimento)")
        spinTipo.adapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, tipos)

        spinTipo.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(p0: AdapterView<*>?, p1: View?, pos: Int, id: Long) {
                val tipo = tipos[pos]

                if (tipo == "Entrada + Parcelas" || tipo == "Cartão (Crédito)") {
                    containerParcelas.visibility = View.VISIBLE
                    containerNumParc.visibility = View.VISIBLE
                } else if (tipo == "Saldo Aberto (Abatimento)") {
                    containerParcelas.visibility = View.VISIBLE
                    containerNumParc.visibility = View.GONE
                    edtNumParcelas.setText("1") 
                } else {
                    containerParcelas.visibility = View.GONE
                }
            }
            override fun onNothingSelected(p0: AdapterView<*>?) {}
        }

        btnSalvar.setOnClickListener {
            if (agendaSelecionada == null) {
                Toast.makeText(context, "Selecione um projeto da Agenda!", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val valorTotal = MoneyTextWatcher.parseCurrency(edtValorTotal.text.toString())
            val entrada = MoneyTextWatcher.parseCurrency(edtEntrada.text.toString())
            val numParc = edtNumParcelas.text.toString().toIntOrNull() ?: 1
            val dataVenc = edtDataVenc.text.toString()
            val tipoPag = spinTipo.selectedItem.toString()

            if (valorTotal <= 0) {
                Toast.makeText(context, "Valor inválido.", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            viewModel.salvarNovoLancamento(
                cliente = null, 
                agenda = agendaSelecionada,
                valorTotal = valorTotal,
                tipoPagamento = tipoPag,
                entrada = entrada,
                numParcelas = numParc,
                dataPrimeiroVenc = dataVenc
            )

            Toast.makeText(context, "Lançamento Salvo!", Toast.LENGTH_SHORT).show()

            spinAgenda.setSelection(0)
            edtValorTotal.setText("R$ 0,00")
            edtEntrada.setText("R$ 0,00")
        }

        btnLimpar.setOnClickListener {
            spinAgenda.setSelection(0)
        }
    }
}