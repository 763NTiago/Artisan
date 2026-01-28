package com.sttalis.artisan.api

import com.sttalis.artisan.model.*
import retrofit2.Response
import retrofit2.http.*

interface ArtisanApi {

    @POST("login/") suspend fun login(@Body request: LoginRequest): Response<LoginResponse>
    @PUT("usuarios/{id}/") suspend fun atualizarUsuario(@Path("id") id: Long, @Body dados: UserUpdate): Response<UserUpdate>

    @GET("dashboard/financeiro/") suspend fun getResumoFinanceiro(): DashboardFinanceiro
    @GET("dashboard/eventos/") suspend fun getEventosDoDia(@Query("data") data: String?): List<EventoDia>

    @GET("agenda/") suspend fun getAgenda(): List<Agenda>
    @POST("agenda/") suspend fun criarAgenda(@Body dados: @JvmSuppressWildcards Map<String, Any>): Agenda
    @DELETE("agenda/{id}/") suspend fun deletarAgenda(@Path("id") id: Long): Response<Unit>
    @GET("agenda/datas_calendario/") suspend fun getDatasAgenda(): List<String>

    @GET("clientes/") suspend fun getClientes(): List<Cliente>
    @POST("clientes/get_or_create/") suspend fun criarCliente(@Body dados: @JvmSuppressWildcards Map<String, String>): Cliente
    @PUT("clientes/{id}/") suspend fun atualizarCliente(@Path("id") id: Long, @Body dados: Cliente): Response<Cliente>

    @GET("orcamentos/") suspend fun getOrcamentos(): List<Orcamento>
    @POST("orcamentos/") suspend fun criarOrcamento(@Body dados: @JvmSuppressWildcards Map<String, Any>): Orcamento
    @PUT("orcamentos/{id}/") suspend fun atualizarOrcamento(@Path("id") id: Long, @Body dados: @JvmSuppressWildcards Map<String, Any>): Orcamento
    @DELETE("orcamentos/{id}/") suspend fun deletarOrcamento(@Path("id") id: Long): Response<Unit>

    @GET("materiais/") suspend fun getMateriais(): List<Material>
    @POST("materiais/") suspend fun criarMaterial(@Body dados: @JvmSuppressWildcards Map<String, String>): Material
    @PUT("materiais/{id}/") suspend fun atualizarMaterial(@Path("id") id: Long, @Body dados: @JvmSuppressWildcards Map<String, String>): Material
    @DELETE("materiais/{id}/") suspend fun deletarMaterial(@Path("id") id: Long): Response<Unit>

    @GET("parcelas/") suspend fun getParcelas(): List<Parcela>
    @GET("recebimentos/") suspend fun getRecebimentos(): List<Recebimento>
    @POST("recebimentos/") suspend fun criarRecebimento(@Body dados: @JvmSuppressWildcards Map<String, Any>): Recebimento
    @POST("parcelas/") suspend fun criarParcela(@Body dados: @JvmSuppressWildcards Map<String, Any>): Parcela

    @PATCH("parcelas/{id}/") suspend fun atualizarParcela(@Path("id") id: Long, @Body dados: @JvmSuppressWildcards Map<String, Any>): Parcela

    @GET("arquitetos/") suspend fun getArquitetos(): List<Arquiteto>
    @POST("arquitetos/") suspend fun criarArquiteto(@Body dados: @JvmSuppressWildcards Map<String, Any>): Arquiteto
    @PUT("arquitetos/{id}/") suspend fun atualizarArquiteto(@Path("id") id: Long, @Body dados: @JvmSuppressWildcards Map<String, Any>): Response<Arquiteto>
    @DELETE("arquitetos/{id}/") suspend fun deletarArquiteto(@Path("id") id: Long): Response<Unit>

    @GET("comissoes/") suspend fun getComissoes(): List<Comissao>
    @POST("comissoes/") suspend fun criarComissao(@Body dados: @JvmSuppressWildcards Map<String, Any>): Comissao

    @PATCH("comissoes/{id}/") suspend fun atualizarComissao(@Path("id") id: Long, @Body dados: @JvmSuppressWildcards Map<String, Any>): Comissao

    @DELETE("comissoes/{id}/") suspend fun deletarComissao(@Path("id") id: Long): Response<Unit>

    @GET("relatorios/completo/") suspend fun getRelatorioCompleto(): List<RelatorioItem>
}