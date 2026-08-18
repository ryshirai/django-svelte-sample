# Django DRF + Svelte コーディング規約

AI と人間が Django REST Framework と Svelte の実装を同じ構造・責務・依存方向で再現するための規約。

この文書は設計上の自由度より再現性を優先する。一般的な Django / Svelte の選択肢を列挙する文書ではない。ここに規定された経路・公開 API・命名・禁止事項を、単純な CRUD を含むすべての実装で適用する。

## 1. 優先順位

1. 明示されたプロダクト要件
2. この `docs/coding_style.md`。見た目・寸法・CSS は `docs/frontend_design.md`
3. リポジトリ固有の仕様書
4. 既存コード
5. 一般的な Django / DRF / Svelte 慣習

上位と下位が矛盾する場合は上位を優先する。ただし AI は矛盾を独自解釈で解消してはならず、人間へ確認する。

既存コードがこの規約に違反していても、その違反を新規コードへコピーしない。要求範囲外の既存違反を無断で修正しない。

## 2. 基本原則

- Django 標準と DRF 標準を優先する。Svelte は公式の Svelte / SvelteKit の仕組みを優先する。
- Repository、独自 DI Container、不要な Interface / Protocol / BaseClass を導入しない。
- 読み取りと更新を分離する。
- ORM へ到達する公開経路を Selector と Service に限定する。
- 画面・クライアントは Django ORM を知らない。HTTP API だけを使う。
- 暗黙の副作用を作らない。
- 単純な CRUD でも固定経路を省略しない。
- 将来使うかもしれない抽象化、index、soft delete、共通基盤、状態管理ライブラリを先回りして追加しない。
- 業務ルールの正は backend にある。frontend の検証は UX 用であり、backend 検証の代替にしない。
- AI は要求範囲外の変更、依存追加、リファクタリングを行わない。
- 不明点は推測せず確認する。

## 3. 標準処理経路

### 3.1 読み取り

```text
Svelte page / component
        |
        v
   frontend API client
        |
        v
   DRF API View
        |
        v
     Selector
        |
        v
   Model / ORM
```

### 3.2 更新・副作用

```text
Svelte page / component
        |
        v
   frontend API client
        |
        v
   DRF API View
        |
        v
      Service
        |
        v
   Model / ORM
```

Serializer は入力・出力境界であり ORM を触らない。

Service と Selector は相互に呼ばない。public Service 同士も呼ばない。

Svelte の page / component は `fetch` を直接呼ばない。frontend API client を通す。

## 4. リポジトリ構成

```text
.
├── backend/
│   ├── config/              # Django project（settings, urls, asgi/wsgi）
│   ├── application/         # 唯一の business Django app
│   ├── manage.py
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   ├── static/
│   ├── package.json
│   └── svelte.config.js
└── docs/
```

business Django app は `application` 1つだけとする。frontend は SvelteKit 1アプリとする。

`utils.py`、`common.py`、`misc.py`、`utils.ts`、`helpers.ts` は禁止する。責務を命名できないコードは置き場所を決め直す。

## 5. Backend 固定ディレクトリ

```text
backend/application/
├── models/
├── services/
├── selectors/
├── validators/
├── errors/
├── messages/
├── audit/
├── api/
│   ├── serializers/
│   ├── views/
│   └── urls.py
├── management/
│   └── commands/
├── admin.py
└── apps.py
```

`models.py` は作らず `models/` package を使う。primary Model 単位で Model / Service / Selector module を分割する。

Django template、`forms.Form`、MPA view は使わない。UI は Svelte に置く。

## 6. Frontend 固定ディレクトリ

```text
frontend/src/
├── app.css             # Tailwind 入口、ルートスケール、テーマトークン
├── lib/
│   ├── api/            # Django API への唯一の出口
│   ├── components/     # 再利用 UI。データ取得を持たない
│   ├── errors/         # API error code の型と表示用 mapping
│   ├── messages/       # 画面表示用の定義済み文言
│   ├── types/          # API 契約に対応する型
│   └── states/         # 画面をまたぐ client state（必要なときだけ）
└── routes/             # SvelteKit routing。page が API client を呼ぶ
```

