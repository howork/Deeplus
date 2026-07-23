<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# 부록 B — 토큰, 키워드 및 연산자

## 어휘 토큰 범주

| 토큰/범주 | 문법 줄 |
|---|---:|
| `IDENTIFIER` | 44 |
| `WILDCARD` | 47 |
| `HARD_KEYWORD` | 50 |
| `NUMERIC_LITERAL` | 65 |
| `INTEGER_LITERAL` | 66 |
| `FLOAT_LITERAL` | 71 |
| `DECIMAL_INTEGER` | 77 |
| `CHAR_LITERAL` | 93 |
| `PLAIN_STRING_LITERAL` | 101 |
| `STRING_START` | 102 |
| `STRING_TEXT` | 103 |
| `STRING_ESCAPE` | 104 |
| `INTERPOLATION_BOUNDARY` | 105 |
| `INTERPOLATION_OPEN` | 106 |
| `INTERPOLATION_CLOSE` | 107 |
| `INTERPOLATION_FORMAT_TEXT` | 108 |
| `STRING_END` | 109 |
| `RAW_STRING_LITERAL` | 112 |
| `MULTILINE_STRING_LITERAL` | 113 |
| `BYTES_LITERAL` | 114 |
| `PATH_SEP` | 117 |
| `FAT_ARROW` | 118 |
| `ARROW` | 119 |
| `DOT_DOT` | 120 |
| `DOT_DOT_LT` | 121 |
| `DOT_DOT_GT` | 122 |
| `ELLIPSIS` | 123 |
| `TRIPLE_STAR` | 124 |
| `DOUBLE_STAR` | 125 |
| `STAR_PLUS` | 126 |
| `STAR_DOT` | 127 |
| `AMP_AMP` | 128 |
| `PIPE_PIPE` | 129 |
| `CARET_CARET` | 130 |
| `QUESTION_COLON` | 131 |
| `DOUBLE_DOLLAR` | 132 |
| `EQ_EQ` | 133 |
| `BANG_EQ` | 134 |
| `LT_EQ` | 135 |
| `GT_EQ` | 136 |
| `PLUS_EQ` | 137 |
| `MINUS_EQ` | 138 |
| `STAR_EQ` | 139 |
| `SLASH_EQ` | 140 |
| `PERCENT_EQ` | 141 |
| `TILDE_TILDE` | 142 |
| `COLON_EQ` | 143 |
| `BANG_BANG` | 144 |
| `DOUBLE_L_BRACE` | 145 |
| `DOUBLE_R_BRACE` | 146 |
| `DOLLAR_L_BRACE` | 147 |
| `EOF_TOKEN` | 155 |
| `NAME_TOKEN` | 157 |
| `EOF` | 158 |

## 하드 키워드

| 단어 |
|---|
| `and` |
| `as` |
| `catch` |
| `class` |
| `def` |
| `defer` |
| `else` |
| `enum` |
| `false` |
| `finally` |
| `for` |
| `if` |
| `import` |
| `in` |
| `let` |
| `match` |
| `module` |
| `not` |
| `null` |
| `or` |
| `repeat` |
| `return` |
| `throw` |
| `trait` |
| `true` |
| `try` |
| `type` |
| `use` |
| `var` |
| `while` |

## 문맥 단어

| 단어 |
|---|
| `C` |
| `abstract` |
| `actor` |
| `any` |
| `async` |
| `await` |
| `backing` |
| `bitfield` |
| `borrow` |
| `borrowed` |
| `break` |
| `budget` |
| `c` |
| `cancellable` |
| `capability` |
| `capacity` |
| `catalog` |
| `cleanup` |
| `clone` |
| `common` |
| `conformance` |
| `conforms` |
| `consume` |
| `context` |
| `continue` |
| `copy` |
| `data` |
| `deep` |
| `delegate` |
| `effects` |
| `ensures` |
| `entry` |
| `equalsRatio` |
| `error` |
| `errors` |
| `export` |
| `extension` |
| `extern` |
| `facet` |
| `final` |
| `flags` |
| `forward` |
| `generate` |
| `get` |
| `group` |
| `guard` |
| `inout` |
| `is` |
| `isolated` |
| `law` |
| `lazy` |
| `lsb0` |
| `mailbox` |
| `map` |
| `move` |
| `mut` |
| `on` |
| `once` |
| `opaque` |
| `open` |
| `order` |
| `otherwise` |
| `out` |
| `owned` |
| `pack` |
| `preview` |
| `private` |
| `protocol` |
| `public` |
| `pure` |
| `raw` |
| `request` |
| `requires` |
| `resource` |
| `ret` |
| `schema` |
| `scope` |
| `scoped` |
| `sealed` |
| `send` |
| `set` |
| `shielded` |
| `signature` |
| `some` |
| `spawn` |
| `static` |
| `super` |
| `task` |
| `then` |
| `throws` |
| `to` |
| `typeof` |
| `typestate` |
| `unit` |
| `unsafe` |
| `using` |
| `value` |
| `via` |
| `where` |
| `witness` |
| `yield` |

## Pratt 연산자 소유자

| 도메인 | ID | 토큰 | 결합력 | 결합 방향 |
|---|---|---|---|---|
| `expression` | `assignment` | `= / += / -= / *= / /= / %=` | 10/9 | right |
| `expression` | `ternary` | `? / :` | 20/19 | right |
| `expression` | `otherwise` | `otherwise` | 30/31 | left |
| `expression` | `or` | `or` | 40/41 | left |
| `expression` | `and_then` | `and then` | 50/51 | left |
| `expression` | `and` | `and` | 60/61 | left |
| `expression` | `comparison` | `== / != / < / <= / > / >= / in / ! in / is / ! is` | 70/71 | checker_bounded_chain |
| `expression` | `option_coalesce` | `?:` | 80/79 | right |
| `expression` | `bitwise_or` | `\|\|` | 90/91 | left |
| `expression` | `bitwise_xor` | `^^` | 100/101 | left |
| `expression` | `bitwise_and` | `&&` | 110/111 | left |
| `expression` | `range` | `.. / ..<` | 120/121 | nonassociative |
| `expression` | `additive` | `+ / -` | 130/131 | left |
| `expression` | `multiplicative` | `* / / / %` | 140/141 | left |
| `expression` | `linear_product` | `** / *+` | 150/151 | left |
| `expression` | `power` | `^` | 160/159 | right |
| `expression` | `prefix` | `+ / - / not / ~~ / move / borrow / & / await` | /170 | right |
| `expression` | `cast` | `as ? / as !` | 180/ | nonassociative |
| `expression` | `postfix` | `` | 190/ | left |
| `type` | `union` | `\|` | 10/11 |  |
| `type` | `intersection` | `&` | 20/21 |  |
| `type` | `ownership` | `owned / borrowed / mut / inout` | /30 |  |
| `type` | `optional` | `?` | 40/ |  |
| `unit` | `product` | `*` | 20/21 |  |
| `unit` | `division` | `/` | 20/21 |  |
| `unit` | `power` | `^` | 30/ |  |
