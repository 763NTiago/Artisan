package com.sttalis.artisan.ui.comissao

import android.os.Bundle
import android.view.View
import androidx.fragment.app.Fragment
import androidx.viewpager2.widget.ViewPager2
import com.google.android.material.tabs.TabLayout
import com.google.android.material.tabs.TabLayoutMediator
import com.sttalis.artisan.R

class ComissoesFragment : Fragment(R.layout.fragment_comissoes) {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val tabLayout = view.findViewById<TabLayout>(R.id.tabComissoes)
        val viewPager = view.findViewById<ViewPager2>(R.id.pagerComissoes)

        viewPager.adapter = ComissoesPagerAdapter(this)

        TabLayoutMediator(tabLayout, viewPager) { tab, position ->
            tab.text = when (position) {
                0 -> "🚀 A Pagar (Pendentes)"
                1 -> "👤 Gerenciar Arquitetos"
                2 -> "📜 Histórico Pagos"
                else -> ""
            }
        }.attach()
    }
}