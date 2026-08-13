# Frontend デザイン規約

AI と人間が Svelte の見た目を、同じ構図・同じ寸法の決め方で再現するための規約。

この文書は視覚上の自由度より再現性を優先する。一般的なレスポンシブ手法を列挙する文書ではない。ここに規定された対象幅・スケール・単位・配置・禁止事項を、単純な画面を含むすべての UI 実装で適用する。

構造・責務・API 経路は `docs/coding_style.md` に従う。見た目・寸法・CSS の書き方はこの文書に従う。両者が矛盾する場合は人間へ確認する。

見た目は Tailwind CSS で書く。ユーティリティクラスが視覚の唯一の経路である。

## 1. 目的

タブレットでも 4K モニタでも、画面の**形（構図）が同じ**に見えるようにする。

幅が変わってもカラム数、要素の相対位置、余白と文字の比率を変えない。大きい画面用レイアウトと小さい画面用レイアウトを分岐しない。

## 2. 対象ビューポート

| 項目 | 値 |
|---|---|
| 最小幅 | `1024px`（タブレット横向き） |
| 基準幅 | `1280px` |
| 最大幅 | `3840px`（4K） |
| 対象 | CSS viewport 幅。OS の表示スケール適用後の値 |

`1024px` 未満のスマートフォン縦向きは対象外とする。対象外幅向けの別レイアウト、別コンポーネント、別ルートを追加しない。

高さは固定しない。縦に収まらない内容はスクロールする。横方向の構図を高さのために組み替えない。

物理ピクセル数や端末 DPI で分岐しない。

## 3. スケール

基準幅 `1280px` のとき、ルートの `1rem` はユーザー設定の `1rem`（通常 `16px`）とする。ルートフォントサイズを CSS viewport 幅に比例させ、Tailwind の rem ユーティリティをそれに追従させる。

`frontend/src/app.css` の `@layer base` へ次をそのまま置く。値を画面ごとに変えない。

```css
html {
	font-size: clamp(0.8rem, 1.25vw, 3rem);
}
```

| viewport 幅 | 計算されるルート | 通常環境での目安 |
|---|---|---|
| `1024px` | `0.8rem` | 約 `12.8px` |
| `1280px` | `1rem` | 約 `16px` |
| `1920px` | `1.5rem` | 約 `24px` |
| `3840px` | `3rem` | 約 `48px` |

`clamp` の下限 `0.8rem` は最小幅 `1024px` の比例値、上限 `3rem` は最大幅 `3840px` の比例値である。対象幅の内側では常に `1.25vw` が使われ、線形に拡縮する。

このブロック以外でルートフォントサイズを変更しない。`html` / `:root` / `body` への上書き、`zoom`、ルートへの `transform: scale()` は禁止する。

ユーザーのブラウザ拡大縮小を無効化しない。`text-size-adjust` で拡大を止めない。

Tailwind の spacing / text / size / rounded は rem なので、ルートが変われば画面全体が同じ比率で拡縮する。`p-4` や `text-base` に `px` を足して打ち消さない。

## 4. Tailwind

### 4.1 採用するもの

- Tailwind CSS v4
- 公式の `@tailwindcss/vite`
- `frontend/src/app.css` の `@import 'tailwindcss'`
- マークアップの utility class

PostCSS 設定、`tailwind.config.js` / `tailwind.config.ts`、DaisyUI / Flowbite / shadcn 相当、UnoCSS、CSS-in-JS を追加しない。

### 4.2 置き場所

| 置くもの | 場所 |
|---|---|
| Tailwind の入口、`@theme`、ルートスケール、`body`、`:focus-visible` | `frontend/src/app.css` |
| 画面・コンポーネントの見た目 | その `.svelte` の `class` |

`app.css` はルート layout から1回 import する。

画面とコンポーネントに `<style>` を置いて見た目を書かない。繰り返す見た目は Svelte コンポーネントにする。`@apply` でクラスを再定義しない。

`<style>` がどうしても必要な場合（仕様で明示された例外）は `@reference "tailwindcss"` を置き、この文書の単位・構図・禁止事項を守る。AI がこの例外を作ってはならない。

インライン `style=""` へ寸法・色を書かない。SvelteKit が生成する `display: contents` ラッパは例外とする。

### 4.3 ブレークポイントを無効化する

対象幅で構図を変える手段をフレームワークから除く。`app.css` の `@theme` に次を置く。

```css
@theme {
	--breakpoint-*: initial;
}
```

`--container-*` は消さない。`max-w-3xl` などがこのトークンを参照する。

`sm:` / `md:` / `lg:` / `xl:` / `2xl:` / `max-sm:` / `min-lg:` / `@sm:` / `@md:` などの幅・コンテナバリアントを使わない。ブレークポイントは無効化されている前提で書いてはならない。

