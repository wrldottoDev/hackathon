import UIKit

final class KeyboardViewController: UIInputViewController {
    private let coordinator = CaptureCoordinator()
    private var symbolsMode = false
    private var uppercaseMode = false
    private var draftBuffer = ""

    override func viewDidLoad() {
        super.viewDidLoad()
        renderKeyboard()
    }

    private func renderKeyboard() {
        view.subviews.forEach { $0.removeFromSuperview() }

        let stack = UIStackView()
        stack.axis = .vertical
        stack.spacing = 8
        stack.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(stack)

        NSLayoutConstraint.activate([
            stack.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 8),
            stack.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -8),
            stack.topAnchor.constraint(equalTo: view.topAnchor, constant: 8),
            stack.bottomAnchor.constraint(equalTo: view.bottomAnchor, constant: -8),
        ])

        let rows = symbolsMode
            ? ["1234567890", "-/:;()$&@", ".,?!'\""]
            : ["qwertyuiop", "asdfghjkl", "zxcvbnm"]

        rows.forEach { row in
            stack.addArrangedSubview(makeRow(row.map(String.init)))
        }

        stack.addArrangedSubview(makeRow([
            symbolsMode ? "ABC" : "123",
            "⇧",
            "space",
            "⌫",
            "⏎",
        ]))
    }

    private func makeRow(_ labels: [String]) -> UIStackView {
        let row = UIStackView()
        row.axis = .horizontal
        row.spacing = 6
        row.distribution = .fillEqually

        labels.forEach { label in
            let button = UIButton(type: .system)
            button.setTitle(title(for: label), for: .normal)
            button.backgroundColor = UIColor(white: 0.96, alpha: 1)
            button.layer.cornerRadius = 10
            button.titleLabel?.font = UIFont.systemFont(ofSize: 18, weight: .semibold)
            button.heightAnchor.constraint(equalToConstant: 44).isActive = true
            button.addAction(UIAction { [weak self] _ in
                self?.handleKey(label)
            }, for: .touchUpInside)
            row.addArrangedSubview(button)
        }

        return row
    }

    private func title(for key: String) -> String {
        guard key != "space" else {
            return "Space"
        }
        if !symbolsMode && uppercaseMode && key.count == 1 {
            return key.uppercased()
        }
        return key
    }

    private func handleKey(_ key: String) {
        switch key {
        case "123", "ABC":
            symbolsMode.toggle()
            renderKeyboard()

        case "⇧":
            uppercaseMode.toggle()
            renderKeyboard()

        case "space":
            textDocumentProxy.insertText(" ")
            draftBuffer.append(" ")

        case "⌫":
            textDocumentProxy.deleteBackward()
            if !draftBuffer.isEmpty {
                draftBuffer.removeLast()
            }

        case "⏎":
            flushDraft()
            textDocumentProxy.insertText("\n")

        default:
            let output = (!symbolsMode && uppercaseMode) ? key.uppercased() : key
            textDocumentProxy.insertText(output)
            draftBuffer.append(output)
        }
    }

    private func flushDraft() {
        coordinator.acceptKeyboardDraft(content: draftBuffer)
        draftBuffer.removeAll()
    }
}
