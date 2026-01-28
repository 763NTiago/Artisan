package com.sttalis.artisan.ui.recebimentos.tabs

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.sttalis.artisan.R
import com.sttalis.artisan.ui.recebimentos.FinanceiroAdapter
import com.sttalis.artisan.ui.recebimentos.RecebimentosViewModel

class TabHistoricoFragment : Fragment() {

    private lateinit var viewModel: RecebimentosViewModel
    private lateinit var adapter: FinanceiroAdapter

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        val view = inflater.inflate(R.layout.fragment_tab_historico, container, false)
        val recycler = view.findViewById<RecyclerView>(R.id.recyclerHistoricoTab)
        recycler.layoutManager = LinearLayoutManager(context)

        adapter = FinanceiroAdapter(isHistorico = true) { parcela ->
            Toast.makeText(context, "Recebido: ${parcela.valorPago}", Toast.LENGTH_SHORT).show()
        }
        recycler.adapter = adapter

        view.findViewById<Button>(R.id.btnAtualizarLista)?.setOnClickListener {
            viewModel.carregarDados()
        }

        return view
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        viewModel = ViewModelProvider(requireParentFragment())[RecebimentosViewModel::class.java]

        viewModel.listaHistorico.observe(viewLifecycleOwner) { lista ->
            adapter.atualizarLista(lista.filter { it.valorPago > 0.01 })
        }
        viewModel.carregarDados()
    }

    override fun onResume() {
        super.onResume()
        viewModel.carregarDados()
    }
}