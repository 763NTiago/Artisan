package com.sttalis.artisan.ui

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.fragment.app.Fragment
import com.sttalis.artisan.R
import com.sttalis.artisan.data.ArtisanRepository
import com.sttalis.artisan.data.SessionManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class PerfilFragment : Fragment(R.layout.fragment_perfil) {
    private lateinit var session: SessionManager
    private val repository = ArtisanRepository()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        session = SessionManager(requireContext())

        val etNome = view.findViewById<EditText>(R.id.etNomePerfil)
        val etEmail = view.findViewById<EditText>(R.id.etEmailPerfil)
        val etSenha = view.findViewById<EditText>(R.id.etSenhaPerfil)
        val btnSalvar = view.findViewById<Button>(R.id.btnSalvarPerfil)
        val btnLogout = view.findViewById<Button>(R.id.btnLogout)

        val user = session.getUserDetails()
        etNome.setText(user["name"] as String)
        etEmail.setText(user["email"] as String)

        btnSalvar.setOnClickListener {
            val id = user["id"] as Long
            val pass = if(etSenha.text.isNotEmpty()) etSenha.text.toString() else null

            CoroutineScope(Dispatchers.IO).launch {
                val sucesso = repository.atualizarUsuario(id, etNome.text.toString(), etEmail.text.toString(), pass)
                withContext(Dispatchers.Main) {
                    if(sucesso) {
                        Toast.makeText(context, "Perfil atualizado!", Toast.LENGTH_SHORT).show()
                        etSenha.text.clear()
                    } else {
                        Toast.makeText(context, "Erro ao atualizar.", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        }

        btnLogout.setOnClickListener {
            session.logout()
            val intent = Intent(requireContext(), LoginActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            startActivity(intent)
        }
    }
}