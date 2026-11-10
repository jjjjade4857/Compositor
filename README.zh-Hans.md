# Compositor 中文支持维护分支

上游：<https://github.com/robbietilton/Compositor>。本仓库是社区 fork，保留 MIT 许可。

`main` 保留上游基线；`zh-Hans` 是中文支持分支，初始基于上游 v1.6.6（2f507800bc4b32db6b31d34a822cbfc577bf46cf）。源码保留英文回退；仓库打包的中文发行版使用统一简体中文元数据，固定应用名称和标识。

固定 SwiftUI 文本通过原生 Localizable.strings 本地化，动态字符串及 AppKit 菜单通过 ChineseLocalization 翻译显示名称。混合模式保留独立的原始标识，不改变工程格式或用户内容。翻译源为 localization/zh-Hans.txt；Compositor/Resources 中的文件由脚本生成，可被 Xcode 原生构建直接打包。

```sh
python3 scripts/generate-localization.py
python3 scripts/audit-localization.py
python3 scripts/review-localization.py
xcodebuild build -project Compositor.xcodeproj -scheme Compositor -configuration Release -destination 'platform=macOS,arch=arm64' CODE_SIGNING_ALLOWED=NO
```

GitHub Actions 的 Chinese build 会检查缺译、生成资源、构建并上传临时签名安装包。该包尚未 Apple 公证，也未接入独立自动升级 feed。原版 Sparkle 更新在此分支中停用，避免覆盖中文支持。现有本机手工构建应用仍可独立使用。

Review upstream release 每天检查官方最新正式 release；已有版本则跳过，新版本尝试合并到 sync 分支并生成草稿 PR、触发中文构建。出现冲突或缺译则失败并保留维护分支现状。需在 Actions 中查看失败记录并人工修复。合并前应确认该分支的 Chinese build 结果，并检查菜单、动态提示及工程打开保存；不自动合并、不自动发布安装更新。PR 自动创建还需要仓库允许 GitHub Actions 创建 PR。

当前检查包含全源码候选字符串、编译器提取键和已识别显示入口；零缺失仍须结合真实界面复核。后续应逐步补齐复杂格式字符串并迁移到 String Catalog；可在此基础上整理面向上游的本地化 PR。尚未向上游作者提交 PR 或联系作者。

审查修订：图层缩略图、蒙版、字体及快捷键录制等 AppKit 提示已接入翻译；动态翻译不会再次替换文件名中的百分号占位符。上游同步会恢复已有审查分支，补跑 Chinese build 和 Verify，并避免重复创建 PR。维护脚本回归检查可运行 `python3 scripts/test-maintenance.py`。

当前中文修订 6（2026-11-10）将源码词条清单、编译器提取键和显示入口分别检查。`localization/reviewed-exceptions.json` 对保留的协议字段、品牌和单位逐条记录理由。新版本构建若出现未审查文字或直接插值原始枚举值的已识别显示入口，会停止。`localization/release.json` 与 `scripts/configure-chinese-bundle.py` 统一本地和 CI 的应用名称、标识与修订信息。

本地构建和打包：
```sh
python3 scripts/build-chinese.py
python3 scripts/review-localization.py --require-compiler-data
python3 scripts/package-chinese.py
```

唯一安装名称为 `Compositor 中文版.app`；后续应替换同一入口，避免按版本号生成多个可启动副本。完整的人工界面遍历与第三方系统错误仍须按实际场景验证，不能将静态扫描零缺失等同于无条件的全部状态证明。
