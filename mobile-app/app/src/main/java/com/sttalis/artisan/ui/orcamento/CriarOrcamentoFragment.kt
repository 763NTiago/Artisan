package com.sttalis.artisan.ui.orcamento

import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.viewpager2.widget.ViewPager2
import com.google.android.material.tabs.TabLayout
import com.google.android.material.tabs.TabLayoutMediator
import com.sttalis.artisan.R
import com.sttalis.artisan.model.Orcamento
import com.sttalis.artisan.utils.PdfGenerator
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class CriarOrcamentoFragment : Fragment(R.layout.fragment_criar_orcamento) {

    private val viewModel: OrcamentoViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val tabLayout = view.findViewById<TabLayout>(R.id.tabLayout)
        val viewPager = view.findViewById<ViewPager2>(R.id.viewPager)
        val btnPreview = view.findViewById<Button>(R.id.btnPreview)
        val btnSalvar = view.findViewById<Button>(R.id.btnSalvar)

        val adapter = OrcamentoPagerAdapter(this)
        viewPager.adapter = adapter
        viewPager.offscreenPageLimit = 5

        TabLayoutMediator(tabLayout, viewPager) { tab, position ->
            tab.text = when (position) {
                0 -> "Cliente"
                1 -> "Itens"
                2 -> "Termos"
                3 -> "Histórico"
                4 -> "Materiais"
                5 -> "Config"
                else -> ""
            }
        }.attach()

        viewModel.tabParaSelecionar.observe(viewLifecycleOwner) { index ->
            if (index != null) {
                viewPager.currentItem = index
                viewModel.limparComandoAba()
            }
        }

        btnPreview.setOnClickListener {
            gerarEVisualizarPdf()
        }

        btnSalvar.setOnClickListener {
            viewModel.salvarOrcamentoAtual()
        }

        viewModel.statusSalvamento.observe(viewLifecycleOwner) { status ->
            when (status) {
                is StatusSalvamento.Carregando -> {
                    btnSalvar.text = "Salvando..."
                    btnSalvar.isEnabled = false
                }
                is StatusSalvamento.Sucesso -> {
                    btnSalvar.text = "SALVAR E HISTÓRICO"
                    btnSalvar.isEnabled = true
                    Toast.makeText(context, "Salvo com Sucesso! Gerando PDF...", Toast.LENGTH_SHORT).show()
                    gerarEVisualizarPdf()
                }
                is StatusSalvamento.Erro -> {
                    btnSalvar.text = "SALVAR E HISTÓRICO"
                    btnSalvar.isEnabled = true
                    Toast.makeText(context, status.msg, Toast.LENGTH_LONG).show()
                }
                is StatusSalvamento.Ocioso -> {
                    btnSalvar.text = "SALVAR E HISTÓRICO"
                    btnSalvar.isEnabled = true
                }
            }
        }
    }

    private fun gerarEVisualizarPdf() {
        val cliente = viewModel.cliente.value
        if (cliente == null) {
            Toast.makeText(context, "Preencha os dados do cliente primeiro.", Toast.LENGTH_SHORT).show()
            return
        }

        val orcamentoTemp = Orcamento(
            id = viewModel.orcamentoEmEdicaoId.value ?: 0,
            dataCriacao = SimpleDateFormat("dd/MM/yyyy", Locale("pt", "BR")).format(Date()),
            clienteNome = cliente.nome,
            clienteEndereco = cliente.endereco,
            clienteCpf = cliente.cpfCnpj,
            clienteEmail = cliente.email,
            clienteTelefone = cliente.telefone,
            itensJson = com.google.gson.Gson().toJson(viewModel.itens.value),
            _valorTotalFinal = viewModel.getValorTotal(),
            observacoes = viewModel.observacoes.value,
            condicoesPagamentoAPI = viewModel.condicoesPagamento.value
        )

        try {
            PdfGenerator(requireContext()).gerarPdfOrcamento(orcamentoTemp)
        } catch (e: Exception) {
            Toast.makeText(context, "Erro ao gerar PDF: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }
}