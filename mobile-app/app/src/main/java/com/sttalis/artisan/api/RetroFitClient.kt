package com.sttalis.artisan.api

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import com.sttalis.artisan.BuildConfig

object RetrofitClient {
    private const val BASE_URL = BuildConfig.API_URL

    val api: ArtisanApi by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ArtisanApi::class.java)
    }
}