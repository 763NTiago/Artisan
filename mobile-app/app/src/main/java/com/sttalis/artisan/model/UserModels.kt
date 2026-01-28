package com.sttalis.artisan.model

data class LoginRequest(
    val username: String,
    val password: String
)

data class LoginResponse(
    val id: Long,
    val token: String,
    val first_name: String,
    val email: String,
    val username: String
)

data class UserUpdate(
    val first_name: String,
    val email: String,
    val password: String? = null
)