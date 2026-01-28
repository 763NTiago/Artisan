package com.sttalis.artisan.ui.recebimentos

import android.os.Bundle
import android.view.View
import androidx.fragment.app.Fragment
import androidx.viewpager2.widget.ViewPager2
import com.google.android.material.tabs.TabLayout
import com.google.android.material.tabs.TabLayoutMediator
import com.sttalis.artisan.R

class RecebimentosFragment : Fragment(R.layout.fragment_recebimentos) {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val tabLayout = view.findViewById<TabLayout>(R.id.tabRecebimentos)
        val viewPager = view.findViewById<ViewPager2>(R.id.pagerRecebimentos)

        viewPager.adapter = RecebimentosPagerAdapter(this)

        TabLayoutMediator(tabLayout, viewPager) { tab, position ->
            tab.text = when (position) {
                0 -> "🚀 Novo Lançamento"
                1 -> "💲 Baixa Parcelas"
                2 -> "📜 Histórico Geral"
                else -> ""
            }
        }.attach()
    }
}