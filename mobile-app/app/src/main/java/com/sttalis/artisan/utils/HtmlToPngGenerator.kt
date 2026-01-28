package com.sttalis.artisan.utils

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.net.Uri
import android.os.Handler
import android.os.Looper
import android.util.Base64
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.core.content.FileProvider
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileOutputStream

object HtmlToPngGenerator {

    fun gerarPngDoHtml(
        context: Context,
        htmlContent: String,
        nomeArquivo: String,
        onResult: (Uri?) -> Unit
    ) {
        Handler(Looper.getMainLooper()).post {
            val webView = WebView(context)

            webView.settings.apply {
                javaScriptEnabled = true
                allowFileAccess = true
                loadsImagesAutomatically = true
                useWideViewPort = true
                loadWithOverviewMode = true
                textZoom = 100
            }

            val largura = 1080
            val altura = 1080

            webView.layout(0, 0, largura, altura)

            webView.setInitialScale(100)

            webView.webViewClient = object : WebViewClient() {
                override fun onPageFinished(view: WebView, url: String) {
                    view.layout(0, 0, largura, altura)

                    val bitmap = Bitmap.createBitmap(largura, altura, Bitmap.Config.ARGB_8888)
                    val canvas = Canvas(bitmap)

                    view.draw(canvas)

                    try {
                        val cachePath = File(context.cacheDir, "cartoes")
                        cachePath.mkdirs()

                        val nomeFinal = if (nomeArquivo.endsWith(".png")) nomeArquivo else "$nomeArquivo.png"
                        val file = File(cachePath, nomeFinal)

                        val stream = FileOutputStream(file)
                        bitmap.compress(Bitmap.CompressFormat.PNG, 100, stream)
                        stream.close()

                        val contentUri = FileProvider.getUriForFile(
                            context,
                            "${context.packageName}.provider",
                            file
                        )
                        onResult(contentUri)

                    } catch (e: Exception) {
                        e.printStackTrace()
                        onResult(null)
                    }

                    view.destroy()
                }
            }

            webView.loadDataWithBaseURL("file:///android_asset/", htmlContent, "text/html", "UTF-8", null)
        }
    }

    fun montarHtmlCartaoSimples(
        context: Context,
        nomeCliente: String,
        porcentagem: String,
        validade: String,
        codigo: String
    ): String {
        var html = lerArquivoAsset(context, "templates/cartao.html")
        val css = lerArquivoAsset(context, "css/cartao.css")

        html = html.replace("{{ css_style }}", css)

        val fundoBase64 = getFundoImagemBase64(context)
        val instaBase64 = getAssetImageAsBase64(context, "images/Instagram.png")
        val whatsBase64 = getAssetImageAsBase64(context, "images/whatsapp_icon.png")

        html = html
            .replace("{{ fundo_cartao_base64 }}", fundoBase64)
            .replace("{{ nome_cliente }}", nomeCliente)
            .replace("{{ porcentagem }}", porcentagem)
            .replace("{{ data_validade }}", validade)
            .replace("{{ codigo_promocional }}", codigo)

            .replace("{{ qrcode_insta_base64 }}", instaBase64)
            .replace("{{ whatsapp_icon_base64 }}", whatsBase64)

        html = html
            .replace("{% if fundo_cartao_base64 %}", "")
            .replace("{% endif %}", "")
            .replace("{% if qrcode_insta_base64 %}", if (instaBase64.isNotEmpty()) "" else "<div style='display:none'>")
            .replace("{% if whatsapp_icon_base64 %}", if (whatsBase64.isNotEmpty()) "" else "<div style='display:none'>")

        return html
    }


    private fun lerArquivoAsset(context: Context, caminho: String): String {
        return try {
            context.assets.open(caminho).bufferedReader().use { it.readText() }
        } catch (e: Exception) {
            ""
        }
    }

    private fun getFundoImagemBase64(context: Context): String {
        val prefs = context.getSharedPreferences("bellas_config", Context.MODE_PRIVATE)
        val customUriString = prefs.getString("custom_card_bg_uri", null)

        return if (customUriString != null) {
            try {
                val uri = Uri.parse(customUriString)
                val inputStream = context.contentResolver.openInputStream(uri)
                val bitmap = android.graphics.BitmapFactory.decodeStream(inputStream)
                bitmapToBase64(bitmap)
            } catch (e: Exception) {
                getAssetImageAsBase64(context, "images/fundo_cartao.png")
            }
        } else {
            getAssetImageAsBase64(context, "images/fundo_cartao.png")
        }
    }

    private fun getAssetImageAsBase64(context: Context, path: String): String {
        return try {
            val inputStream = context.assets.open(path)
            val bitmap = android.graphics.BitmapFactory.decodeStream(inputStream)
            bitmapToBase64(bitmap)
        } catch (e: Exception) { "" }
    }

    private fun bitmapToBase64(bitmap: Bitmap?): String {
        if (bitmap == null) return ""
        val outputStream = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.PNG, 90, outputStream)
        return Base64.encodeToString(outputStream.toByteArray(), Base64.NO_WRAP)
    }
}