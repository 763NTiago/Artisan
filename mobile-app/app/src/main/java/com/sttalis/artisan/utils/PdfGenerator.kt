package com.sttalis.artisan.utils

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.print.PrintAttributes
import android.print.PrintManager
import android.util.Base64
import android.webkit.WebView
import android.webkit.WebViewClient
import com.sttalis.artisan.model.Orcamento
import java.io.ByteArrayOutputStream
import java.text.NumberFormat
import java.util.Locale

class PdfGenerator(private val context: Context) {

    fun gerarPdfOrcamento(orcamento: Orcamento) {
        var htmlFinal = loadAsset("templates/template.html")

        htmlFinal = processarIncludes(htmlFinal)

        val cssBase = loadAsset("css/base.css")
        val cssCapa = loadAsset("css/capa.css")
        val cssConteudo = loadAsset("css/conteudo.css")
        val cssCompleto = "$cssBase\n$cssCapa\n$cssConteudo"

        htmlFinal = htmlFinal.replace("{{ css_style }}", cssCompleto)

        val logoB64 = getAssetImageAsBase64("images/logo.png")
        val fundoB64 = getFundoImagemBase64()

        val format = NumberFormat.getCurrencyInstance(Locale("pt", "BR"))

        htmlFinal = htmlFinal
            .replace("{{ logo_base64 }}", logoB64)
            .replace("{{ fundo_base64 }}", fundoB64)
            .replace("{{ empresa_nome }}", "Artisan")
            .replace("{{ cliente_nome }}", orcamento.clienteNome ?: "")
            .replace("{{ cliente_endereco }}", orcamento.clienteEndereco ?: "-")
            .replace("{{ cliente_endereco if cliente_endereco else '-' }}", orcamento.clienteEndereco ?: "-")
            .replace("{{ data_hoje }}", orcamento.dataCriacao ?: "")
            .replace("{{ valor_total_final }}", format.format(orcamento.valorTotalFinal))

        val linhasItens = StringBuilder()
        for (item in orcamento.itens) {
            val qtdDisplay = if (item.quantidade % 1.0 == 0.0) item.quantidade.toInt().toString() else String.format("%.1f", item.quantidade)

            linhasItens.append("""
                <tr>
                    <td><span class="item-amb">${item.ambiente}</span></td>
                    <td><span class="item-desc" style="white-space: pre-wrap;">${item.descricao}</span></td>
                    <td class="text-center">$qtdDisplay</td>
                    <td class="text-right">${format.format(item.valorUnitario)}</td>
                    <td class="text-right">${format.format(item.valorTotal)}</td>
                </tr>
            """.trimIndent())
        }

        val regexLoop = Regex("\\{% for item in itens %\\}(.*?)\\{% endfor %\\}", setOf(RegexOption.DOT_MATCHES_ALL))

        if (regexLoop.containsMatchIn(htmlFinal)) {
            htmlFinal = htmlFinal.replace(regexLoop) { linhasItens.toString() }
        } else {
            htmlFinal = htmlFinal.replace("{{ itens_tabela }}", linhasItens.toString())
        }

        val obs = orcamento.observacoes ?: ""
        val pag = orcamento.condicoesPagamento

        htmlFinal = htmlFinal
            .replace("{% if observacoes %}", if (obs.isNotEmpty()) "" else "<div style='display:none'>")
            .replace("{% endif %}", "</div>")
            .replace("{% if condicoes_pagamento %}", if (pag.isNotEmpty()) "" else "<div style='display:none'>")
            .replace("{{ observacoes | safe }}", obs)
            .replace("{{ condicoes_pagamento | safe }}", pag)
            .replace("{% endif %}", "")

        criarWebViewParaImpressao(htmlFinal)
    }

    private fun loadAsset(path: String): String {
        return try {
            context.assets.open(path).bufferedReader().use { it.readText() }
        } catch (e: Exception) { "" }
    }

    private fun processarIncludes(html: String): String {
        var processado = html
        val regex = Regex("\\{% include '(.*?)' %\\}")
        var match = regex.find(processado)
        while (match != null) {
            val arquivo = match.groupValues[1]
            val conteudo = loadAsset("templates/$arquivo")
            processado = processado.replace(match.value, conteudo)
            match = regex.find(processado)
        }
        return processado
    }

    private fun getAssetImageAsBase64(path: String): String {
        return try {
            val inputStream = context.assets.open(path)
            val bitmap = BitmapFactory.decodeStream(inputStream)
            bitmapToBase64(bitmap)
        } catch (e: Exception) { "" }
    }

    private fun getFundoImagemBase64(): String {
        val prefs = context.getSharedPreferences("bellas_config", Context.MODE_PRIVATE)
        val customUriString = prefs.getString("custom_cover_uri", null)
        if (customUriString != null) {
            try {
                val uri = android.net.Uri.parse(customUriString)
                val inputStream = context.contentResolver.openInputStream(uri)
                val bitmap = BitmapFactory.decodeStream(inputStream)
                return bitmapToBase64(bitmap)
            } catch (e: Exception) { }
        }
        return getAssetImageAsBase64("images/fundo_padrao.png")
    }

    private fun bitmapToBase64(bitmap: Bitmap?): String {
        if (bitmap == null) return ""
        val outputStream = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.PNG, 80, outputStream)
        return Base64.encodeToString(outputStream.toByteArray(), Base64.NO_WRAP)
    }

    private fun criarWebViewParaImpressao(htmlContent: String) {
        val webView = WebView(context)
        webView.settings.apply {
            javaScriptEnabled = true
            allowFileAccess = true
            loadsImagesAutomatically = true
            useWideViewPort = true
            loadWithOverviewMode = true
            textZoom = 100
        }
        webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                val printManager = context.getSystemService(Context.PRINT_SERVICE) as? PrintManager
                val printAdapter = webView.createPrintDocumentAdapter("Orcamento_Artisan")
                printManager?.print("Orcamento", printAdapter, PrintAttributes.Builder().build())
            }
        }
        webView.loadDataWithBaseURL("file:///android_asset/", htmlContent, "text/html", "UTF-8", null)
    }
}