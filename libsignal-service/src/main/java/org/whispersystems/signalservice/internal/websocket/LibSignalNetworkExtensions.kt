/*
 * Copyright 2024 Signal Messenger, LLC
 * SPDX-License-Identifier: AGPL-3.0-only
 */
@file:JvmName("LibSignalNetworkExtensions")

package org.whispersystems.signalservice.internal.websocket

import org.signal.core.util.logging.Log
import org.signal.core.util.orNull
import org.signal.libsignal.net.Network
import org.whispersystems.signalservice.internal.configuration.SignalServiceConfiguration
import java.io.IOException

private const val TAG = "LibSignalNetworkExtensions"

/**
 * Helper method to apply settings from the SignalServiceConfiguration.
 */
fun Network.applyConfiguration(config: SignalServiceConfiguration) {
  val proxy = null // MOLLY: TODO

  if (proxy == null) {
    this.clearProxy()
  } else {
    // try {
    //   this.setProxy(proxy.host, proxy.port)
    // } catch (e: IOException) {
    //   Log.e(TAG, "Invalid proxy configuration set! Failing connections until changed.")
    //   this.setInvalidProxy()
    // }
  }

  this.setCensorshipCircumventionEnabled(config.censored)
}