- page（`+page.svelte` / `+page.ts`）は画面固有の組み立てと API client 呼び出しだけを持つ。
- 再利用 UI は `lib/components/` に置き、props でデータを受け取る。
- 画面固有で再利用しないブロックは、その route 配下に colocate する。
- `lib/api/` は backend の primary resource 単位で module を分ける。
- SvelteKit server hook / `+page.server.ts` / form action に業務ルールを置かない。
- frontend から Django ORM、backend 内部 module、DB を直接参照しない。

## 7. 依存方向

| 呼び出し元 | 呼び出し可能 | 呼び出し禁止 |
|---|---|---|
| Svelte page | API client, component, types, messages, states | `fetch` 直呼び, 業務ルール再実装 |
| Svelte component | 子 component, 渡された props / snippet | API client, `fetch`, page 固有 routing 知識 |
| frontend API client | `fetch` wrapper, types, errors | Svelte component, page, 業務ルール |
| DRF View | Serializer, Service, Selector, Error mapping | ORM 直接操作 |
| Serializer | pure Validator, Input dataclass 構築 | ORM, Service, Selector |
| Service | Model, Error, Message code, pure Validator, Audit API | Selector, 他 public Service, View / API, frontend |
| Selector | Model, Filter dataclass, Error | Service, View / API, 書き込み ORM |
| Model | 自身の instance 値だけを使う pure method | Service, Selector, 外部 I/O, ORM query |
| Admin | Selector | 独自 ORM 更新, Service 経由の更新 |
| Command | Service, Selector | ORM 直接操作 |

循環依存を解消するために依存方向を破ってはならない。責務配置を見直す。

## 8. 命名

コード上の識別子は英語のみ。

### 8.1 Backend

| 対象 | 規則 | 例 |
|---|---|---|
| Model | singular PascalCase | `PurchaseApplication` |
| Service | `<verb>_<noun>` | `submit_application` |
| Service Input | `<Verb><Noun>Input` | `SubmitApplicationInput` |
| Single Selector | `get_<noun>` | `get_purchase_application` |
| List Selector | `list_<plural>` | `list_purchase_applications` |
| Filter | `<Noun>Filter` | `PurchaseApplicationFilter` |
| API Input | `<Verb><Noun>InputSerializer` | `CreatePurchaseApplicationInputSerializer` |
| API Output | `<Noun>OutputSerializer` | `PurchaseApplicationOutputSerializer` |
| API List item | `<Noun>ListItemOutputSerializer` | `PurchaseApplicationListItemOutputSerializer` |
| API View | `<noun>_<action>` | `purchase_application_create` |
| Error class | `<Noun><Reason>Error` | `PurchaseApplicationNotFoundError` |
| Error code | `<noun>.<reason>` | `purchase_application.not_found` |

### 8.2 Frontend

| 対象 | 規則 | 例 |
|---|---|---|
| Page route | resource の複数形 / 動作 | `src/routes/purchase-applications/create/+page.svelte` |
| Component | PascalCase | `PurchaseApplicationStatusBadge.svelte` |
| API module | resource の複数形 | `lib/api/purchaseApplications.ts` |
| API function | backend の Service / Selector に対応 | `createPurchaseApplication`, `listPurchaseApplications` |
| Type | Serializer に対応 | `PurchaseApplicationOutput`, `CreatePurchaseApplicationInput` |
| Client state | `<noun>State` | `currentUserState` |

`handler`, `process`, `execute`, `do`, `manager`, `helper` のように責務が曖昧な名前を公開 API に使わない。

## 9. Service

public Service は class ではなく module function とする。

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class SubmitApplicationInput:
    application_id: int
    expected_revision: int


@transaction.atomic
def submit_application(*, input: SubmitApplicationInput) -> None:
    application = PurchaseApplication.objects.select_for_update().get(
        pk=input.application_id,
    )
    application.status = PurchaseApplication.Status.SUBMITTED
    application.save(update_fields=["status"])