JS で `window.innerWidth` や `matchMedia` を見て class を切り替えない。

## 5. 単位とユーティリティ

視覚寸法は Tailwind の rem スケール、`%`、`fr`、`auto` だけを使う。

| 用途 | 使うもの | 使わないもの |
|---|---|---|
| 文字サイズ | `text-sm` `text-base` `text-lg` `text-2xl` `text-3xl` | `text-[13px]`、`text-xs`、`text-4xl` 以上 |
| 余白・gap | 既定の spacing（`p-4` `gap-6` `mt-2` 等） | `p-[16px]`、`m-[0.7rem]` |
| 幅・高さ | 既定の size、`w-full`、`max-w-*`、`flex-1`、`min-w-0` | `w-[400px]`、`w-screen`、`h-screen`、`min-h-screen` |
| 角丸 | 既定の `rounded-*` | `rounded-[10px]` |
| 線幅 | `border`（1px）、`border-2`（2px） | `border-4` 以上、`border-[3px]` |
| 影 | 既定の `shadow-*` | `shadow-[0_4px_...]` |
| 色 | §6 の意味付きトークン | `bg-gray-100`、`text-[#333]`、`bg-red-500` |

arbitrary value（`[...]`）は使わない。足りない段階は、画面のついでに発明せず、この文書と `app.css` の `@theme` を先に更新する。

`w-screen` / `h-screen` / `min-h-screen` / `w-dvw` / `h-dvh` は `vw` / `vh` 直書きと同じなので禁止する。`vw` / `vh` は §3 のルートフォントサイズにだけ使う。

## 6. テーマトークン

色とフォントは `app.css` の `@theme` に固定する。コンポーネントへ hex やデフォルトパレット名を散らさない。

```css
@theme {
	--color-*: initial;
	--color-inherit: inherit;
	--color-current: currentColor;
	--color-transparent: transparent;
	--color-fg: #141820;
	--color-fg-muted: #5c6370;
	--color-fg-inverse: #f5f6f8;
	--color-bg: #eef0f4;
	--color-bg-elevated: #ffffff;
	--color-bg-subtle: #e4e7ed;
	--color-bg-brand: #121826;
	--color-border: #cfd3dc;
	--color-focus: #c45c12;
	--color-accent: #c45c12;
	--color-danger: #b42318;
	--color-success: #157a3e;
	--color-warning: #9a6700;

	--font-sans: system-ui, 'Segoe UI', sans-serif;
}
```

コンポーネントからは次だけを使う。

| 用途 | class |
|---|---|
| 本文色 | `text-fg` |
| 補助色 | `text-fg-muted` |
| 反転本文 | `text-fg-inverse` |
| 背景 | `bg-bg` |
| カード背景 | `bg-bg-elevated` |
| 弱い背景 | `bg-bg-subtle` |
| ブランド面 | `bg-bg-brand` |
| 枠線 | `border-border` |
| フォーカス | `outline-focus` / `ring-focus` |
| アクセント | `text-accent` / `border-accent` / `bg-accent` |
| 危険 | `text-danger` / `bg-danger` |
| 成功 | `text-success` / `bg-success` |
| 注意 | `text-warning` / `bg-warning` |
| フォント | `font-sans` |
| 現在色 | `text-current` |
| 透明 | `bg-transparent` |

本文は `text-base`。補助テキストは `text-sm`。画面タイトルは `text-2xl`。`text-3xl` はページに1つまでの大見出しに限る。

ブランド色や状態色が新たに必要なら、意味のある名前で `@theme` に足し、この節を更新してから使う。`dark:` とダークモード用トークンを要求されていないのに追加しない。

`z-index` は次の層だけを使う。`z-[999]` を置かない。

| 層 | class | 用途 |
|---|---|---|
| 0 | `z-0` | 通常の文書 |
| 10 | `z-10` | ページヘッダ |
| 20 | `z-20` | メニュー、ポップオーバー |
| 30 | `z-30` | ダイアログ |
| 40 | `z-40` | 一時通知 |

画面ごとに `font-sans` 以外の `font-*` を使わない。Web フォントを要求されていないのに追加しない。

`body` のフォント・色・背景は `app.css` の `@layer base` で1回指定する。各ページで `body` 相当を繰り返さない。

## 7. 構図

対象幅のあいだで、レイアウト構造を変えない。

- カラム数を幅で増減しない
- 横並びを縦積みに切り替えない
- ナビゲーションの位置を幅で移さない
- 要素の表示／非表示を幅で切り替えない
- 「デスクトップだけ」「タブレットだけ」のマークアップを持たない

配置は `flex` または `grid` を使う。子の幅は `flex-1`、`w-full`、`min-w-0`、`max-w-*`、`auto` で決める。

