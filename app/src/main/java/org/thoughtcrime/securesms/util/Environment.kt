package org.thoughtcrime.securesms.util

import com.google.android.gms.wallet.WalletConstants
import org.signal.donations.GooglePayApi
import org.signal.donations.StripeApi
import org.thoughtcrime.securesms.BuildConfig

@Suppress("KotlinConstantConditions")
object Environment {
  private const val GOOGLE_PLAY_BILLING_APPLICATION_ID = "org.thoughtcrime.securesms"

  const val IS_STAGING: Boolean = BuildConfig.FLAVOR_environment == "staging"
  const val IS_DEV: Boolean = BuildConfig.FLAVOR_environment == "dev" || BuildConfig.BUILD_TYPE == "instrumentation"

  object Backups {
    @JvmStatic
    fun supportsGooglePlayBilling(): Boolean {
      return BuildConfig.APPLICATION_ID == GOOGLE_PLAY_BILLING_APPLICATION_ID
    }
  }

  object Donations {
    @JvmStatic
    @get:JvmName("getGooglePayConfiguration")
    val GOOGLE_PAY_CONFIGURATION = GooglePayApi.Configuration(
      walletEnvironment = if (IS_STAGING) WalletConstants.ENVIRONMENT_TEST else WalletConstants.ENVIRONMENT_PRODUCTION
    )

    @JvmStatic
    @get:JvmName("getStripeConfiguration")
    val STRIPE_CONFIGURATION = StripeApi.Configuration(
      baseUrl = BuildConfig.STRIPE_BASE_URL,
      publishableKey = BuildConfig.STRIPE_PUBLISHABLE_KEY
    )
  }

  object Calling {
    @JvmStatic
    fun defaultSfuUrl(): String {
      return if (IS_STAGING) BuildConfig.SIGNAL_STAGING_SFU_URL else BuildConfig.SIGNAL_SFU_URL
    }
  }
}
