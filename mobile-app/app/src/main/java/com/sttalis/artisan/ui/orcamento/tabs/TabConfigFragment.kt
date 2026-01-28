package com.sttalis.artisan.ui.orcamento.tabs

import android.content.Context
import android.content.Intent
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.fragment.app.Fragment
import com.sttalis.artisan.R
import java.io.InputStream

class TabConfigFragment : Fragment(R.layout.fragment_tab_config) {

    private lateinit var txtCaminho: TextView
    private lateinit var imgPreview: ImageView

    private val prefs by lazy {
        requireContext().getSharedPreferences("bellas_config", Context.MODE_PRIVATE)
    }

    private val pickImageLauncher = registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri: Uri? ->
        uri?.let {
            try {
                requireContext().contentResolver.takePersistableUriPermission(
                    it, Intent.FLAG_GRANT_READ_URI_PERMISSION
                )

                salvarNovaCapa(it.toString())
            } catch (e: Exception) {
                Toast.makeText(context, "Erro de permissão: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        txtCaminho = view.findViewById(R.id.txtCaminhoAtual)
        imgPreview = view.findViewById(R.id.imgPreviewCapa)
        val btnAlterar = view.findViewById<Button>(R.id.btnAlterarCapa)
        val btnRestaurar = view.findViewById<Button>(R.id.btnRestaurarCapa)

        atualizarInterface()

        btnAlterar.setOnClickListener {
            pickImageLauncher.launch(arrayOf("image/*"))
        }

        btnRestaurar.setOnClickListener {
            prefs.edit().remove("custom_cover_uri").apply()
            atualizarInterface()
            Toast.makeText(context, "Capa restaurada para o padrão!", Toast.LENGTH_SHORT).show()
        }
    }

    private fun salvarNovaCapa(uriString: String) {
        prefs.edit().putString("custom_cover_uri", uriString).apply()
        atualizarInterface()
        Toast.makeText(context, "Nova capa definida!", Toast.LENGTH_SHORT).show()
    }

    private fun atualizarInterface() {
        val uriString = prefs.getString("custom_cover_uri", null)

        if (uriString != null) {
            try {
                val uri = Uri.parse(uriString)

                val inputStream: InputStream? = requireContext().contentResolver.openInputStream(uri)
                inputStream?.close() 
                imgPreview.setImageURI(uri)
                txtCaminho.text = "Personalizada"

            } catch (e: Exception) {
                Toast.makeText(context, "Imagem personalizada não encontrada. Restaurando padrão.", Toast.LENGTH_LONG).show()
                prefs.edit().remove("custom_cover_uri").apply()
                carregarImagemPadrao()
            }
        } else {
            carregarImagemPadrao()
        }
    }

    private fun carregarImagemPadrao() {
        try {
            val inputStream = requireContext().assets.open("images/fundo_padrao.png")
            val bitmap = BitmapFactory.decodeStream(inputStream)
            imgPreview.setImageBitmap(bitmap)
            txtCaminho.text = "Padrão do Sistema (Assets)"
        } catch (e: Exception) {
            txtCaminho.text = "Erro ao carregar padrão: ${e.message}"
        }
    }
}