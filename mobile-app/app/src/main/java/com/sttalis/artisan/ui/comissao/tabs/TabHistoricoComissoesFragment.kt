package com.sttalis.artisan.ui.comissao.tabs

import android.app.AlertDialog
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.sttalis.artisan.R
import com.sttalis.artisan.ui.comissao.ComissaoAdapter
import com.sttalis.artisan.ui.comissao.ComissoesViewModel

class TabHistoricoComissoesFragment : Fragment() {

    private lateinit var viewModel: ComissoesViewModel
    private lateinit var adapter: ComissaoAdapter

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.fragment_tab_historico_comissoes, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewModel = ViewModelProvider(requireParentFragment())[ComissoesViewModel::class.java]

        val recycler = view.findViewById<RecyclerView>(R.id.recyclerHistoricoComissoes)

        adapter = ComissaoAdapter { item ->
            AlertDialog.Builder(requireContext())
                .setTitle("Histórico")
                .setMessage("Deseja remover este registro do histórico?")
                .setPositiveButton("Remover") { _, _ ->
                    viewModel.deletarComissao(item)
                    Toast.makeText(context, "Registro removido.", Toast.LENGTH_SHORT).show()
                }
                .setNegativeButton("Cancelar", null)
                .show()
        }

        recycler.layoutManager = LinearLayoutManager(context)
        recycler.adapter = adapter

        viewModel.listaComissoesPagas.observe(viewLifecycleOwner) { lista ->
            adapter.lista = lista
            adapter.notifyDataSetChanged()
        }
    }
}