package com.sttalis.artisan.ui.orcamento

import androidx.fragment.app.Fragment
import androidx.viewpager2.adapter.FragmentStateAdapter
import com.sttalis.artisan.ui.orcamento.tabs.TabClienteFragment
import com.sttalis.artisan.ui.orcamento.tabs.TabItensFragment
import com.sttalis.artisan.ui.orcamento.tabs.TabTermosFragment
import com.sttalis.artisan.ui.orcamento.tabs.TabHistoricoFragment
import com.sttalis.artisan.ui.orcamento.tabs.TabMateriaisFragment
import com.sttalis.artisan.ui.orcamento.tabs.TabConfigFragment

class OrcamentoPagerAdapter(fragment: Fragment) : FragmentStateAdapter(fragment) {

    override fun getItemCount(): Int = 6

    override fun createFragment(position: Int): Fragment {
        return when (position) {
            0 -> TabClienteFragment()
            1 -> TabItensFragment()
            2 -> TabTermosFragment()
            3 -> TabHistoricoFragment()
            4 -> TabMateriaisFragment()
            5 -> TabConfigFragment()
            else -> TabClienteFragment()
        }
    }
}