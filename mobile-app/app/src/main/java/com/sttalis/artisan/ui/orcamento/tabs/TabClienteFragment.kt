package com.sttalis.artisan.ui.orcamento.tabs

import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.EditText
import android.widget.Spinner
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.lifecycle.lifecycleScope
import com.sttalis.artisan.R
import com.sttalis.artisan.data.AppDatabase
import com.sttalis.artisan.model.Cliente
import com.sttalis.artisan.ui.orcamento.OrcamentoViewModel
import kotlinx.coroutines.launch

class TabClienteFragment : Fragment(R.layout.fragment_tab_cliente) {

    private val viewModel: OrcamentoViewModel by activityViewModels()
    private val db by lazy { AppDatabase.getDatabase(requireContext()) }
    private var isUpdating = false

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val spinner = view.findViewById<Spinner>(R.id.spinnerClientesTab)
        val inputNome = view.findViewById<EditText>(R.id.inputNomeTab)
        val inputEnd = view.findViewById<EditText>(R.id.inputEnderecoTab)
        val inputCpf = view.findViewById<EditText>(R.id.inputCpfTab)
        val inputTel = view.findViewById<EditText>(R.id.inputTelefoneTab)
        val inputEmail = view.findViewById<EditText>(R.id.inputEmailTab)

        lifecycleScope.launch {
            try {
                val clientes = db.clienteDao().listarTodos()
                if (clientes.isNotEmpty()) {
                    val listaNomes = mutableListOf("Selecione um cliente cadastrado...")
                    listaNomes.addAll(clientes.map { it.nome })

                    val adapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_item, listaNomes)
                    adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
                    spinner.adapter = adapter

                    spinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
                        override fun onItemSelected(p0: AdapterView<*>?, p1: View?, pos: Int, id: Long) {
                            if (pos > 0) {
                                isUpdating = true
                                val cliente = clientes[pos - 1]
                                viewModel.setCliente(cliente)
                                isUpdating = false
                            }
                        }
                        override fun onNothingSelected(p0: AdapterView<*>?) {}
                    }
                }
            } catch (e: Exception) { e.printStackTrace() }
        }

        viewModel.cliente.observe(viewLifecycleOwner) { cliente ->
            if (cliente != null && !isUpdating) {
                atualizarCampoSeNecessario(inputNome, cliente.nome)
                atualizarCampoSeNecessario(inputEnd, cliente.endereco)
                atualizarCampoSeNecessario(inputCpf, cliente.cpfCnpj)
                atualizarCampoSeNecessario(inputTel, cliente.telefone)
                atualizarCampoSeNecessario(inputEmail, cliente.email)
            }
        }

        val watcher = object : TextWatcher {
            override fun afterTextChanged(s: Editable?) {
                if (isUpdating) return
                isUpdating = true
                val tempCliente = Cliente(
                    id = viewModel.cliente.value?.id ?: 0,
                    nome = inputNome.text.toString(),
                    endereco = inputEnd.text.toString(),
                    cpfCnpj = inputCpf.text.toString(),
                    telefone = inputTel.text.toString(),
                    email = inputEmail.text.toString()
                )
                viewModel.setCliente(tempCliente)
                isUpdating = false
            }
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
        }

        inputNome.addTextChangedListener(watcher)
        inputEnd.addTextChangedListener(watcher)
        inputCpf.addTextChangedListener(watcher)
        inputTel.addTextChangedListener(watcher)
        inputEmail.addTextChangedListener(watcher)
    }

    private fun atualizarCampoSeNecessario(editText: EditText, novoValor: String?) {
        val valorAtual = editText.text.toString()
        val valorFinal = novoValor ?: ""
        if (valorAtual != valorFinal) {
            editText.setText(valorFinal)
            if (editText.hasFocus()) {
                editText.setSelection(valorFinal.length)
            }
        }
    }
}