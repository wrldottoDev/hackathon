package com.tensorflowkeyboard.app.ime

import android.content.Context
import io.flutter.FlutterInjector
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.embedding.engine.dart.DartExecutor

object KeyboardFlutterEngineStore {
    @Volatile
    private var engine: FlutterEngine? = null

    fun getOrCreate(context: Context): FlutterEngine {
        return engine ?: synchronized(this) {
            engine ?: buildEngine(context.applicationContext).also { engine = it }
        }
    }

    private fun buildEngine(context: Context): FlutterEngine {
        val loader = FlutterInjector.instance().flutterLoader()
        if (!loader.initialized()) {
            loader.startInitialization(context)
            loader.ensureInitializationComplete(context, null)
        }

        return FlutterEngine(context).apply {
            dartExecutor.executeDartEntrypoint(
                DartExecutor.DartEntrypoint(
                    loader.findAppBundlePath(),
                    "keyboardEntrypoint",
                ),
            )
        }
    }
}