```

### 9.1 契約

- public Service は Use Case 固有 Input dataclass のみを業務入力として受ける。
- Input は `@dataclass(frozen=True, slots=True, kw_only=True)`。
- Input に Model instance / QuerySet / request / Serializer を入れない。
- ID、文字列、数値、日付、Enum / Choices 等の値を渡す。
- primary Model ごとに module を分割する。
- 更新 Service は `transaction.atomic` 必須。
- 既存行を更新する場合は原則 `select_for_update()` でロックする。
- `save()` は `update_fields=[...]` を明示する。
- 削除は Service 内で明示的に行う。
- Service は Selector を呼ばない。
- public Service から別 public Service を呼ばない。
- 同一 Use Case の分割は同一 module 内 private function とする。

### 9.2 複数 Model 更新

1つの Use Case が複数 Model / table を更新する場合でも、入口となる public Service は1つにする。同一 transaction 内で必要な Model を直接取得・更新し、private helper へ分割する。

public Service の連鎖でオーケストレーションしない。

### 9.3 読み取りを伴う更新

更新判断に DB 読み取りが必要でも Selector は呼ばない。Service 自身が ORM で必要な行を取得する。読み取りロジックの重複を避けるために Service → Selector を許可することはしない。

## 10. Selector

public Selector は module function とする。

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class PurchaseApplicationFilter:
    status: PurchaseApplication.Status | None = None


def get_purchase_application(*, application_id: int) -> PurchaseApplication:
    try:
        return PurchaseApplication.objects.get(pk=application_id)
    except PurchaseApplication.DoesNotExist as error:
        raise PurchaseApplicationNotFoundError() from error


def list_purchase_applications(
    *,
    filter: PurchaseApplicationFilter,
) -> QuerySet[PurchaseApplication]:
    queryset = PurchaseApplication.objects.all()
    if filter.status is not None:
        queryset = queryset.filter(status=filter.status)
    return queryset
```

### 10.1 契約

- 単一取得は keyword-only 引数。
- 不存在は typed NotFound Error。`None` を返さない。
- 一覧・検索は未評価 QuerySet を返す。
- 一覧条件は frozen Filter dataclass にまとめる。
- Selector は DB write を行わない。
- `select_related` / `prefetch_related` / `annotate` / `only` 等の読み取り最適化は Selector 内に置ける。
- custom Manager / custom QuerySet へ読み取り責務を逃がさない。

### 10.2 QuerySet 契約を維持できない読み取り

ページング、複数種別統合、既評価データの合成等により QuerySet 契約を維持できない読み取りは、仕様で明示された場合のみ評価済み immutable DTO sequence を返してよい。AI が独自にこの例外を作ってはならない。

## 11. Model

Model は ORM 定義、DB constraint、自身の instance 値だけから計算できる pure behavior のみを持つ。

許可例:

```python
def is_submitted(self) -> bool:
    return self.status == self.Status.SUBMITTED
```

禁止:

- Model method 内 ORM query
- related manager への暗黙アクセス
- Model method による状態変更
- Model method 内 `save()` / `delete()`
- `save()` / `delete()` override
- custom Manager / custom QuerySet
- project 固有 Signal
- 独自 `clean()` / `full_clean()`
- 外部 I/O

主キーは原則 `BigAutoField`。共通 BaseModel を作らない。timestamp、soft delete 等も必要な Model に明示する。

DB constraint は DB で保証すべき不変条件に使う。speculative index は追加しない。

## 12. Validator

Validator は pure function とする。

- ORM を呼ばない。
- Service / Selector を呼ばない。
- request / Serializer に依存しない。
- 値を受け取り、成功時は値を返すか `None`、失敗時は定義済み typed business error を送出する。
- 複数境界で再利用される値レベルのルールだけを置く。

DB 状態を必要とする検証は pure Validator ではない。読み取りなら Selector、更新 Use Case の事前条件なら Service 内で実施する。

frontend の入力チェックは Validator の複製ではない。必須・形式などの UX 用チェックに限り、backend の契約と矛盾しない範囲で page 側に置ける。

## 13. Serializer

