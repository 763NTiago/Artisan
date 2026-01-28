package com.sttalis.artisan.ui.comissao

import androidx.fragment.app.Fragment
import androidx.viewpager2.adapter.FragmentStateAdapter
import com.sttalis.artisan.ui.comissao.tabs.TabArquitetosFragment
import com.sttalis.artisan.ui.comissao.tabs.TabHistoricoComissoesFragment
import com.sttalis.artisan.ui.comissao.tabs.TabPagarFragment

class ComissoesPagerAdapter(fragment: Fragment) : FragmentStateAdapter(fragment) {

    override fun getItemCount(): Int = 3

    override fun createFragment(position: Int): Fragment {
        return when (position) {
            0 -> TabPagarFragment()                
            1 -> TabArquitetosFragment()          
            2 -> TabHistoricoComissoesFragment()   
            else -> TabPagarFragment()
        }
    }
}