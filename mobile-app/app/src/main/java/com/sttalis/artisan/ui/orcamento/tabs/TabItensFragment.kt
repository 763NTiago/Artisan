package com.sttalis.artisan.ui.orcamento.tabs

import android.app.AlertDialog
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.sttalis.artisan.R
import com.sttalis.artisan.model.ItemOrcamento
import com.sttalis.artisan.ui.orcamento.ItemOrcamentoAdapter
import com.sttalis.artisan.ui.orcamento.OrcamentoViewModel
import java.text.NumberFormat
import java.util.Locale

class TabItensFragment : Fragment(R.layout.fragment_tab_itens) {

    private val viewModel: OrcamentoViewModel by activityViewModels()
    private lateinit var adapter: ItemOrcamentoAdapter

    private var itemSelecionado: ItemOrcamento? = null

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val recycler = view.findViewById<RecyclerView>(R.id.recyclerItensTab)
        val btnAdd = view.findViewById<Button>(R.id.btnAdicionarItem)
        val btnEdit = view.findViewById<Button>(R.id.btnEditarItem)
        val btnRem = view.findViewById<Button>(R.id.btnRemoverItem)
        val txtTotal = view.findViewById<TextView>(R.id.txtTotalOrcamento)

        adapter = ItemOrcamentoAdapter { item ->
            itemSelecionado = item
        }

        recycler.layoutManager = LinearLayoutManager(context)
        recycler.adapter = adapter

        viewModel.itens.observe(viewLifecycleOwner) { lista ->
            adapter.atualizarLista(lista)

            val total = lista.sumOf { it.valorTotal }
            val fmt = NumberFormat.getCurrencyInstance(Locale("pt", "BR"))
            txtTotal.text = "TOTAL ORÇAMENTO: ${fmt.format(total)}"
        }

        btnAdd.setOnClickListener {
            abrirDialogItem(null)
        }

        btnEdit.setOnClickListener {
            if (itemSelecionado != null) {
                abrirDialogItem(itemSelecionado)
            } else {
                Toast.makeText(context, "Selecione um item na lista para editar.", Toast.LENGTH_SHORT).show()
            }
        }

        btnRem.setOnClickListener {
            val item = itemSelecionado
            if (item != null) {
                AlertDialog.Builder(requireContext())
                    .setTitle("Remover Item")
                    .setMessage("Deseja remover '${item.descricao}'?")
                    .setPositiveButton("Sim") { _, _ ->
                        viewModel.removerItem(item)
                        itemSelecionado = null
                        Toast.makeText(context, "Item removido.", Toast.LENGTH_SHORT).show()
                    }
                    .setNegativeButton("Não", null)
                    .show()
            } else {
                Toast.makeText(context, "Selecione um item para remover.", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun abrirDialogItem(itemParaEditar: ItemOrcamento?) {
        val dialogView = LayoutInflater.from(requireContext()).inflate(R.layout.dialog_add_item, null)

        val inputQtd = dialogView.findViewById<EditText>(R.id.inputQuantidade)
        val inputAmb = dialogView.findViewById<EditText>(R.id.inputAmbiente)
        val inputValor = dialogView.findViewById<EditText>(R.id.inputValorUnit)
        val inputDesc = dialogView.findViewById<EditText>(R.id.inputDescricao)
        val lblTitulo = dialogView.findViewById<TextView>(R.id.lblTituloDialog)

        inputValor.addTextChangedListener(com.sttalis.artisan.utils.MoneyTextWatcher(inputValor))

        val fmt = NumberFormat.getCurrencyInstance(Locale("pt", "BR"))

        if (itemParaEditar != null) {
            lblTitulo.text = "Editar Item"
            val qtdDisplay = if (itemParaEditar.quantidade % 1.0 == 0.0)
                itemParaEditar.quantidade.toInt().toString()
            else
                itemParaEditar.quantidade.toString()
            inputQtd.setText(qtdDisplay)

            inputAmb.setText(itemParaEditar.ambiente)
            inputValor.setText(fmt.format(itemParaEditar.valorUnitario))
            inputDesc.setText(itemParaEditar.descricao)
        } else {
            inputValor.setText("R$ 0,00")
        }

        AlertDialog.Builder(requireContext())
            .setView(dialogView)
            .setPositiveButton(if (itemParaEditar == null) "Adicionar" else "Salvar Alterações") { _, _ ->
                try {
                    val qtdDouble = inputQtd.text.toString().toDoubleOrNull() ?: 1.0
                    val amb = inputAmb.text.toString()
                    val valorUnitDouble = com.sttalis.artisan.utils.MoneyTextWatcher.parseCurrency(inputValor.text.toString())
                    val desc = inputDesc.text.toString()

                    if (desc.isEmpty()) {
                        Toast.makeText(context, "A descrição é obrigatória.", Toast.LENGTH_SHORT).show()
                        return@setPositiveButton
                    }

                    val totalDouble = qtdDouble * valorUnitDouble
                    val idFinal = itemParaEditar?.id ?: System.currentTimeMillis()

                    val valorUnitString = fmt.format(valorUnitDouble) 
                    val totalString = fmt.format(totalDouble)         
                    val qtdString = if (qtdDouble % 1.0 == 0.0) qtdDouble.toInt().toString() else qtdDouble.toString()

                    val novoItem = ItemOrcamento(
                        id = idFinal,
                        _quantidade = qtdString,      
                        ambiente = amb,
                        descricao = desc,
                        _valorUnitario = valorUnitString, 
                        _valorTotal = totalString         
                    )

                    if (itemParaEditar == null) {
                        viewModel.adicionarItem(novoItem)
                    } else {
                        viewModel.removerItem(itemParaEditar)
                        viewModel.adicionarItem(novoItem)
                        itemSelecionado = null
                    }

                } catch (e: Exception) {
                    Toast.makeText(context, "Erro: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
            .setNegativeButton("Cancelar", null)
            .show()
    }
}