package com.sttalis.artisan.ui.comissao.tabs

import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.sttalis.artisan.R
import com.sttalis.artisan.ui.comissao.ArquitetoAdapter
import com.sttalis.artisan.ui.comissao.ComissoesViewModel

class TabArquitetosFragment : Fragment(R.layout.fragment_tab_arquitetos) {

    private lateinit var viewModel: ComissoesViewModel
    private lateinit var adapter: ArquitetoAdapter

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewModel = ViewModelProvider(requireParentFragment())[ComissoesViewModel::class.java]

        val edtNome = view.findViewById<EditText>(R.id.edtNomeArq)
        val edtDia = view.findViewById<EditText>(R.id.edtDiaPagArq)
        val edtPct = view.findViewById<EditText>(R.id.edtPctArq) 
        val btnSalvar = view.findViewById<Button>(R.id.btnSalvarArq)
        val recycler = view.findViewById<RecyclerView>(R.id.recyclerArquitetos)

        adapter = ArquitetoAdapter { item ->
            AlertDialog.Builder(requireContext())
                .setTitle("Remover")
                .setMessage("Remover parceiro ${item.nome}?")
                .setPositiveButton("Sim") { _, _ -> viewModel.deletarArquiteto(item) }
                .setNegativeButton("Não", null)
                .show()
        }

        recycler.layoutManager = LinearLayoutManager(context)
        recycler.adapter = adapter

        viewModel.listaArquitetos.observe(viewLifecycleOwner) { lista ->
            adapter.lista = lista
            adapter.notifyDataSetChanged()
        }

        btnSalvar.setOnClickListener {
            val nome = edtNome.text.toString()
            val diaStr = edtDia.text.toString()
            val pctStr = edtPct.text.toString()

            val dia = diaStr.toIntOrNull() ?: 0
            val pct = pctStr.toDoubleOrNull() ?: 0.0

            if (nome.isNotEmpty()) {
                if (dia < 1 || dia > 31) {
                    Toast.makeText(context, "O dia deve ser entre 1 e 31.", Toast.LENGTH_SHORT).show()
                    return@setOnClickListener
                }

                viewModel.salvarArquiteto(nome, dia, pct)

                edtNome.text.clear()
                edtDia.setText("10")
                edtPct.setText("") 
                edtNome.requestFocus()

                Toast.makeText(context, "Parceiro Salvo!", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(context, "Digite o nome do Arquiteto.", Toast.LENGTH_SHORT).show()
            }
        }
    }
}