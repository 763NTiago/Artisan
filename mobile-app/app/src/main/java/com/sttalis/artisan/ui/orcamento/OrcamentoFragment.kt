package com.sttalis.artisan.ui.orcamento

import android.os.Bundle
import android.view.View
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.floatingactionbutton.FloatingActionButton
import com.sttalis.artisan.R

class OrcamentoFragment : Fragment(R.layout.fragment_orcamentos) {

    private val viewModel: OrcamentoViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val recycler = view.findViewById<RecyclerView>(R.id.recyclerOrcamentos)
        val txtVazio = view.findViewById<View>(R.id.txtVazio)
        val fab = view.findViewById<FloatingActionButton>(R.id.fabNovoOrcamento)

        val adapter = OrcamentoAdapter { orcamentoClicado ->
            viewModel.carregarOrcamento(orcamentoClicado)
            findNavController().navigate(R.id.nav_criar_orcamento)
        }

        recycler.layoutManager = LinearLayoutManager(context)
        recycler.adapter = adapter
        viewModel.listaHistorico.observe(viewLifecycleOwner) { lista ->
            adapter.submitList(lista)

            if (lista.isEmpty()) {
                txtVazio.visibility = View.VISIBLE
                recycler.visibility = View.GONE
            } else {
                txtVazio.visibility = View.GONE
                recycler.visibility = View.VISIBLE
            }
        }

        fab.setOnClickListener {
            viewModel.limparEstado()
            findNavController().navigate(R.id.nav_criar_orcamento)
        }

        viewModel.carregarHistorico()
    }
}