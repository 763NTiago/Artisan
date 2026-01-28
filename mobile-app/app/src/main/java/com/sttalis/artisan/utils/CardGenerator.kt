package com.sttalis.artisan.utils

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.util.Base64
import java.io.ByteArrayOutputStream

object CardGenerator {

    fun gerarHtmlCartao(
        context: Context,
        nomeCliente: String,
        porcentagem: String,
        validade: String
    ): String {
        var htmlTemplate = try {
            context.assets.open("templates/cartao.html")
                .bufferedReader()
                .use { it.readText() }
        } catch (e: Exception) {
            return "<h1>Erro ao carregar template do cartão</h1>"
        }

        val cssContent = try {
            context.assets.open("css/cartao.css")
                .bufferedReader()
                .use { it.readText() }
        } catch (e: Exception) { "" }

        val fundoBase64 = getFundoImagemBase64(context)
        val whatsappBase64 = getAssetImageAsBase64(context, "images/whatsapp_icon.png")
        val instaBase64 = getAssetImageAsBase64(context, "images/Instagram.png")

        htmlTemplate = htmlTemplate
            .replace("{{ css_style }}", cssContent)
            .replace("{{ fundo_cartao_base64 }}", fundoBase64)
            .replace("{{ whatsapp_icon_base64 }}", whatsappBase64)
            .replace("{{ qrcode_insta_base64 }}", instaBase64)
            .replace("{{ nome_cliente }}", nomeCliente)
            .replace("{{ porcentagem }}", porcentagem)
            .replace("{{ data_validade }}", validade)

            .replace("{% if fundo_cartao_base64 %}", "")
            .replace("{% endif %}", "")
            .replace("{% if qrcode_insta_base64 %}", "")
            .replace("{% if whatsapp_icon_base64 %}", "")

        return htmlTemplate
    }

    private fun getFundoImagemBase64(context: Context): String {
        val prefs = context.getSharedPreferences("bellas_config", Context.MODE_PRIVATE)
        val customUriString = prefs.getString("custom_card_bg_uri", null)

        return if (customUriString != null) {
            try {
                val uri = Uri.parse(customUriString)
                val inputStream = context.contentResolver.openInputStream(uri)
                val bitmap = BitmapFactory.decodeStream(inputStream)
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
            val bitmap = BitmapFactory.decodeStream(inputStream)
            bitmapToBase64(bitmap)
        } catch (e: Exception) { "" }
    }

    private fun bitmapToBase64(bitmap: Bitmap): String {
        val outputStream = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.PNG, 100, outputStream)
        return Base64.encodeToString(outputStream.toByteArray(), Base64.NO_WRAP)
    }
}