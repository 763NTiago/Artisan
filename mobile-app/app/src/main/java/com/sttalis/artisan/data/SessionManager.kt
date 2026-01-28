package com.sttalis.artisan.data

import android.content.Context
import android.content.SharedPreferences
import com.sttalis.artisan.model.LoginResponse

class SessionManager(context: Context) {
    private val prefs: SharedPreferences = context.getSharedPreferences("bellas_artes_session", Context.MODE_PRIVATE)

    fun saveAuthToken(user: LoginResponse) {
        val editor = prefs.edit()
        editor.putString("token", user.token)
        editor.putLong("user_id", user.id)
        editor.putString("user_name", user.first_name)
        editor.putString("user_email", user.email)
        editor.apply()
    }

    fun getToken(): String? {
        return prefs.getString("token", null)
    }

    fun getUserDetails(): Map<String, Any?> {
        return mapOf(
            "id" to prefs.getLong("user_id", -1),
            "name" to prefs.getString("user_name", ""),
            "email" to prefs.getString("user_email", "")
        )
    }

    fun logout() {
        val editor = prefs.edit()
        editor.clear()
        editor.apply()
    }
}