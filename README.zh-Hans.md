# Compositor 中文支持维护分支

上游：<https://github.com/robbietilton/Compositor>。本仓库是社区 fork，保留 MIT 许可。

`main` 保留上游基线；`zh-Hans` 是中文支持分支，初始基于上游 v1.6.6（2f507800bc4b32db6b31d34a822cbfc577bf46cf）。中文支持使用 macOS 的语言选择，英文作为回退；可在系统设置的应用语言中选择简体中文。

固定 SwiftUI 文本通过原生 Localizable.strings 本地化，动态字符串及 AppKit 菜单通过 ChineseLocalization 翻译显示名称。混合模式保留独立的原始标识，不改变工程格式或用户内容。翻译源为 localization/zh-Hans.txt；Compositor/Resources 中的文件由脚本生成，可被 Xcode 原生构建直接打包。

```sh
python3 scripts/generate-localization.py
python3 scripts/audit-localization.py
xcodebuild build -project Compositor.xcodeproj -scheme Compositor -configuration Release -destination 'platform=macOS,arch=arm64' CODE_SIGNING_ALLOWED=NO
```

GitHub Actions 的 Chinese build 会检查缺译、生成资源、构建并上传临时签名安装包。该包尚未 Apple 公证，也未接入独立自动升级 feed。原版 Sparkle 更新在此分支中停用，避免覆盖中文支持。现有本机手工构建应用仍可独立使用。

Review upstream release 每天检查官方最新正式 release；已有版本则跳过，新版本尝试合并到 sync 分支并生成草稿 PR、触发中文构建。出现冲突或缺译则失败并保留维护分支现状。需在 Actions 中查看失败记录并人工修复。合并前应确认该分支的 Chinese build 结果，并检查菜单、动态提示及工程打开保存；不自动合并、不自动发布安装更新。PR 自动创建还需要仓库允许 GitHub Actions 创建 PR。

当前静态扫描只覆盖常见固定文字入口，零缺失不等于所有动态界面均完成翻译。后续应逐步补齐复杂格式字符串并迁移到 String Catalog；可在此基础上整理面向上游的本地化 PR。尚未向上游作者提交 PR 或联系作者。
