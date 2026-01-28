package com.sttalis.artisan.ui.orcamento.tabs

import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.sttalis.artisan.R
import com.sttalis.artisan.model.Material

class TabMateriaisFragment : Fragment(R.layout.fragment_tab_materiais) {

    private val viewModel: MateriaisViewModel by viewModels()
    private lateinit var adapter: MaterialAdapter

    private var materialEmEdicao: Material? = null

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val edtNome = view.findViewById<EditText>(R.id.edtNomeMaterial)
        val edtDesc = view.findViewById<EditText>(R.id.edtDescMaterial)
        val btnSalvar = view.findViewById<Button>(R.id.btnSalvarMaterial)
        val btnCancelar = view.findViewById<Button>(R.id.btnCancelarEdicao)
        val recycler = view.findViewById<RecyclerView>(R.id.recyclerMateriais)

        adapter = MaterialAdapter(
            onClick = { material ->
                preencherFormulario(material, edtNome, edtDesc, btnSalvar, btnCancelar)
            },
            onDelete = { material ->
                confirmarExclusao(material)
            }
        )

        recycler.layoutManager = LinearLayoutManager(context)
        recycler.adapter = adapter

        viewModel.listaMateriais.observe(viewLifecycleOwner) { lista ->
            adapter.lista = lista
            adapter.notifyDataSetChanged()
        }

        viewModel.carregarMateriais()

        btnSalvar.setOnClickListener {
            val nome = edtNome.text.toString()
            val desc = edtDesc.text.toString()

            if (nome.isNotEmpty()) {
                val novoMaterial = Material(
                    id = materialEmEdicao?.id ?: 0, 
                    nome = nome,
                    descricao = desc,
                    precoUnitario = 0.0,
                    unidade = "un"
                )

                viewModel.salvar(novoMaterial)

                limparFormulario(edtNome, edtDesc, btnSalvar, btnCancelar)
                Toast.makeText(context, "Material Salvo!", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(context, "O nome é obrigatório.", Toast.LENGTH_SHORT).show()
            }
        }

        btnCancelar.setOnClickListener {
            limparFormulario(edtNome, edtDesc, btnSalvar, btnCancelar)
        }
    }

    private fun preencherFormulario(
        material: Material,
        edtNome: EditText,
        edtDesc: EditText,
        btnSalvar: Button,
        btnCancelar: Button
    ) {
        materialEmEdicao = material
        edtNome.setText(material.nome)
        edtDesc.setText(material.descricao)

        btnSalvar.text = "✔️ ATUALIZAR MATERIAL"
        btnCancelar.visibility = View.VISIBLE
    }

    private fun limparFormulario(
        edtNome: EditText,
        edtDesc: EditText,
        btnSalvar: Button,
        btnCancelar: Button
    ) {
        materialEmEdicao = null
        edtNome.text.clear()
        edtDesc.text.clear()

        btnSalvar.text = "✔️ SALVAR NOVO MATERIAL"
        btnCancelar.visibility = View.GONE

        edtNome.clearFocus()
    }

    private fun confirmarExclusao(material: Material) {
        AlertDialog.Builder(requireContext())
            .setTitle("Remover Material")
            .setMessage("Tem certeza que deseja remover '${material.nome}'?")
            .setPositiveButton("Sim") { _, _ ->
                viewModel.deletar(material)
                Toast.makeText(context, "Removido.", Toast.LENGTH_SHORT).show()

                if (materialEmEdicao?.id == material.id) {
                    materialEmEdicao = null
                }
            }
            .setNegativeButton("Não", null)
            .show()
    }
}