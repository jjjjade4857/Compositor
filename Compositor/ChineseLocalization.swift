import Foundation
import SwiftUI

/// Translates display strings only. Serialized enum raw values, shortcuts and layer content remain unchanged.
nonisolated enum ChineseLocalization {
    static let enabled = Bundle.main.preferredLocalizations.first?.hasPrefix("zh") == true

    static let bundle: Bundle = {
        guard enabled else { return .main }
        guard let path = Bundle.main.path(forResource: "zh-Hans", ofType: "lproj"), let bundle = Bundle(path: path) else { return .main }
        return bundle
    }()

    /// Some AppKit titles interpolate values before lookup. Match the same translated format keys there.
    static let templates: [(NSRegularExpression, String)] = {
        guard let url = Bundle.main.url(forResource: "ChineseTranslations", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let strings = try? JSONDecoder().decode([String: String].self, from: data),
              let token = try? NSRegularExpression(pattern: "%@|%lld|%ld|%d") else { return [] }
        return strings.keys.sorted().compactMap { key in
            let matches = token.matches(in: key, range: NSRange(key.startIndex..., in: key))
            guard !matches.isEmpty else { return nil }
            var pattern = "^", end = key.startIndex
            for match in matches {
                guard let range = Range(match.range, in: key) else { return nil }
                pattern += NSRegularExpression.escapedPattern(for: String(key[end..<range.lowerBound]))
                pattern += key[range] == "%@" ? "(.+?)" : "([0-9.,−–-]+)"
                end = range.upperBound
            }
            pattern += NSRegularExpression.escapedPattern(for: String(key[end...])) + "$"
            guard let regex = try? NSRegularExpression(pattern: pattern), let translation = strings[key] else { return nil }
            return (regex, translation)
        }
    }()

    /// Substitute original placeholder ranges from right to left, preserving captured user text verbatim.
    static func substitute(_ template: String, captures: [String]) -> String? {
        guard let token = try? NSRegularExpression(pattern: "%@|%lld|%ld|%d") else { return nil }
        let placeholders = token.matches(in: template, range: NSRange(template.startIndex..., in: template))
        guard placeholders.count == captures.count else { return nil }
        var result = template
        for index in placeholders.indices.reversed() {
            guard let target = Range(placeholders[index].range, in: result) else { return nil }
            result.replaceSubrange(target, with: captures[index])
        }
        return result
    }

    static func text(_ value: String) -> String {
        guard enabled, !value.isEmpty else { return value }
        let direct = bundle.localizedString(forKey: value, value: value, table: nil)
        if direct != value { return direct }
        for (regex, template) in templates {
            guard let match = regex.firstMatch(in: value, range: NSRange(value.startIndex..., in: value)) else { continue }
            let captures = (1..<match.numberOfRanges).compactMap { index in
                Range(match.range(at: index), in: value).map { String(value[$0]) }
            }
            if let result = substitute(template, captures: captures) { return result }
        }
        if value.hasSuffix("…") {
            let stem = String(value.dropLast()), translated = text(stem)
            if translated != stem { return translated + "…" }
        }
        if value.contains(" › ") { return value.components(separatedBy: " › ").map(text).joined(separator: " › ") }
        if value.contains(" · ") { return value.components(separatedBy: " · ").map(text).joined(separator: " · ") }
        for (prefix, translated) in [("Align ", "对齐 "), ("Distribute ", "分布 "), ("Cancel ", "取消 "), ("Copy ", "复制 "), ("Undo ", "撤销 "), ("Redo ", "重做 "), ("Last Filter: ", "上次使用的滤镜："), ("Delete ", "删除 "), ("Show ", "显示 "), ("Hide ", "隐藏 "), ("Edit ", "编辑 "), ("Export ", "导出 "), ("Reset ", "重置 "), ("Add ", "添加 "), ("Remove ", "移除 ")] {
            if value.hasPrefix(prefix) { return translated + text(String(value.dropFirst(prefix.count))) }
        }
        return value
    }
}

nonisolated func zh(_ value: String) -> String { ChineseLocalization.text(value) }
nonisolated func zh(_ value: LocalizedStringKey) -> LocalizedStringKey { value }
