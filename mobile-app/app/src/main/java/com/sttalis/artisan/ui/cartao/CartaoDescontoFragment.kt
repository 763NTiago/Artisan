package com.sttalis.artisan.ui.cartao

import android.app.DatePickerDialog
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.sttalis.artisan.R
import com.sttalis.artisan.utils.HtmlToPngGenerator
import java.util.*

class CartaoDescontoFragment : Fragment(R.layout.fragment_cartao_desconto) {

    private val viewModel: CartaoViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val edtNome = view.findViewById<EditText>(R.id.inputNomeCliente)
        val edtTel = view.findViewById<EditText>(R.id.inputTelefone)
        val edtPorc = view.findViewById<EditText>(R.id.inputPorcentagem)
        val edtCodigo = view.findViewById<EditText>(R.id.inputCodigo)
        val edtValidade = view.findViewById<EditText>(R.id.inputValidade)

        val btnSalvar = view.findViewById<Button>(R.id.btnSalvarPng)
        val btnCompartilhar = view.findViewById<Button>(R.id.btnCompartilhar)

        if (edtValidade.text.isEmpty()) {
            edtValidade.setText(viewModel.getDataValidadePadrao())
        }

        if (edtCodigo.text.isEmpty()) {
            edtCodigo.setText(viewModel.gerarCodigoPadrao(edtPorc.text.toString()))
        }

        edtPorc.addTextChangedListener(object : TextWatcher {
            override fun afterTextChanged(s: Editable?) {
                if (!s.isNullOrEmpty()) {
                    edtCodigo.setText(viewModel.gerarCodigoPadrao(s.toString()))
                }
            }
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
        })

        edtValidade.setOnClickListener {
            val cal = Calendar.getInstance()
            DatePickerDialog(requireContext(), { _, year, month, day ->
                val fmt = String.format("%02d/%02d/%04d", day, month + 1, year)
                edtValidade.setText(fmt)
            }, cal.get(Calendar.YEAR), cal.get(Calendar.MONTH), cal.get(Calendar.DAY_OF_MONTH)).show()
        }

        btnSalvar.setOnClickListener {
            gerarCartao(
                edtNome.text.toString(),
                edtPorc.text.toString(),
                edtValidade.text.toString(),
                edtCodigo.text.toString(),
                compartilhar = false
            )
        }

        btnCompartilhar.setOnClickListener {
            gerarCartao(
                edtNome.text.toString(),
                edtPorc.text.toString(),
                edtValidade.text.toString(),
                edtCodigo.text.toString(),
                compartilhar = true
            )
        }
    }

    private fun gerarCartao(nome: String, porc: String, validade: String, codigo: String, compartilhar: Boolean) {
        if (nome.isEmpty()) {
            Toast.makeText(context, "Preencha o nome do cliente", Toast.LENGTH_SHORT).show()
            return
        }

        Toast.makeText(context, "Gerando cartão...", Toast.LENGTH_SHORT).show()


        val htmlCompleto = HtmlToPngGenerator.montarHtmlCartaoSimples(
            requireContext(),
            nomeCliente = nome,
            porcentagem = porc,
            validade = validade,
            codigo = codigo
        )

        val nomeArquivo = "Cartao_${nome.replace(" ", "_")}"

        HtmlToPngGenerator.gerarPngDoHtml(requireContext(), htmlCompleto, nomeArquivo) { uri ->
            if (uri != null) {
                if (compartilhar) {
                    compartilharImagem(uri, nome, porc, validade)
                } else {
                    Toast.makeText(context, "Salvo em Imagens!", Toast.LENGTH_LONG).show()
                    visualizarImagem(uri)
                }
            } else {
                Toast.makeText(context, "Erro ao gerar imagem.", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun compartilharImagem(uri: Uri, nome: String, porc: String, validade: String) {
        val mensagem = "Olá $nome! ✨\nParabéns! Você ganhou um cartão de desconto de $porc% na Artisan!\nVálido até: $validade"

        val intent = Intent(Intent.ACTION_SEND).apply {
            type = "image/png"
            putExtra(Intent.EXTRA_STREAM, uri)
            putExtra(Intent.EXTRA_TEXT, mensagem)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        startActivity(Intent.createChooser(intent, "Enviar Cartão via..."))
    }

    private fun visualizarImagem(uri: Uri) {
        val intent = Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(uri, "image/png")
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        startActivity(intent)
    }
}