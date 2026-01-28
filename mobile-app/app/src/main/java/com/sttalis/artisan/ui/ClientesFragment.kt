package com.sttalis.artisan.ui

import android.app.AlertDialog
import android.os.Bundle
import android.view.View
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.floatingactionbutton.FloatingActionButton
import com.sttalis.artisan.R
import com.sttalis.artisan.data.AppDatabase
import com.sttalis.artisan.model.Cliente
import kotlinx.coroutines.launch

class ClientesFragment : Fragment(R.layout.fragment_clientes) {

    private lateinit var adapter: ClienteAdapter
    private val db by lazy { AppDatabase.getDatabase(requireContext()) }
    private lateinit var recycler: RecyclerView
    private lateinit var txtVazio: View

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        recycler = view.findViewById(R.id.recyclerClientes)
        val fab = view.findViewById<FloatingActionButton>(R.id.fabAdicionar)
        txtVazio = view.findViewById(R.id.txtVazio)

        adapter = ClienteAdapter { clienteClicado ->
            mostrarDialogNovoCliente(clienteClicado)
        }

        recycler.layoutManager = LinearLayoutManager(context)
        recycler.adapter = adapter

        carregarClientes()

        fab.setOnClickListener {
            mostrarDialogNovoCliente(null) 
        }
    }

    private fun carregarClientes() {
        lifecycleScope.launch {
            try {
                val listaClientes = db.clienteDao().listarTodos()
                if (listaClientes.isEmpty()) {
                    txtVazio.visibility = View.VISIBLE
                    recycler.visibility = View.GONE
                } else {
                    txtVazio.visibility = View.GONE
                    recycler.visibility = View.VISIBLE
                    adapter.submitList(listaClientes)
                }
            } catch (e: Exception) {
                Toast.makeText(context, "Erro ao carregar clientes", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun mostrarDialogNovoCliente(clienteParaEditar: Cliente?) {
        val builder = AlertDialog.Builder(requireContext())
        builder.setTitle(if (clienteParaEditar == null) "Novo Cliente" else "Editar Cliente")

        val layout = LinearLayout(requireContext())
        layout.orientation = LinearLayout.VERTICAL
        layout.setPadding(50, 40, 50, 10)

        val inputNome = EditText(requireContext())
        inputNome.hint = "Nome Completo"
        layout.addView(inputNome)

        val inputTelefone = EditText(requireContext())
        inputTelefone.hint = "Telefone"
        layout.addView(inputTelefone)

        val inputEmail = EditText(requireContext())
        inputEmail.hint = "Email"
        layout.addView(inputEmail)

        val inputEndereco = EditText(requireContext())
        inputEndereco.hint = "Endereço"
        layout.addView(inputEndereco)

        val inputCpf = EditText(requireContext())
        inputCpf.hint = "CPF / CNPJ"
        layout.addView(inputCpf)

        if (clienteParaEditar != null) {
            inputNome.setText(clienteParaEditar.nome)
            inputTelefone.setText(clienteParaEditar.telefone)
            inputEmail.setText(clienteParaEditar.email)
            inputEndereco.setText(clienteParaEditar.endereco)
            inputCpf.setText(clienteParaEditar.cpfCnpj)
        }

        builder.setView(layout)

        builder.setPositiveButton("Salvar") { _, _ ->
            val nome = inputNome.text.toString()
            val telefone = inputTelefone.text.toString()
            val email = inputEmail.text.toString()
            val endereco = inputEndereco.text.toString()
            val cpf = inputCpf.text.toString()

            if (nome.isNotEmpty()) {
                val clienteFinal = if (clienteParaEditar == null) {
                    Cliente(nome = nome, telefone = telefone, email = email, endereco = endereco, cpfCnpj = cpf)
                } else {
                    clienteParaEditar.copy(
                        nome = nome,
                        telefone = telefone,
                        email = email,
                        endereco = endereco,
                        cpfCnpj = cpf
                    )
                }
                salvarCliente(clienteFinal, isEdicao = clienteParaEditar != null)
            } else {
                Toast.makeText(context, "Nome é obrigatório", Toast.LENGTH_SHORT).show()
            }
        }

        builder.setNegativeButton("Cancelar", null)
        builder.show()
    }

    private fun salvarCliente(cliente: Cliente, isEdicao: Boolean) {
        lifecycleScope.launch {
            try {
                if (isEdicao) {
                    db.clienteDao().atualizar(cliente)
                    Toast.makeText(context, "Cliente atualizado!", Toast.LENGTH_SHORT).show()
                } else {
                    db.clienteDao().inserir(cliente)
                    Toast.makeText(context, "Cliente criado!", Toast.LENGTH_SHORT).show()
                }
                carregarClientes()
            } catch (e: Exception) {
                Toast.makeText(context, "Erro ao salvar: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }
}