ページ全体を何 px 相当にも引き伸ばさない。読み幅が決まっている本文化の塊（フォーム、説明、設定）には `max-w-*` を置く。表やツールバーなど画面幅を使う塊は、親の利用可能幅いっぱいに伸ばしてよい。どちらも幅バリアントで切り替えない。

`fixed` の座標も Tailwind の inset / 既定 size とする。

許可する例:

```svelte
<main class="mx-auto max-w-3xl p-6">
	<h1 class="text-2xl font-semibold text-fg">Title</h1>
	<p class="mt-4 text-base text-fg-muted">Body</p>
</main>
```

禁止する例:

```svelte
<main class="p-[16px] md:grid md:grid-cols-2">
	<aside class="hidden lg:block w-[320px]">Side</aside>
</main>
```

## 8. メディアクエリ

対象幅のあいだで、構図・寸法・表示／非表示を変えるメディアクエリを書いてはならない。Tailwind の幅バリアントも同じ禁止である。

許可するのは次だけである。

- `motion-reduce:`（`prefers-reduced-motion`）
- `contrast-more:` / `forced-colors:`
- `print:`

`prefers-color-scheme` で別パレットへ切り替える場合は、トークン値だけを変え、構図は変えない。要求されていないのにダークモードを追加しない。`dark:` を使わない。

## 9. フォーカスと動き

フォーカス可能な要素からアウトラインを消さない。`outline-none` を単独で置かない。`:focus-visible` は `app.css` で次を使う。

```css
:focus-visible {
	outline: 2px solid var(--color-focus);
	outline-offset: 2px;
}
```

動きは要求されたフィードバックに限る。ホバーや遷移のために構図が変わるアニメーションを標準にしない。`motion-reduce:` で必須でない transition / animation を切る。

## 10. 画像とメディア

`img` / `svg` / `canvas` の表示サイズも `w-*` `h-*` `max-w-full` `h-auto` とする。ビットマップに `w-[24px]` を書かない。

装飾 SVG は `text-current` で親の文字色に合わせる。アイコンサイズは既定の size スケールを使う。

## 11. 禁止パターン一覧

- 対象幅内でのレイアウト分岐（`md:` 等、Container Query、JS の幅判定、手書き `@media`）
- スマートフォン向けレイアウトの先回り実装
- `html` / `:root` / `body` のフォントサイズ上書き（§3 以外）
- `zoom`、ルートの `transform: scale()` による全体縮小
- 文字・余白・幅・高さへの `px` と `p-[16px]` のような arbitrary `px`
- `w-screen` / `h-screen` / コンポーネントへの `vw` / `vh`
- 意味付きトークン以外の色（デフォルトパレット、hex）
- 段階外の余白・文字サイズ
- 任意の `z-[...]`
- `<style>` や `@apply` での見た目定義
- DaisyUI 等のコンポーネント CSS フレームワークの無断追加
- `dark:` と要求されていないダークモード
- 幅で要素を `hidden` する
- ユーザー拡大の無効化

## 12. AI 実装プロトコル

UI を実装する AI は、コードを書く前にこの文書を全文読む。

1. 対象幅 `1024px`〜`3840px` で構図が同じか判定する
2. 見た目を Tailwind の utility class だけで書けるか確認する
3. 新しい寸法が既定スケール、新しい色が §6 のトークンに載るか確認する
4. `px`、幅バリアント、arbitrary value、`<style>` が混入していないか確認する
5. 不足トークンや対象外デバイスの要求があれば、推測で補わず人間へ確認する

検証するときは、少なくとも `1024px` 幅と `3840px` 幅で同じカラム構造・同じ相対位置になることを確認する。見た目の絶対サイズが幅に比例して変わることは欠陥ではない。構図が変わることが欠陥である。

## 13. Definition of Done

- [ ] `frontend/src/app.css` に Tailwind 入口、§3 のルートスケール、§4.3 のブレークポイント無効化、§6 のトークンがある
- [ ] 見た目が utility class だけで、`<style>` と `@apply` が無い
- [ ] 視覚寸法が Tailwind の rem スケールである（線幅 `border` / `border-2` を除く）
- [ ] 対象幅内に幅バリアントとレイアウト用メディアクエリがない
- [ ] `w-screen` / arbitrary `px` / デフォルトパレット色がない
- [ ] `1024px` と `3840px` で構図が同じである
- [ ] ユーザー拡大を無効にしていない
- [ ] 要求されていない CSS フレームワーク / トークン / ダークモードがない

## 14. 規約の変更

この規約自体の変更は通常の画面実装と分離してレビューする。個別画面を通すためにその場でスケール式や対象幅を変えない。

例外が必要な場合は、少なくとも以下を明文化する。

- どの規則の例外か
- なぜ通常規則では成立しないか
- 適用範囲
- 代替案を採用しない理由
- 例外が恒久か一時的か

一度の例外を暗黙の新ルールとして横展開しない。
