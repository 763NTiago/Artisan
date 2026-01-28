package com.sttalis.artisan.ui.recebimentos

import androidx.fragment.app.Fragment
import androidx.viewpager2.adapter.FragmentStateAdapter
import com.sttalis.artisan.ui.recebimentos.tabs.TabNovoLancamentoFragment
import com.sttalis.artisan.ui.recebimentos.tabs.TabBaixaFragment
import com.sttalis.artisan.ui.recebimentos.tabs.TabHistoricoFragment

class RecebimentosPagerAdapter(fragment: Fragment) : FragmentStateAdapter(fragment) {
    override fun getItemCount(): Int = 3

    override fun createFragment(position: Int): Fragment {
        return when (position) {
            0 -> TabNovoLancamentoFragment()
            1 -> TabBaixaFragment()
            2 -> TabHistoricoFragment()
            else -> TabNovoLancamentoFragment()
        }
    }
}