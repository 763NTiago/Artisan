package com.sttalis.artisan.ui.orcamento.tabs

import android.app.AlertDialog
import android.graphics.Color
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.sttalis.artisan.R
import com.sttalis.artisan.data.AppDatabase
import com.sttalis.artisan.model.Orcamento
import com.sttalis.artisan.ui.orcamento.OrcamentoViewModel
import kotlinx.coroutines.launch
import java.text.NumberFormat
import java.util.Locale

class TabHistoricoFragment : Fragment(R.layout.fragment_tab_historico) {

    private val viewModel: OrcamentoViewModel by activityViewModels()
    private val db by lazy { AppDatabase.getDatabase(requireContext()) }

    private lateinit var adapter: HistoricoAdapter
    private var orcamentoSelecionado: Orcamento? = null

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val recycler = view.findViewById<RecyclerView>(R.id.recyclerHistoricoTab)
        val btnCarregar = view.findViewById<Button>(R.id.btnCarregarHist)
        val btnEditar = view.findViewById<Button>(R.id.btnEditarHist)
        val btnRemover = view.findViewById<Button>(R.id.btnRemoverHist)
        val btnAtualizar = view.findViewById<Button>(R.id.btnAtualizarLista)

        adapter = HistoricoAdapter { item ->
            orcamentoSelecionado = item
        }

        recycler.layoutManager = LinearLayoutManager(context)
        recycler.adapter = adapter

        carregarDados()

        viewModel.orcamentoEmEdicaoId.observe(viewLifecycleOwner) { idEmEdicao ->
            if (idEmEdicao != null && idEmEdicao > 0) {
                adapter.selecionarPorId(idEmEdicao)
                orcamentoSelecionado = adapter.getSelectedItem()
            }
        }

        btnAtualizar.setOnClickListener { carregarDados() }

        btnCarregar.setOnClickListener {
            val item = orcamentoSelecionado
            if (item != null) {
                viewModel.carregarOrcamento(item)
                Toast.makeText(context, "Orçamento Carregado!", Toast.LENGTH_SHORT).show()
                viewModel.mudarAba(0)
            } else {
                Toast.makeText(context, "Selecione um item.", Toast.LENGTH_SHORT).show()
            }
        }

        btnEditar.setOnClickListener {
            btnCarregar.performClick()
        }

        btnRemover.setOnClickListener {
            val item = orcamentoSelecionado
            if (item != null) {
                AlertDialog.Builder(requireContext())
                    .setTitle("Excluir")
                    .setMessage("Deseja excluir permanentemente o Orçamento ID ${item.id}?")
                    .setPositiveButton("Sim") { _, _ ->
                        lifecycleScope.launch {
                            try {
                                db.orcamentoDao().deletar(item)
                                carregarDados()
                                orcamentoSelecionado = null
                                Toast.makeText(context, "Removido!", Toast.LENGTH_SHORT).show()
                            } catch (e: Exception) {
                                Toast.makeText(context, "Erro: ${e.message}", Toast.LENGTH_SHORT).show()
                            }
                        }
                    }
                    .setNegativeButton("Não", null)
                    .show()
            }
        }
    }

    private fun carregarDados() {
        lifecycleScope.launch {
            try {
                val lista = db.orcamentoDao().listarTodos()
                adapter.lista = lista
                adapter.notifyDataSetChanged()

                val atualId = viewModel.orcamentoEmEdicaoId.value
                if (atualId != null) adapter.selecionarPorId(atualId)

            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    inner class HistoricoAdapter(private val onClick: (Orcamento) -> Unit) : RecyclerView.Adapter<HistoricoAdapter.VH>() {
        var lista = emptyList<Orcamento>()
        private var selectedPos = RecyclerView.NO_POSITION

        fun selecionarPorId(id: Long) {
            val index = lista.indexOfFirst { it.id == id }
            if (index != -1) {
                val old = selectedPos
                selectedPos = index
                notifyItemChanged(old)
                notifyItemChanged(selectedPos)
                orcamentoSelecionado = lista[index]
            }
        }

        fun getSelectedItem(): Orcamento? {
            return if (selectedPos != RecyclerView.NO_POSITION && selectedPos < lista.size) lista[selectedPos] else null
        }

        inner class VH(v: View) : RecyclerView.ViewHolder(v) {
            val txtId: TextView = v.findViewById(R.id.txtIdHist)
            val txtData: TextView = v.findViewById(R.id.txtDataHist)
            val txtCliente: TextView = v.findViewById(R.id.txtClienteHist)
            val txtValor: TextView = v.findViewById(R.id.txtValorHist)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
            val v = LayoutInflater.from(parent.context).inflate(R.layout.item_historico_table, parent, false)
            return VH(v)
        }

        override fun onBindViewHolder(holder: VH, position: Int) {
            val item = lista[position]
            holder.txtId.text = item.id.toString()
            holder.txtData.text = item.dataCriacao ?: ""
            holder.txtCliente.text = item.clienteNome ?: "Sem Nome"

            val fmt = NumberFormat.getCurrencyInstance(Locale("pt", "BR"))
            holder.txtValor.text = fmt.format(item.valorTotalFinal)

            if (selectedPos == position) {
                holder.itemView.setBackgroundColor(Color.parseColor("#E3F2FD"))
            } else {
                holder.itemView.setBackgroundColor(Color.WHITE)
            }

            holder.itemView.setOnClickListener {
                val old = selectedPos
                val currentPos = holder.adapterPosition 
                if (currentPos != RecyclerView.NO_POSITION) {
                    selectedPos = currentPos
                    notifyItemChanged(old)
                    notifyItemChanged(selectedPos)
                    onClick(item)
                }
            }
        }

        override fun getItemCount() = lista.size
    }
}