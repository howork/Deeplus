<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# 부록 B — 토큰, 키워드 및 연산자

## 어휘 토큰 범주

| 토큰/범주 | 문법 줄 |
|---|---:|
| `IDENTIFIER` | 44 |
| `WILDCARD` | 47 |
| `HARD_KEYWORD` | 50 |
| `NUMERIC_LITERAL` | 68 |
| `IMAGINARY_LITERAL` | 73 |
| `RATIONAL_LITERAL` | 78 |
| `INTEGER_LITERAL` | 79 |
| `FLOAT_LITERAL` | 84 |
| `DECIMAL_INTEGER` | 90 |
| `CHAR_LITERAL` | 106 |
| `PLAIN_STRING_LITERAL` | 114 |
| `STRING_START` | 115 |
| `STRING_TEXT` | 116 |
| `STRING_ESCAPE` | 117 |
| `INTERPOLATION_BOUNDARY` | 118 |
| `INTERPOLATION_OPEN` | 119 |
| `INTERPOLATION_CLOSE` | 120 |
| `INTERPOLATION_FORMAT_TEXT` | 121 |
| `STRING_END` | 122 |
| `RAW_STRING_LITERAL` | 126 |
| `MULTILINE_STRING_LITERAL` | 127 |
| `BYTES_LITERAL` | 128 |
| `PATH_SEP` | 131 |
| `FAT_ARROW` | 132 |
| `ARROW` | 133 |
| `DOT_DOT` | 134 |
| `DOT_DOT_LT` | 135 |
| `DOT_DOT_GT` | 136 |
| `ELLIPSIS` | 137 |
| `TRIPLE_STAR` | 138 |
| `DOUBLE_STAR` | 139 |
| `STAR_PLUS` | 140 |
| `STAR_DOT` | 141 |
| `AMP_AMP` | 142 |
| `PIPE_PIPE` | 143 |
| `CARET_CARET` | 144 |
| `QUESTION_COLON` | 145 |
| `DOUBLE_DOLLAR` | 146 |
| `EQ_EQ` | 147 |
| `BANG_EQ` | 148 |
| `LT_EQ` | 149 |
| `GT_EQ` | 150 |
| `PLUS_EQ` | 151 |
| `MINUS_EQ` | 152 |
| `STAR_EQ` | 153 |
| `SLASH_EQ` | 154 |
| `PERCENT_EQ` | 155 |
| `TILDE_TILDE` | 156 |
| `COLON_EQ` | 157 |
| `BANG_BANG` | 158 |
| `DOUBLE_L_BRACE` | 159 |
| `DOUBLE_R_BRACE` | 160 |
| `DOLLAR_L_BRACE` | 161 |
| `EOF_TOKEN` | 169 |
| `NAME_TOKEN` | 171 |
| `EOF` | 172 |

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
| `auto` |
| `await` |
| `backing` |
| `bitfield` |
| `borrow` |
| `borrowed` |
| `break` |
| `budget` |
| `by` |
| `c` |
| `cancellable` |
| `capability` |
| `capacity` |
| `catalog` |
| `cleanup` |
| `clone` |
| `common` |
| `concur` |
| `conform` |
| `conformance` |
| `conforms` |
| `consume` |
| `context` |
| `continue` |
| `copy` |
| `data` |
| `deep` |
| `delegate` |
| `derives` |
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
| `supports` |
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
| `expression` | `numeric_prefix_sign` | `+ / -` | /159 | right |
| `expression` | `prefix` | `not / ~~ / move / borrow / & / await` | /170 | right |
| `expression` | `cast` | `as ? / as !` | 180/ | nonassociative |
| `expression` | `postfix` | `` | 190/ | left |
| `type` | `union` | `\|` | 10/11 |  |
| `type` | `intersection` | `&` | 20/21 |  |
| `type` | `ownership` | `owned / borrowed / mut / inout` | /30 |  |
| `type` | `optional` | `?` | 40/ |  |
| `unit` | `product` | `*` | 20/21 |  |
| `unit` | `division` | `/` | 20/21 |  |
| `unit` | `power` | `^` | 30/ |  |