- `serializers.Serializer` のみ使用する。
- `ModelSerializer` 禁止。
- `PrimaryKeyRelatedField` 禁止。
- Input と Output を必ず別 class にする。
- ORM / Service / Selector を呼ばない。
- Input Serializer は値の検証と Service Input 構築まで。
- Output Serializer は View が Selector / Service から得た出力の表現に限定する。
- frontend の TypeScript 型は、この Serializer 契約に合わせて定義する。型を frontend 独自に発明しない。

## 14. API View

View は function-based view、または業務ロジックを持たない `APIView` のみ。`ViewSet` / `ModelViewSet` / generic CBV を禁止する。

- prefix は `/api/v1/` 固定。
- Input Serializer → Service / Selector → Output Serializer の順とする。
- ORM を直接呼ばない。
- Service 戻り Model を View で mutation / save しない。
- 認証・許可の枠は DRF permission / authentication を使う。
- アプリ固有の ownership / 業務認可は Selector または Service に明示する。
- 成功 status は endpoint 種別ごとに仕様で固定する。
- error response は共通 envelope に固定する。

```json
{
  "error": {
    "code": "purchase_application.not_found",
    "message": "...",
    "details": {}
  }
}
```

未定義の status / error code / envelope を AI が発明しない。

## 15. Admin

Admin は原則 read / inspect 用とする。

- 読み取りに Selector を利用できる。
- 独自 ORM 更新は禁止。
- Service 経由の更新も禁止。
- 業務更新が必要なら通常の API Use Case を用意する。
- Django admin 標準が内部で行う ORM 操作まで禁止対象とはしない。ただし独自 action / `save_model` 等で業務更新を追加しない。

## 16. Management Command

Command は orchestration boundary とする。

- 読み取りは Selector。
- 更新は Service。
- ORM 直接操作は禁止。
- business logic を Command に実装しない。

## 17. Error と Message

予測可能な業務失敗は typed custom exception を使う。business error に Django `ValidationError` を使わない。

```python
class PurchaseApplicationNotFoundError(Exception):
    code = "purchase_application.not_found"
```

- Error class と error code を `errors/` に集約する。
- user-facing message は backend `messages/` に集約する。
- code と message を分離する。
- literal message を View / Service / Model / Svelte component 等へ分散させない。
- frontend は error `code` を受け取り、`lib/errors/` と `lib/messages/` で表示へ写す。
- 未定義 code / message を AI が発明しない。
- programmer error は business error に変換して握り潰さない。

## 18. Audit

Audit が要求される場合のみ `audit/` を使用する。

- Service から公開 Audit API を呼べる。
- Audit API は業務 Service を呼ばない。
- audit failure の transaction 方針は仕様で明示する。
- 任意の audit / log を AI 判断で追加しない。

## 19. Logging

既存 logging policy に従う。要求されていない log を追加しない。`print()` / `console.log()` は禁止。

秘密情報、credential、token、password、個人情報を log へ出さない。

## 20. Transaction と競合

- 更新 Service は `transaction.atomic`。
- 更新対象の既存行は原則 `select_for_update()`。
- lock 順序が複数 Model にまたがる場合は module 内で順序を固定する。
- 外部 I/O を DB transaction 内に入れる必要がある場合は、失敗整合性を仕様で決める。AI が勝手に `on_commit` や retry を導入しない。
- optimistic revision を採用する場合は仕様で明示し、競合は typed error とする。

## 21. 外部 I/O

メール、Storage、HTTP API、queue 等は ORM とは別の副作用である。

- View / Serializer / Model / Selector / Svelte から直接実行しない。
- Service が Use Case として起動する。
- 外部 I/O 用 adapter が必要な場合も、要求された integration 単位の具体 module とし、汎用 Repository / DI abstraction を作らない。
- transaction との整合性、再試行、冪等性が必要なら仕様で定義する。

frontend が第三者と直接通信する必要がある場合も、仕様で明示された integration に限る。Django API で代行できるなら frontend から直接呼ばない。

## 22. Svelte

Svelte 5 + SvelteKit を使う。Svelte 4 store API や独自状態管理ライブラリを先に導入しない。

### 22.1 Page

