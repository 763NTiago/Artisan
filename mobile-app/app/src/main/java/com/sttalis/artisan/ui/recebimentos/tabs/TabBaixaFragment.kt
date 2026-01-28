package com.sttalis.artisan.ui.recebimentos.tabs

import android.os.Bundle
import android.text.InputType
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.sttalis.artisan.R
import com.sttalis.artisan.model.ParcelaDetalhada
import com.sttalis.artisan.ui.recebimentos.FinanceiroAdapter
import com.sttalis.artisan.ui.recebimentos.RecebimentosViewModel
import java.text.NumberFormat
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class TabBaixaFragment : Fragment() {

    private lateinit var viewModel: RecebimentosViewModel
    private lateinit var adapter: FinanceiroAdapter

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        val view = inflater.inflate(R.layout.fragment_tab_historico, container, false)
        val recycler = view.findViewById<RecyclerView>(R.id.recyclerHistoricoTab)
        recycler.layoutManager = LinearLayoutManager(context)

        adapter = FinanceiroAdapter(isHistorico = false) { parcela ->
            abrirDialogoSimples(parcela)
        }
        recycler.adapter = adapter
        return view
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        viewModel = ViewModelProvider(requireParentFragment())[RecebimentosViewModel::class.java]

        viewModel.listaPendentes.observe(viewLifecycleOwner) { lista ->
            adapter.atualizarLista(lista.filter { it.valorRestante > 0.01 })
        }
        viewModel.carregarDados()
    }

    private fun abrirDialogoSimples(parcela: ParcelaDetalhada) {
        val ctx = requireContext()
        val builder = AlertDialog.Builder(ctx)

        builder.setTitle("Realizar Pagamento")

        val fmt = NumberFormat.getCurrencyInstance(Locale("pt", "BR"))
        builder.setMessage("Cliente: ${parcela.cliente}\nValor Restante: ${fmt.format(parcela.valorRestante)}")

        val input = EditText(ctx)
        input.inputType = InputType.TYPE_CLASS_NUMBER or InputType.TYPE_NUMBER_FLAG_DECIMAL
        input.setText(String.format(Locale.US, "%.2f", parcela.valorRestante))
        builder.setView(input)

        builder.setPositiveButton("Confirmar") { _, _ ->
            val digitado = input.text.toString().replace(",", ".").toDoubleOrNull()
            if (digitado != null && digitado > 0) {
                val totalAcumulado = parcela.valorPago + digitado
                val hoje = SimpleDateFormat("dd/MM/yyyy", Locale("pt", "BR")).format(Date())

                viewModel.realizarBaixa(parcela, digitado, hoje) 
                Toast.makeText(ctx, "Sucesso!", Toast.LENGTH_SHORT).show()
            }
        }
        builder.setNegativeButton("Cancelar", null)
        builder.show()
    }
}