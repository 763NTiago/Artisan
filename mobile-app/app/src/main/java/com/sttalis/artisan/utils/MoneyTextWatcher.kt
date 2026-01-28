package com.sttalis.artisan.utils

import android.text.Editable
import android.text.TextWatcher
import android.widget.EditText
import java.lang.ref.WeakReference
import java.math.BigDecimal
import java.text.NumberFormat
import java.util.Locale

class MoneyTextWatcher(editText: EditText, locale: Locale = Locale("pt", "BR")) : TextWatcher {
    private val editTextWeakReference = WeakReference(editText)
    private val numberFormat = NumberFormat.getCurrencyInstance(locale)

    override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}

    override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}

    override fun afterTextChanged(editable: Editable?) {
        val editText = editTextWeakReference.get() ?: return
        val s = editable.toString()
        if (s.isEmpty()) return

        editText.removeTextChangedListener(this)

        val cleanString = s.replace("[^0-9]".toRegex(), "")

        val parsed = try {
            BigDecimal(cleanString).setScale(2, BigDecimal.ROUND_FLOOR)
                .divide(BigDecimal(100), BigDecimal.ROUND_FLOOR)
        } catch (e: NumberFormatException) {
            BigDecimal("0.00")
        }

        val formatted = numberFormat.format(parsed)

        editText.setText(formatted)
        editText.setSelection(formatted.length)

        editText.addTextChangedListener(this)
    }

    companion object {
        fun parseCurrency(valorString: String): Double {
            return try {
                val cleanString = valorString.replace("[^0-9]".toRegex(), "")
                cleanString.toDouble() / 100.0
            } catch (e: Exception) {
                0.0
            }
        }
    }
}