- 読み取りは `+page.ts` の `load`、または page から API client を呼ぶ。
- 更新は page の event handler から API client を呼ぶ。
- 成功後の再表示は再 fetch、または仕様で決めた client state 更新に限定する。
- 業務ルール、ステータス遷移、認可判定を page に書かない。
- URL の resource 名は backend API の resource と揃える。

### 22.2 Component

- 表示と局所的な UI 状態だけを持つ。
- データ取得、永続化、認可、業務判定を持たない。
- props は明示的に型付けする。
- 再利用しない画面固有 UI を `lib/components/` に上げない。

### 22.3 API client

- Django API への HTTP 呼び出しは `lib/api/` に限定する。
- resource 単位の module function とし、class / SDK generator を無断導入しない。
- 共通 `fetch` wrapper が CSRF、認証ヘッダ、error envelope の解釈を担当する。
- 成功時は Output 型、失敗時は typed API error を返す。
- endpoint path、method、request / response 型を backend 契約と一致させる。
- 未定義 endpoint を frontend 側で発明しない。

```ts
export async function getPurchaseApplication(
  applicationId: number,
): Promise<PurchaseApplicationOutput> {
  return apiGet(`/api/v1/purchase-applications/${applicationId}`);
}
```

### 22.4 状態

- 単一 page 内の状態は `$state` / `$derived`。
- 画面をまたぐ状態だけを `lib/states/` に置く。
- サーバ上の業務データの正本は API 応答である。client cache を正本にしない。
- optimistic update は仕様で明示された場合のみ。
- `$effect` で fetch や書き込みを暗黙実行しない。読み書きの起点は page の `load` またはユーザー操作とする。

### 22.5 CSS

見た目・寸法・CSS の書き方は `docs/frontend_design.md` に従う。

- 見た目は Tailwind CSS の utility class で書く。
- 対象幅は `1024px`〜`3840px`。このあいだで構図を変えない。
- ルートフォントサイズを viewport 幅に比例させ、寸法は Tailwind の rem ユーティリティで書く。
- グローバル CSS は `frontend/src/app.css` のみ（Tailwind 入口、スケール、テーマ）。
- 幅バリアント、寸法の `px`、arbitrary value、画面の `<style>` での見た目定義を禁止する。

### 22.6 ルーティングとサーバ側

- ルーティングは SvelteKit file-based routing を使う。
- `+page.server.ts` や form action を BFF として増やし、backend Use Case を複製しない。
- SvelteKit server から Django 内部コードや DB に接続しない。
- 認証 cookie / CSRF の扱いが必要な場合は仕様に従い、API client の共通 wrapper に閉じる。

## 23. Complexity

public / private function とも以下を上限とする。Svelte の `<script>` も同様。

- cyclomatic complexity ≤ 10
- branch 数 ≤ 12
- statement 数 ≤ 50

超過時は同一 module 内 private function、または page から component への表示分割へ責務を分ける。閾値回避の `# noqa` / `eslint-disable` は禁止。

## 24. Type / Lint / Format

### 24.1 Backend

- mypy strict 必須。
- Ruff Formatter + Linter を唯一の formatter / linter とする。
- `# noqa` 禁止。
- `type: ignore` 禁止。
- 型エラーを suppression せず、型境界を修正する。

### 24.2 Frontend

- TypeScript strict 必須。
- プロジェクトで採用した formatter / linter を唯一の経路とする。追加の独自設定を増やさない。
- class の並びは `prettier-plugin-tailwindcss` に任せる。
- `eslint-disable` / `@ts-ignore` / `@ts-expect-error` / `as any` 禁止。
- API 応答を曖昧な型で受けず、`lib/types/` の契約型を使う。

## 25. テスト

- Use Case の更新仕様は Service test で検証する。
- 読み取り条件は Selector test で検証する。
- Serializer は入力境界を検証する。
- API View test は HTTP routing、status、response mapping を中心にする。
- Model test は pure behavior と DB constraint を中心にする。
- frontend は API client の request / error mapping と、page の表示分岐を検証する。
- component test は props に対する表示と局所 UI 状態に限定する。
- private helper を直接 test せず public contract 経由で検証する。
- test 名は仕様を説明する英語名にする。
- 実装詳細に依存する過剰 mock を避ける。
- frontend test で backend 内部実装を mock して業務ルールを再定義しない。

