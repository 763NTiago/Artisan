package com.sttalis.artisan.ui.orcamento.tabs

import android.app.AlertDialog
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.LayoutInflater
import android.view.View
import android.widget.*
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.sttalis.artisan.R
import com.sttalis.artisan.data.AppDatabase
import com.sttalis.artisan.model.MaterialIncluso
import com.sttalis.artisan.ui.orcamento.OrcamentoViewModel
import kotlinx.coroutines.launch

class TabTermosFragment : Fragment(R.layout.fragment_tab_termos) {

    private val viewModel: OrcamentoViewModel by activityViewModels()
    private val db by lazy { AppDatabase.getDatabase(requireContext()) }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val inputObs = view.findViewById<EditText>(R.id.inputObservacoes)
        val inputPag = view.findViewById<EditText>(R.id.inputPagamento)
        val btnEditarMateriais = view.findViewById<Button>(R.id.btnEditarMateriaisInclusos)

        val obsPadrao = "Ex: Todos os puxadores conforme projeto, corrediças invisíveis, dobradiças em inox com amortecimento."
        val pagPadrao = "Orçamento válido por: 20 dias.\n" +
                "Prazo de entrega: 60 dias úteis.\n\n" +
                "--- CONDIÇÕES DE PAGAMENTO ---\n" +
                "À VISTA: 50% entrada, 50% na entrega.\n" +
                "A PRAZO: 40% entrada, restante em 6x no cheque."

        if (viewModel.observacoes.value.isNullOrEmpty()) {
            inputObs.setText(obsPadrao)
            viewModel.setObservacoes(obsPadrao)
        } else {
            inputObs.setText(viewModel.observacoes.value)
        }

        if (viewModel.condicoesPagamento.value.isNullOrEmpty()) {
            inputPag.setText(pagPadrao)
            viewModel.setCondicoesPagamento(pagPadrao)
        } else {
            inputPag.setText(viewModel.condicoesPagamento.value)
        }

        val watcher = object : TextWatcher {
            override fun afterTextChanged(s: Editable?) {
                viewModel.setObservacoes(inputObs.text.toString())
                viewModel.setCondicoesPagamento(inputPag.text.toString())
            }
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
        }
        inputObs.addTextChangedListener(watcher)
        inputPag.addTextChangedListener(watcher)

        btnEditarMateriais.setOnClickListener {
            abrirDialogEditorMateriais(inputObs)
        }
    }

    private fun abrirDialogEditorMateriais(inputObs: EditText) {
        val dialogView = LayoutInflater.from(requireContext()).inflate(R.layout.dialog_editor_materiais, null)

        val spinMateriais = dialogView.findViewById<Spinner>(R.id.spinMaterialDialog)
        val edtDesc = dialogView.findViewById<EditText>(R.id.edtDescMaterialDialog)
        val btnAdd = dialogView.findViewById<Button>(R.id.btnAddListaDialog)
        val recycler = dialogView.findViewById<RecyclerView>(R.id.recyclerMateriaisDialog)
        val btnRemover = dialogView.findViewById<Button>(R.id.btnRemoverDialog)
        val btnConfirmar = dialogView.findViewById<Button>(R.id.btnConfirmarDialog)

        val adapterLista = MaterialInclusoAdapter { }
        recycler.layoutManager = LinearLayoutManager(context)
        recycler.adapter = adapterLista

        val textoAtual = inputObs.text.toString()
        val regex = Regex("--- MATERIAIS INCLUSOS ---\\n(.*?)\\n--- FIM MATERIAIS ---", setOf(RegexOption.DOT_MATCHES_ALL, RegexOption.IGNORE_CASE))

        val match = regex.find(textoAtual)
        if (match != null) {
            val blocoMateriais = match.groupValues[1].trim()
            val linhas = blocoMateriais.split("\n")

            for (linha in linhas) {
                if (linha.isBlank() || linha.contains("Nenhum material")) continue
                val partes = linha.split("\t\t", limit = 2)
                val nome = partes.getOrNull(0)?.trim() ?: ""
                val desc = partes.getOrNull(1)?.trim() ?: ""

                if (nome.isNotEmpty()) {
                    adapterLista.lista.add(MaterialIncluso(nome, desc))
                }
            }
            adapterLista.notifyDataSetChanged()
        }

        lifecycleScope.launch {
            try {
                val materiaisDb = db.materialDao().listarTodos()

                if (materiaisDb.isNotEmpty()) {
                    val nomes = materiaisDb.map { it.nome }
                    val spinnerAdapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, nomes)
                    spinMateriais.adapter = spinnerAdapter

                    spinMateriais.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
                        override fun onItemSelected(p0: AdapterView<*>?, p1: View?, pos: Int, id: Long) {
                            val selecionado = materiaisDb[pos]
                            edtDesc.setText(selecionado.descricao ?: "")
                        }
                        override fun onNothingSelected(p0: AdapterView<*>?) {}
                    }
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }

        val dialog = AlertDialog.Builder(requireContext())
            .setView(dialogView)
            .create()

        btnAdd.setOnClickListener {
            val nome = spinMateriais.selectedItem?.toString()
            val desc = edtDesc.text.toString()

            if (nome != null) {
                adapterLista.lista.add(MaterialIncluso(nome, desc))
                adapterLista.notifyDataSetChanged()
            }
        }

        btnRemover.setOnClickListener {
            val sel = adapterLista.selecionado
            if (sel != null) {
                adapterLista.lista.remove(sel)
                adapterLista.selecionado = null
                adapterLista.notifyDataSetChanged()
            } else {
                Toast.makeText(context, "Selecione um item na lista para remover.", Toast.LENGTH_SHORT).show()
            }
        }

        btnConfirmar.setOnClickListener {
            val textoGerado = gerarTextoMateriais(adapterLista.lista)
            inserirTextoNasObservacoes(inputObs, textoGerado)
            dialog.dismiss()
        }

        dialog.show()
    }

    private fun gerarTextoMateriais(lista: List<MaterialIncluso>): String {
        val sb = StringBuilder()
        sb.append("\n\n--- MATERIAIS INCLUSOS ---\n")

        if (lista.isEmpty()) {
            sb.append("Nenhum material específico incluso.\n")
        } else {
            for (item in lista) {
                sb.append("${item.nome}\t\t${item.descricao}\n")
            }
        }
        sb.append("--- FIM MATERIAIS ---\n\n")
        return sb.toString()
    }

    private fun inserirTextoNasObservacoes(editText: EditText, novoTexto: String) {
        val textoAtual = editText.text.toString()
        val regex = Regex("--- MATERIAIS INCLUSOS ---.*--- FIM MATERIAIS ---", setOf(RegexOption.DOT_MATCHES_ALL, RegexOption.IGNORE_CASE))

        val textoFinal = if (regex.containsMatchIn(textoAtual)) {
            textoAtual.replace(regex, novoTexto.trim())
        } else {
            textoAtual + novoTexto
        }
        editText.setText(textoFinal)
    }
}