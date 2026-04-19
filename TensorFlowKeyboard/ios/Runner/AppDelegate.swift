import Flutter
import UIKit
import UserNotifications

@main
@objc final class AppDelegate: FlutterAppDelegate {
    private let methodsChannelName = "tensorflow_keyboard/methods"
    private let eventsChannelName = "tensorflow_keyboard/events"

    override func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        let controller = window?.rootViewController as? FlutterViewController

        if let controller {
            let methodsChannel = FlutterMethodChannel(
                name: methodsChannelName,
                binaryMessenger: controller.binaryMessenger
            )
            let eventsChannel = FlutterEventChannel(
                name: eventsChannelName,
                binaryMessenger: controller.binaryMessenger
            )

            eventsChannel.setStreamHandler(IOSNativeStreamHandler.shared)
            methodsChannel.setMethodCallHandler(handleMethodCall)
        }

        GeneratedPluginRegistrant.register(with: self)
        UNUserNotificationCenter.current().delegate = self
        return super.application(application, didFinishLaunchingWithOptions: launchOptions)
    }

    private func handleMethodCall(_ call: FlutterMethodCall, result: @escaping FlutterResult) {
        switch call.method {
        case "setTrustedContacts":
            let args = call.arguments as? [String: Any]
            let contacts = args?["contacts"] as? [String] ?? []
            UserDefaults.standard.set(contacts, forKey: "trusted_contacts")
            result(nil)

        case "getPlatformSummary":
            result([
                "imeEnabled": false,
                "accessibilityEnabled": false,
                "notificationEnabled": false,
                "bufferSize": 0,
                "trustedContactsCount": (UserDefaults.standard.array(forKey: "trusted_contacts") as? [String] ?? []).count,
                "platformNote": "The keyboard extension must be configured in Xcode. iOS does not support cross-app text capture."
            ])

        case "seedSimulationEvent":
            let args = call.arguments as? [String: Any]
            IOSNativeStreamHandler.shared.emit([
                "id": UUID().uuidString,
                "source": "simulation",
                "senderName": args?["senderName"] as? String,
                "content": args?["content"] as? String ?? "",
                "timestamp": Int(Date().timeIntervalSince1970 * 1000),
                "blockedByWhitelist": false,
                "metadata": ["origin": "ios_debug"]
            ])
            result(nil)

        case "openInputMethodSettings", "openAccessibilitySettings", "openNotificationSettings":
            if let url = URL(string: UIApplication.openSettingsURLString) {
                UIApplication.shared.open(url)
            }
            result(nil)

        default:
            result(FlutterMethodNotImplemented)
        }
    }
}

final class IOSNativeStreamHandler: NSObject, FlutterStreamHandler {
    static let shared = IOSNativeStreamHandler()

    private var eventSink: FlutterEventSink?

    func onListen(withArguments arguments: Any?, eventSink events: @escaping FlutterEventSink) -> FlutterError? {
        eventSink = events
        return nil
    }

    func onCancel(withArguments arguments: Any?) -> FlutterError? {
        eventSink = nil
        return nil
    }

    func emit(_ payload: [String: Any]) {
        eventSink?(payload)
    }
}