### 25.1 Backend test のディレクトリ構成

`backend/application/tests/` はフラットに置かず、5章の Backend 固定ディレクトリと同じ type(`services` / `selectors` / `validators` / `api` 等)でサブディレクトリを分ける。

```text
backend/application/tests/
├── services/
├── selectors/
├── validators/
├── api/
│   ├── views/
│   └── serializers/
└── fixtures/          # 複数 test module から共有する fixture
```

- 対応する source module 1 つにつき、同じ type ディレクトリ配下に test module を 1 つ置く(`services/order.py` → `tests/services/test_order.py`)。
- 型はディレクトリで表現し、ファイル名末尾に `_service` 等の type suffix を重複させない。
- 型ディレクトリを見れば、その type の対象すべてに test が揃っているか一覧できることを目的とする。
- 密接に関連する複数 module(例: 登録とセッションのように 1 Use Case 群とみなせるもの)を 1 test module にまとめる場合は、対象 module 名を明示し、まとめる理由を仕様で示す。

## 26. 境界判断

### 26.1 Service から複雑な read が必要

Selector を呼ばない。Service module 内 private query helper、または Service 内 ORM を使う。read API の再利用より依存方向を優先する。

### 26.2 複数 Use Case で同じ更新ロジックが必要

public Service を共通関数として呼び回さない。完全に同じ primary Model の内部操作なら、その Model の Service module 内 private helper として共有する。module をまたぐ共通化が必要に見える場合は人間に設計確認する。

### 26.3 画面の select 候補に DB 値が必要

API → Selector で候補を取得し、frontend は Output を表示する。Svelte component や Serializer から Selector を呼ばない。

### 26.4 Service が作成後 Model を View に返したい

原則 ID または immutable result dataclass を返す。View が Model を変更できる契約を作らない。画面表示の再取得が必要なら成功後に Selector 経由の GET を使う。

### 26.5 NotFound と業務上の利用不可

存在しないことは typed NotFound Error。存在するが現在の状態では操作できないことは別の typed business error。Selector の filter で「操作不可」を「不存在」に偽装しない。frontend も同じ code を別の意味に読み替えない。

### 26.6 uniqueness の確認

表示・事前案内の read は Selector に置ける。更新時の競合防止は Service + DB constraint が最終責任を持つ。事前 SELECT や frontend の重複チェックだけを整合性保証にしない。

### 26.7 bulk update / bulk create

性能要件または仕様上必要な場合のみ Service 内で使用する。`save()`、signal 等が走らない性質を理解し、暗黙副作用禁止と整合させる。AI が性能推測だけで導入しない。

### 26.8 soft delete

原則導入しない。要件で必要な場合のみ、通常の状態として Model に明示し、全 Selector / Service 契約を仕様化してから採用する。共通 BaseModel や custom Manager で暗黙化しない。

### 26.9 Django / DRF authentication / permission

Django / DRF 標準 authentication / permission の内部 ORM は禁止対象外。アプリ固有の ownership / business authorization query は Selector または Service の責務として明示する。frontend の表示制御は認可の代替にしない。

### 26.10 migration

migration は Django migration framework を使う。data migration が必要な場合、migration の historical model API は例外として ORM を直接使用できる。runtime Service / Selector を migration から import しない。

### 26.11 同じ検証を frontend にも置きたい

必須・形式など即時フィードバックが必要なものだけ page に置く。状態遷移、一意性、権限、他レコード参照は backend のみ。frontend 独自の業務 error code を作らない。

### 26.12 SvelteKit を BFF にしたい

原則採用しない。認証・CORS・cookie のための最小 proxy が仕様で必要な場合のみ。Use Case の複製、データの組み替え、認可の再実装を SvelteKit server に置かない。

## 27. 禁止パターン一覧

