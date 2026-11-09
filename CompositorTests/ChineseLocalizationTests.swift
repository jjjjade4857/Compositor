import Testing
@testable import Compositor

struct ChineseLocalizationTests {
    @Test func capturedFileNamesKeepPercentTokens() {
        #expect(ChineseLocalization.substitute("文件 %@ 有 %d 层", captures: ["海报%d%@.comp", "3"])
                == "文件 海报%d%@.comp 有 3 层")
    }

    @Test func unicodeCapturesKeepTemplateOffsets() {
        #expect(ChineseLocalization.substitute("%@：%@，%lld", captures: ["🎨设计", "长文件名", "12"])
                == "🎨设计：长文件名，12")
    }

    @Test func mismatchedPlaceholdersAreRejected() {
        #expect(ChineseLocalization.substitute("%@ %d", captures: ["only one"]) == nil)
    }
}