- Repository
- 独自 DI Container
- 不要な Interface / Protocol / BaseClass
- Service class / Selector class
- `utils.py` / `common.py` / `misc.py` / `utils.ts` / `helpers.ts`
- custom Manager / QuerySet
- project 固有 Django Signal
- Model `save` / `delete` override
- Model 独自 `clean` / `full_clean`
- ModelSerializer / ModelForm
- PrimaryKeyRelatedField / ModelChoiceField
- ViewSet / ModelViewSet / writing generic CBV
- Django template / MPA Form view
- View / Serializer / Command / Admin の ORM 直接操作
- Service → Selector
- Selector → Service
- public Service → public Service
- Selector の DB write
- View による Service 戻り Model の mutation / save
- business error への Django ValidationError
- user-facing message literal の分散
- Svelte page / component からの `fetch` 直呼び
- component 内での API 呼び出し
- `$effect` による暗黙 fetch / 書き込み
- 対象幅内でのレイアウト分岐 / 寸法の `px` / Tailwind 幅バリアント / 画面の `<style>` での見た目定義
- SvelteKit server への業務ロジック複製
- 未定義 endpoint / error code の frontend 発明
- `# noqa` / `type: ignore` / `eslint-disable` / `as any`
- `print()` / `console.log()`
- 任意の log 追加
- soft delete / BaseModel の無断追加
- speculative index
- 要求外 dependency の追加
- 要求外 abstraction / refactor

## 28. AI 実装プロトコル

AI は実装前に以下を順に判定する。

1. 要求を read / write / boundary / infrastructure / UI に分類する。
2. primary Model と対応する frontend route / API client を特定する。
3. 変更対象 module と公開 API 名をこの規約から決める。
4. 既存仕様とこの規約の矛盾を確認する。
5. 不明な business rule / code / message / status / endpoint があれば作業を止めて確認する。
6. UI を含む場合は `docs/frontend_design.md` を全文読み、対象幅で構図が同じまま実装する。
7. 最小変更で実装する。
8. backend は Ruff、mypy、test を実行する。frontend は formatter / lint / typecheck / test を実行する。
9. 禁止依存、ORM 直接操作、frontend の `fetch` 直呼び、UI の `px` / 幅バリアント / レイアウト分岐をセルフレビューする。

AI がしてはならないこと:

- 「より綺麗」「将来便利」を理由に構造を変更する。
- 既存の違反を見つけたことを理由に要求範囲を拡張する。
- 未定義仕様を一般論で補完する。
- test を通すためにこの規約を回避する。

## 29. Definition of Done

- [ ] Read は Selector、Write / Side Effect は Service を通る
- [ ] View / API / Serializer / Command / Admin に禁止 ORM がない
- [ ] Service ↔ Selector 呼び出しがない
- [ ] public Service 間呼び出しがない
- [ ] 更新 Service が `transaction.atomic` を持つ
- [ ] 既存行更新で必要な lock と `update_fields` が明示されている
- [ ] Model が pure contract を守る
- [ ] Input / Filter dataclass が frozen + slots + kw_only
- [ ] Serializer が ORM 非依存
- [ ] frontend の HTTP 呼び出しが API client に閉じている
- [ ] page / component に業務ルールがない
- [ ] UI が `docs/frontend_design.md` のスケール・単位・構図を守っている
- [ ] typed error code と message が分離されている
- [ ] message literal が分散していない
- [ ] complexity 上限内
- [ ] mypy strict が通る
- [ ] TypeScript strict が通る
- [ ] Ruff が通る
- [ ] frontend formatter / linter が通る
- [ ] test が通る
- [ ] `noqa` / `type: ignore` / `eslint-disable` / `print()` / `console.log()` がない
- [ ] 要求外 dependency / abstraction / index / log がない
- [ ] 未定義仕様を AI が発明していない

## 30. 規約の変更

この規約自体の変更は通常実装と分離してレビューする。個別機能を通すためにその場で規約を緩和しない。

例外が必要な場合は、少なくとも以下を明文化する。

- どの規則の例外か
- なぜ通常規則では成立しないか
- 適用範囲
- 代替案を採用しない理由
- 例外が恒久か一時的か

一度の例外を暗黙の新ルールとして横展開しない。
