<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# 부록 A — 정확한 문법 production 참조

권위 원천은 `spec/grammar/deeplus.ebnf`입니다. 이름만 나열하지 않고 모든 production의 정확한 오른쪽 항을 주석을 제외한 정규화된 EBNF로 한 번씩 투영합니다. 줄 번호는 원천을 찾아가기 위한 보조 정보이며 이 부록 자체가 별도 문법 권위는 아닙니다.

## `LEXICAL` 프로파일 — 91개

| 문법 production | 정확한 EBNF 오른쪽 항 | 원천 줄 |
|---|---|---:|
| `SourceCharacter` | `UnicodeScalar` | 39 |
| `LineTerminator` | `"\\r\\n" \| "\\n"` | 40 |
| `HorizontalSpace` | `" " \| "\\t"` | 41 |
| `IDENTIFIER` | `UnicodeXIDStart IdentifierContinue* \| "_" IdentifierContinue+` | 44 |
| `IdentifierContinue` | `UnicodeXIDContinue` | 46 |
| `WILDCARD` | `"_"` | 47 |
| `HARD_KEYWORD` | `ScannerHardKeywordToken` | 50 |
| `Shebang` | `"#!" ShebangScalar* LineTerminator` | 52 |
| `LineComment` | `"//" LineCommentScalar*` | 53 |
| `DocLineComment` | `"//!" DocLineCommentScalar*` | 54 |
| `NestedBlockComment` | `BlockCommentOpen BlockCommentItem* BlockCommentClose` | 55 |
| `BlockCommentOpen` | `"//" DashRun` | 58 |
| `BlockCommentClose` | `DashRun "//"` | 59 |
| `DashRun` | `"-" "-"*` | 60 |
| `BlockCommentItem` | `NestedBlockComment \| BlockCommentScalar` | 61 |
| `DocBlockComment` | `"//!!" DocBlockCommentScalar* "!!//"` | 62 |
| `WordComment` | `"\`" WordCommentScalar+` | 63 |
| `NUMERIC_LITERAL` | `FLOAT_LITERAL \| INTEGER_LITERAL` | 65 |
| `IMAGINARY_LITERAL` | `ScannerImaginaryFloatLiteral` | 70 |
| `RATIONAL_LITERAL` | `ScannerRationalLiteralAtExpressionPrefix` | 75 |
| `INTEGER_LITERAL` | `BinaryInteger IntegerSuffix? \| OctalInteger IntegerSuffix? \| HexInteger IntegerSuffix? \| DECIMAL_INTEGER IntegerSuffix?` | 76 |
| `FLOAT_LITERAL` | `DecimalFraction ExponentPart? FloatSuffix? \| DECIMAL_INTEGER ExponentPart FloatSuffix? \| DECIMAL_INTEGER FloatSuffix` | 81 |
| `BinaryInteger` | `("0b" \| "0B") BinaryDigits` | 84 |
| `OctalInteger` | `("0o" \| "0O") OctalDigits` | 85 |
| `HexInteger` | `("0x" \| "0X") HexDigits` | 86 |
| `DECIMAL_INTEGER` | `DecimalDigits` | 87 |
| `DecimalFraction` | `DecimalDigits "." DecimalDigits` | 88 |
| `ExponentPart` | `("e" \| "E") ("+" \| "-")? DecimalDigits` | 89 |
| `IntegerSuffix` | `"i8" \| "i16" \| "i32" \| "i64" \| "i128" \| "isize" \| "u8" \| "u16" \| "u32" \| "u64" \| "u128" \| "usize"` | 90 |
| `FloatSuffix` | `"f32" \| "f64"` | 92 |
| `BinaryDigits` | `BinaryDigit ("_"? BinaryDigit)*` | 93 |
| `OctalDigits` | `OctalDigit ("_"? OctalDigit)*` | 94 |
| `DecimalDigits` | `DecimalDigit ("_"? DecimalDigit)*` | 95 |
| `HexDigits` | `HexDigit ("_"? HexDigit)*` | 96 |
| `BinaryDigit` | `"0" \| "1"` | 97 |
| `OctalDigit` | `"0" \| "1" \| "2" \| "3" \| "4" \| "5" \| "6" \| "7"` | 98 |
| `DecimalDigit` | `"0" \| "1" \| "2" \| "3" \| "4" \| "5" \| "6" \| "7" \| "8" \| "9"` | 99 |
| `HexDigit` | `DecimalDigit \| "a" \| "b" \| "c" \| "d" \| "e" \| "f" \| "A" \| "B" \| "C" \| "D" \| "E" \| "F"` | 100 |
| `CHAR_LITERAL` | `"'" CharScalar "'"` | 103 |
| `CharScalar` | `DirectCharScalar \| SimpleCharEscape \| UnicodeScalarEscape \| NamedUnicodeEscape` | 104 |
| `SimpleCharEscape` | `"\\\\0" \| "\\\\n" \| "\\\\r" \| "\\\\t" \| "\\\\'" \| "\\\\\\\\"` | 105 |
| `UnicodeScalarEscape` | `"\\\\u{" HexScalarDigits "}"` | 106 |
| `NamedUnicodeEscape` | `"\\\\N{" UnicodeName "}"` | 107 |
| `HexScalarDigits` | `HexDigit HexDigit? HexDigit? HexDigit? HexDigit? HexDigit?` | 108 |
| `PLAIN_STRING_LITERAL` | `ScannerPlainStringLiteral` | 111 |
| `STRING_START` | `ScannerInterpolatedStringStart` | 112 |
| `STRING_TEXT` | `ScannerInterpolatedStringText` | 113 |
| `STRING_ESCAPE` | `ScannerStringEscape` | 114 |
| `INTERPOLATION_BOUNDARY` | `ScannerInterpolationBoundary` | 115 |
| `INTERPOLATION_OPEN` | `ScannerInterpolationOpen` | 116 |
| `INTERPOLATION_CLOSE` | `ScannerInterpolationClose` | 117 |
| `INTERPOLATION_FORMAT_TEXT` | `ScannerInterpolationFormatText` | 118 |
| `STRING_END` | `ScannerInterpolatedStringEnd` | 119 |
| `RAW_STRING_LITERAL` | `ScannerRawStringLiteral` | 123 |
| `MULTILINE_STRING_LITERAL` | `ScannerMultilineStringLiteral` | 124 |
| `BYTES_LITERAL` | `ScannerBytesLiteral` | 125 |
| `PATH_SEP` | `"::"` | 128 |
| `FAT_ARROW` | `"=>"` | 129 |
| `ARROW` | `"->"` | 130 |
| `DOT_DOT` | `".."` | 131 |
| `DOT_DOT_LT` | `"..<"` | 132 |
| `DOT_DOT_GT` | `"..>"` | 133 |
| `ELLIPSIS` | `"..."` | 134 |
| `TRIPLE_STAR` | `"***"` | 135 |
| `DOUBLE_STAR` | `"**"` | 136 |
| `STAR_PLUS` | `"*+"` | 137 |
| `STAR_DOT` | `"*."` | 138 |
| `AMP_AMP` | `"&&"` | 139 |
| `PIPE_PIPE` | `"\|\|"` | 140 |
| `CARET_CARET` | `"^^"` | 141 |
| `QUESTION_COLON` | `"?:"` | 142 |
| `DOUBLE_DOLLAR` | `"$$"` | 143 |
| `EQ_EQ` | `"=="` | 144 |
| `BANG_EQ` | `"!="` | 145 |
| `LT_EQ` | `"<="` | 146 |
| `GT_EQ` | `">="` | 147 |
| `PLUS_EQ` | `"+="` | 148 |
| `MINUS_EQ` | `"-="` | 149 |
| `STAR_EQ` | `"*="` | 150 |
| `SLASH_EQ` | `"/="` | 151 |
| `PERCENT_EQ` | `"%="` | 152 |
| `TILDE_TILDE` | `"~~"` | 153 |
| `COLON_EQ` | `":="` | 154 |
| `BANG_BANG` | `"!!"` | 155 |
| `DOUBLE_L_BRACE` | `"{{"` | 156 |
| `DOUBLE_R_BRACE` | `"}}"` | 157 |
| `DOLLAR_L_BRACE` | `"${"` | 158 |
| `Trivia` | `HorizontalSpace \| LineTerminator \| LineComment \| NestedBlockComment \| DocLineComment \| DocBlockComment \| WordComment` | 163 |
| `EOF_TOKEN` | `EOF` | 166 |
| `NAME_TOKEN` | `ScannerEscapedNameToken` | 168 |
| `EOF` | `ScannerEndOfInput` | 169 |

## `STABLE` 프로파일 — 459개

| 문법 production | 정확한 EBNF 오른쪽 항 | 원천 줄 |
|---|---|---:|
| `Identifier` | `IDENTIFIER` | 177 |
| `QualifiedPath` | `Identifier ("::" Identifier)*` | 180 |
| `TopLevelVisibility` | `"public" \| "private" \| "common"` | 182 |
| `MemberVisibility` | `"+" \| "-" \| "#"` | 191 |
| `ClassDispatchMarker` | `"." \| "+" \| "*." \| "*+"` | 192 |
| `TraitWitnessMarker` | `"." \| "+" \| "*." \| "*+"` | 193 |
| `VarianceMarker` | `"out" \| "in"` | 194 |
| `AnnotationAttachment` | `Annotation+` | 196 |
| `Annotation` | `"@" Identifier ArgumentList? LineBreakBoundary` | 197 |
| `RoleWord` | `Identifier \| HARD_KEYWORD` | 202 |
| `HashTag` | `"#" RoleWord` | 203 |
| `TypeParameterList` | `"<" TypeParameter ("," TypeParameter)* ","? ">"` | 206 |
| `TypeParameter` | `VarianceMarker? Identifier TypeParameterKindAnnotation?` | 207 |
| `TypeParameterKindAnnotation` | `":" TypeParameterKind` | 208 |
| `TypeParameterKind` | `"type" \| "StaticInt" \| "EffectRow" \| "ErrorSet"` | 209 |
| `TypeArgumentList` | `"<" TypeArgument ("," TypeArgument)* ","? ">"` | 211 |
| `TypeArgument` | `TypeRef \| StaticIntLiteral \| ErrorTypeArgument` | 212 |
| `ErrorTypeArgument` | `"error" TypeRef` | 213 |
| `TraitReferenceList` | `QualifiedTypeReference ("," QualifiedTypeReference)*` | 215 |
| `AssociatedTypeConstraintList` | `"where" AssociatedTypeConstraint ("," AssociatedTypeConstraint)*` | 216 |
| `AssociatedTypeConstraint` | `Identifier "==" TypeRef \| Identifier "conforms" QualifiedTypeReference` | 217 |
| `WhereClause` | `"where" WherePredicate ("," WherePredicate)*` | 220 |
| `WherePredicate` | `TypeRef "conforms" QualifiedTypeReference \| TypeRef "==" TypeRef \| RowPredicate` | 221 |
| `RowPredicate` | `Identifier "<=" EffectRow` | 224 |
| `EffectRow` | `EffectRowTerm ("\|" EffectRowTerm)*` | 226 |
| `EffectRowTerm` | `Identifier \| QualifiedTypeReference \| EffectSetLiteral` | 227 |
| `ErrorSet` | `ErrorSetTerm ("\|" ErrorSetTerm)*` | 228 |
| `ErrorSetTerm` | `Identifier \| QualifiedTypeReference` | 229 |
| `EffectSetLiteral` | `"{" IdentifierList? "}"` | 230 |
| `TypeAnnotation` | `":" TypeRef RefinementClause?` | 232 |
| `RefinementClause` | `"where" PredicateExpr` | 233 |
| `Initializer` | `"=" Expr` | 234 |
| `NameAliasClause` | `"as" Identifier` | 235 |
| `ReturnClause` | `"->" NonFunctionTypeRef` | 238 |
| `ThrowsClause` | `"throws" ErrorSet` | 239 |
| `EffectsClause` | `"effects" EffectRow` | 240 |
| `ContractClause` | `RequiresClause \| EnsuresClause` | 241 |
| `RequiresClause` | `"requires" PredicateExpr` | 242 |
| `EnsuresClause` | `"ensures" PredicateExpr` | 243 |
| `LineBreakBoundary` | `LINE_BREAK_IN_TRIVIA` | 248 |
| `StatementBoundary` | `STATEMENT_BOUNDARY_BY_CONTEXT` | 249 |
| `IdentifierList` | `Identifier ("," Identifier)* ","?` | 251 |
| `ExpressionList` | `Expr ("," Expr)* ","?` | 252 |
| `PatternList` | `Pattern ("," Pattern)* ","?` | 253 |
| `StaticIntLiteral` | `DECIMAL_INTEGER` | 255 |
| `UnitSyntax` | `"(" ")"` | 258 |
| `SignedStaticInt` | `("+" \| "-")? StaticIntLiteral` | 259 |
| `LawDecl` | `"law" Identifier LawBody? StatementBoundary` | 261 |
| `LawBody` | `"{" LawBodyItem* "}"` | 264 |
| `LawBodyItem` | `LawAssertion StatementBoundary` | 265 |
| `LawAssertion` | `("requires" \| "ensures" \| "invariant")? PredicateExpr` | 266 |
| `Deeplus` | `LibrarySourceFile \| ExecutableSourceFile \| ScriptSourceFile` | 274 |
| `LibrarySourceFile` | `ModuleDecl? LibrarySourceItem*` | 276 |
| `ExecutableSourceFile` | `ModuleDecl? ExecutableSourceItem*` | 277 |
| `ScriptSourceFile` | `Shebang? ModuleDecl? ScriptSourceItem*` | 278 |
| `LibrarySourceItem` | `AnnotationAttachment LibraryAnnotatableDecl \| ImportOrUseDecl \| TopLevelDecl` | 280 |
| `ExecutableSourceItem` | `AnnotationAttachment ExecutableAnnotatableDecl \| ImportOrUseDecl \| NonBindingTopLevelDecl \| EntryFunctionDecl` | 283 |
| `ScriptSourceItem` | `AnnotationAttachment ScriptAnnotatableDecl \| ImportOrUseDecl \| NonBindingTopLevelDecl \| Stmt` | 287 |
| `LibraryAnnotatableDecl` | `ImportOrUseDecl \| TopLevelDecl` | 292 |
| `ExecutableAnnotatableDecl` | `ImportOrUseDecl \| NonBindingTopLevelDecl \| EntryFunctionDecl` | 293 |
| `ScriptAnnotatableDecl` | `ImportOrUseDecl \| NonBindingTopLevelDecl` | 294 |
| `ModuleDecl` | `"module" QualifiedPath StatementBoundary` | 296 |
| `ImportOrUseDecl` | `ImportDecl \| UseDecl \| UseExportDecl` | 298 |
| `ImportDecl` | `"import" QualifiedPath ImportTail? StatementBoundary` | 299 |
| `ImportTail` | `ImportAlias \| ImportSelection` | 300 |
| `ImportAlias` | `NameAliasClause` | 301 |
| `ImportSelection` | `"::" "{" IdentifierList "}"` | 302 |
| `UseDecl` | `"use" QualifiedPath StatementBoundary` | 303 |
| `UseExportDecl` | `"use" "export" QualifiedPath StatementBoundary` | 304 |
| `ExportDecl` | `"export" ExportItem StatementBoundary?` | 307 |
| `ExportItem` | `ExportableModuleFunctionDecl \| TypeDecl \| Identifier` | 308 |
| `ExportableModuleFunctionDecl` | `TopLevelVisibility? "def" Identifier FunctionRest` | 309 |
| `TopLevelDecl` | `NonBindingTopLevelDecl \| TopLevelBindingDecl` | 317 |
| `NonBindingTopLevelDecl` | `TypeDecl \| ModuleFunctionDecl \| ExtensionFunctionDecl \| ActorDecl \| ActorProtocolDecl \| TypestateResourceDecl \| NamedEffectCapabilityDecl \| ExtensionSetDecl \| ExtensionPackDecl \| UnitCatalogDecl \| ModuleInterfaceDecl \| ConformanceDecl \| SchemaDecl \| BitfieldDecl` | 318 |
| `TypeDecl` | `ClassDecl \| TraitDecl \| EnumDecl \| TypeAliasDecl` | 333 |
| `DefIntroducer` | `"def" HashTag*` | 337 |
| `ModuleFunctionDecl` | `TopLevelVisibility? DefIntroducer Identifier FunctionRest` | 339 |
| `EntryFunctionDecl` | `DefIntroducer Identifier EntryFunctionRest` | 340 |
| `ExtensionFunctionDecl` | `TopLevelVisibility? DefIntroducer TypeRef ExtensionFunctionTarget Identifier FunctionRest` | 341 |
| `ExtensionFunctionTarget` | `"~" \| "::"` | 342 |
| `LocalFunctionDecl` | `CaptureList? DefIntroducer Identifier FunctionRest` | 343 |
| `FunctionRest` | `TypeParameterList? ParameterList FunctionTail` | 345 |
| `EntryFunctionRest` | `ParameterList ReturnClause? ThrowsClause? EffectsClause? ContractClause* FunctionBody` | 346 |
| `FunctionTail` | `ReturnClause? ThrowsClause? EffectsClause? ContractClause* WhereClause? FunctionBody` | 347 |
| `TraitFunctionTail` | `ReturnClause? ThrowsClause? EffectsClause? ContractClause* WhereClause? (FunctionBody \| StatementBoundary)` | 348 |
| `FunctionBody` | `"=" FunctionBodyContent` | 350 |
| `FunctionBodyContent` | `CallableBlock \| ReturnShorthand \| ClauseFunctionBody` | 351 |
| `CallableBlock` | `"{" BlockPrologue? FunctionStaticActivation? BlockSequence "}"` | 356 |
| `FunctionStaticActivation` | `"scope" FunctionStaticRole Block` | 357 |
| `FunctionStaticRole` | `"#" "static"` | 358 |
| `ReturnShorthand` | `"return" Expr StatementBoundary` | 359 |
| `ClauseFunctionBody` | `"{{" LineBreakBoundary? MatchArmSequence "}}"` | 360 |
| `MemberFunctionDecl` | `MemberVisibility? DefIntroducer Identifier ClassDispatchMarker FunctionRest` | 362 |
| `TypeSideMemberFunctionDecl` | `MemberVisibility? "def" "::" Identifier FunctionRest` | 363 |
| `ConstructorDecl` | `MemberVisibility? "def" "!" Identifier ParameterList ConstructorSignatureTail? ConstructorDelegationClause? "=" Block` | 365 |
| `ConstructorSignatureTail` | `ThrowsClause EffectsClause? ContractClause* WhereClause? \| EffectsClause ContractClause* WhereClause? \| ContractClause+ WhereClause? \| WhereClause` | 367 |
| `ConstructorDelegationClause` | `":" ConstructorDelegationArm+` | 371 |
| `ConstructorDelegationArm` | `ConstructorDelegationTarget PositiveGuard?` | 372 |
| `ConstructorDelegationTarget` | `Identifier ArgumentList \| "super" "!" Identifier? ArgumentList` | 373 |
| `CleanupDecl` | `DefIntroducer "(" ")" ThrowsClause? EffectsClause? FunctionBody` | 376 |
| `ParameterList` | `"(" ParameterSequence? ")"` | 380 |
| `ParameterSequence` | `CommaParameterSequence \| LayoutParameterSequence` | 381 |
| `CommaParameterSequence` | `Parameter ("," Parameter)* ","?` | 382 |
| `LayoutParameterSequence` | `LineBreakBoundary Parameter (LineBreakBoundary Parameter)* LineBreakBoundary?` | 383 |
| `Parameter` | `StoredParameter \| ContextParameter \| WitnessParameter \| RepeatedParameter \| NamedRestParameter \| ValueParameter` | 385 |
| `ValueParameter` | `ParameterMode? ParameterPatternSlot TypeAnnotation` | 391 |
| `ParameterPatternSlot` | `Identifier` | 394 |
| `ParameterMode` | `"borrow" \| "mut" \| "move" \| "inout"` | 395 |
| `ContextParameter` | `"context" Identifier ":" TypeRef` | 396 |
| `WitnessParameter` | `"using" Identifier ":" "witness" TypeRef` | 397 |
| `RepeatedParameter` | `Identifier "..." TypeAnnotation` | 398 |
| `NamedRestParameter` | `Identifier "***" TypeAnnotation` | 399 |
| `StoredParameter` | `MemberVisibility? ("let" \| "var") Identifier TypeAnnotation?` | 403 |
| `ClassDecl` | `OrdinaryClassDecl \| DataClassDecl` | 407 |
| `OrdinaryClassDecl` | `TopLevelVisibility? ClassFlavor? ClassModifierSequence? "class" Identifier TypeParameterList? ParameterList? InheritanceClause? WhereClause? CleanupBudgetClause? ClassBody` | 408 |
| `DataClassDecl` | `TopLevelVisibility? "data" "class" Identifier TypeParameterList? ParameterList? InheritanceClause? WhereClause? CleanupBudgetClause? ClassBody?` | 411 |
| `ClassFlavor` | `"value" \| "resource"` | 413 |
| `ClassModifierSequence` | `"final" \| "open" \| "abstract" \| "sealed" \| "abstract" "sealed"` | 414 |
| `InheritanceClause` | `":" TypeRef` | 415 |
| `ClassBody` | `"{" MemberDecl* "}"` | 416 |
| `MemberDecl` | `FieldDecl \| MemberFunctionDecl \| ConstructorDecl \| CleanupDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| ForwardDecl` | 418 |
| `FieldDecl` | `MemberVisibility? ("let" \| "var") Identifier TypeAnnotation? Initializer? StatementBoundary` | 427 |
| `TypeSideFieldDecl` | `MemberVisibility? "let" "::" Identifier TypeAnnotation? Initializer? StatementBoundary` | 429 |
| `AccessorPropertyDecl` | `("let" \| "var") Identifier TypeAnnotation ":=" AccessorSpec` | 431 |
| `AccessorSpec` | `AccessorDecl \| "{" AccessorDecl+ "}"` | 432 |
| `AccessorDecl` | `MemberVisibility? "get" Block \| MemberVisibility? "set" "(" Identifier ")" Block` | 433 |
| `ForwardDecl` | `MemberVisibility? "forward" ForwardMemberSpec "to" Expr StatementBoundary` | 435 |
| `ForwardMemberSpec` | `Identifier \| "{" Identifier ("," Identifier)* ","? "}"` | 436 |
| `TraitDecl` | `TopLevelVisibility? "trait" Identifier TypeParameterList? SuperTraitClause? TraitBody?` | 440 |
| `SuperTraitClause` | `"requires" TraitReferenceList` | 441 |
| `TraitBody` | `"{" TraitItem* "}"` | 442 |
| `TraitItem` | `TraitMethodDecl \| AssociatedRequirementDecl \| LawDecl` | 443 |
| `TraitMethodDecl` | `MemberVisibility? DefIntroducer Identifier TraitWitnessMarker TypeParameterList? ParameterList TraitFunctionTail` | 445 |
| `AssociatedRequirementDecl` | `AssociatedTypeRequirementDecl \| AssociatedValueRequirementDecl \| AssociatedFunctionRequirementDecl` | 447 |
| `AssociatedTypeRequirementDecl` | `"type" Identifier AssociatedTypeConstraintList? StatementBoundary` | 450 |
| `AssociatedValueRequirementDecl` | `"let" "::" Identifier TypeAnnotation StatementBoundary` | 451 |
| `AssociatedFunctionRequirementDecl` | `"def" "::" Identifier ParameterList ReturnClause? ThrowsClause? EffectsClause? StatementBoundary` | 452 |
| `ConformanceDecl` | `TopLevelVisibility? "conformance" TypeRef "conforms" QualifiedTypeReference NameAliasClause? ConformanceViaClause? WhereClause? ConformanceBody` | 455 |
| `ConformanceViaClause` | `"via" QualifiedPath` | 457 |
| `ConformanceBody` | `"{" ConformanceItem* "}"` | 458 |
| `ConformanceMethodDecl` | `MemberVisibility? DefIntroducer Identifier TraitWitnessMarker FunctionRest` | 459 |
| `ConformanceItem` | `ConformanceMethodDecl \| TypeSideMemberFunctionDecl \| AssociatedRequirementBinding \| ExtensionDelegationDecl \| LawDecl` | 460 |
| `AssociatedRequirementBinding` | `"type" Identifier "=" TypeRef StatementBoundary \| "let" "::" Identifier "=" Expr StatementBoundary` | 465 |
| `ExtensionDelegationDecl` | `"delegate" Identifier "to" QualifiedExtensionSelector StatementBoundary` | 467 |
| `ExtensionSetDecl` | `TopLevelVisibility? "extension" TypeRef "as" Identifier ExtensionSetBody` | 471 |
| `ExtensionSetBody` | `"{" ExtensionSetItem* "}"` | 472 |
| `ExtensionSetItem` | `ExtensionSetFunctionDecl \| TypeSideMemberFunctionDecl` | 473 |
| `ExtensionSetFunctionDecl` | `MemberVisibility? "def" Identifier ParameterList? ReturnClause? ThrowsClause? EffectsClause? WhereClause? FunctionBody` | 474 |
| `ExtensionPackDecl` | `"extension" "pack" QualifiedPath ExtensionPackBody` | 476 |
| `ExtensionPackBody` | `"{" UseExportDecl* "}"` | 477 |
| `EnumDecl` | `TopLevelVisibility? "enum" EnumOrderRole? Identifier TypeParameterList? EnumBody` | 481 |
| `EnumOrderRole` | `"#" ("increasing" \| "decreasing")` | 482 |
| `EnumBody` | `"{" (EnumCommaCaseSequence \| EnumLayoutBody)? "}"` | 483 |
| `EnumCommaCaseSequence` | `EnumCaseCore ("," EnumCaseCore)+ ","?` | 484 |
| `EnumLayoutBody` | `EnumCaseDecl* EnumMemberDecl*` | 485 |
| `EnumCaseDecl` | `EnumCaseCore StatementBoundary?` | 486 |
| `EnumCaseCore` | `Identifier EnumCasePayload? EnumCaseDisplayMapping?` | 487 |
| `EnumCasePayload` | `"(" EnumCaseFieldList? ")"` | 488 |
| `EnumCaseFieldList` | `EnumCaseField ("," EnumCaseField)* ","?` | 489 |
| `EnumCaseField` | `Identifier TypeAnnotation \| TypeRef` | 490 |
| `EnumMemberDecl` | `MemberFunctionDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| EnumVariantSubsetAliasDecl` | 491 |
| `EnumCaseDisplayMapping` | `"~>" RestrictedEnumDisplayTemplate` | 496 |
| `RestrictedEnumDisplayTemplate` | `PLAIN_STRING_LITERAL \| MULTILINE_STRING_LITERAL \| InterpolatedString` | 497 |
| `EnumVariantSubsetAliasDecl` | `"+" "type" Identifier "=" EnumVariantSubsetRhs StatementBoundary?` | 500 |
| `EnumVariantSubsetRhs` | `Identifier ("\|" Identifier)*` | 502 |
| `SchemaDecl` | `TopLevelVisibility? "schema" Identifier TypeParameterList? SchemaBody` | 506 |
| `SchemaBody` | `"{" SchemaFieldSequence? "}"` | 507 |
| `SchemaFieldSequence` | `CommaSchemaFields \| LayoutSchemaFields` | 508 |
| `CommaSchemaFields` | `SchemaFieldDecl ("," SchemaFieldDecl)* ","?` | 509 |
| `LayoutSchemaFields` | `LineBreakBoundary LayoutSchemaFieldDecl (LineBreakBoundary LayoutSchemaFieldDecl)* LineBreakBoundary?` | 510 |
| `SchemaFieldDecl` | `Identifier TypeAnnotation Initializer? SchemaConstraint* StatementBoundary?` | 511 |
| `LayoutSchemaFieldDecl` | `Identifier TypeAnnotation Initializer? SchemaConstraint*` | 512 |
| `SchemaConstraint` | `"where" Expr` | 513 |
| `TypeAliasDecl` | `TopLevelVisibility? "type" Identifier TypeParameterList? "=" TypeAliasRhs StatementBoundary` | 515 |
| `TypeAliasRhs` | `TypeRef RefinementClause? \| StaticRangeType` | 516 |
| `StaticRangeType` | `StaticIntLiteral ".." StaticIntLiteral` | 517 |
| `TopLevelBindingDecl` | `TopLevelVisibility? ("let" \| "var") Identifier TypeAnnotation? "=" Expr StatementBoundary` | 519 |
| `NamedEffectCapabilityDecl` | `TopLevelVisibility? "capability" Identifier "for" EffectRow StatementBoundary` | 520 |
| `ActorDecl` | `TopLevelVisibility? "actor" MailboxClause? Identifier ActorBody` | 524 |
| `MailboxClause` | `HashTag "(" "capacity" ":" StaticIntLiteral ")"` | 525 |
| `ActorBody` | `"{" ActorItem* "}"` | 526 |
| `ActorItem` | `ActorOnDecl \| ActorRequestDecl \| MemberDecl` | 527 |
| `ActorOnDecl` | `MemberVisibility? "on" Identifier ParameterList? ThrowsClause? EffectsClause? FunctionBody` | 528 |
| `ActorRequestDecl` | `MemberVisibility? "request" Identifier ParameterList? ReturnClause ThrowsClause? EffectsClause? FunctionBody` | 529 |
| `ActorProtocolDecl` | `TopLevelVisibility? "protocol" Identifier ActorProtocolBody` | 531 |
| `ActorProtocolBody` | `"{" ActorProtocolItem* "}"` | 532 |
| `ActorProtocolItem` | `ActorProtocolSendRequirement \| ActorProtocolRequestRequirement` | 533 |
| `ActorProtocolSendRequirement` | `"send" Identifier ParameterList? ThrowsClause? EffectsClause? StatementBoundary` | 534 |
| `ActorProtocolRequestRequirement` | `"request" Identifier ParameterList? ReturnClause ThrowsClause? EffectsClause? StatementBoundary` | 535 |
| `TypestateResourceDecl` | `TopLevelVisibility? "typestate" Identifier TypeParameterList? TypestateBody` | 539 |
| `TypestateBody` | `"{" TypestateTransitionDecl* "}"` | 540 |
| `TypestateTransitionDecl` | `Identifier "->" Identifier FunctionBody?` | 541 |
| `UnitCatalogDecl` | `TopLevelVisibility? "unit" "catalog" Identifier UnitCatalogBody` | 543 |
| `UnitCatalogBody` | `"{" UnitCatalogEntry* "}"` | 544 |
| `UnitCatalogEntry` | `ExactRatioUnitConversionDecl \| Identifier "=" UnitExpr StatementBoundary` | 545 |
| `ExactRatioUnitConversionDecl` | `"unit" Identifier "equalsRatio" MeasureLiteralExpr "/" StaticIntLiteral StatementBoundary` | 546 |
| `ModuleInterfaceDecl` | `ModuleSignatureDecl \| OpaqueModuleFacadeDecl` | 548 |
| `ModuleSignatureDecl` | `TopLevelVisibility? "module" "signature" QualifiedPath ModuleInterfaceBody` | 549 |
| `OpaqueModuleFacadeDecl` | `TopLevelVisibility? "opaque" "module" QualifiedPath ModuleInterfaceBody` | 550 |
| `ModuleInterfaceBody` | `"{" ModuleInterfaceItem* "}"` | 551 |
| `ModuleInterfaceItem` | `ExportDecl \| UseExportDecl \| OpaqueModuleFacadeDecl` | 552 |
| `CleanupBudgetClause` | `"cleanup" "budget" "{" CleanupBudgetItem* "}"` | 556 |
| `CleanupBudgetItem` | `EffectsBudget \| ErrorsBudget` | 557 |
| `EffectsBudget` | `"effects" "{" IdentifierList? "}"` | 558 |
| `ErrorsBudget` | `"errors" TypeRef` | 559 |
| `BitfieldDecl` | `TopLevelVisibility? BitfieldIntroducer Identifier BitfieldBackingClause BitfieldOrderClause BitfieldBody` | 563 |
| `BitfieldIntroducer` | `"bitfield" HashTag?` | 565 |
| `BitfieldBackingClause` | `"backing" TypeRef` | 566 |
| `BitfieldOrderClause` | `"order" "::" "lsb0"` | 567 |
| `BitfieldBody` | `"{" BitfieldLayoutSection BitfieldMemberDecl* "}"` | 568 |
| `BitfieldLayoutSection` | `BitfieldSlotDecl+ \| FlagSlotDecl+` | 569 |
| `BitfieldSlotDecl` | `BitfieldNamedSlot StatementBoundary \| BitfieldReservedSlot StatementBoundary` | 570 |
| `FlagSlotDecl` | `FlagNamedSlot StatementBoundary \| BitfieldReservedSlot StatementBoundary` | 571 |
| `BitfieldNamedSlot` | `MemberVisibility? Identifier ":" StaticIntLiteral BitfieldDefault?` | 572 |
| `BitfieldReservedSlot` | `"_" ":" StaticIntLiteral` | 573 |
| `FlagNamedSlot` | `MemberVisibility? Identifier` | 574 |
| `BitfieldDefault` | `"=" Literal` | 575 |
| `BitfieldMemberDecl` | `MemberFunctionDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| LawDecl` | 576 |
| `TypeRef` | `PrattType` | 588 |
| `NonFunctionTypeRef` | `PrattNonFunctionType` | 589 |
| `TypePrimary` | `QualifiedTypeReference \| FacetType \| ParenTypeSyntax \| SharpShapeType \| ExistentialType \| OpaqueType \| TypeofType \| AssociatedProjection` | 592 |
| `TypePrefixParselet` | `OwnershipQualifier` | 600 |
| `TypePostfixParselet` | `"?"` | 601 |
| `TypeInfixOperator` | `"&" \| "\|"` | 602 |
| `QualifiedTypeReference` | `QualifiedPath TypeArgumentList?` | 604 |
| `FacetType` | `"Facet" "<" "borrow" "any" QualifiedTypeReference AssociatedTypeConstraintList? ">"` | 606 |
| `OwnershipQualifier` | `"owned" \| "borrowed" \| "mut" \| "inout"` | 607 |
| `ParenTypeSyntax` | `HashTag* "(" ParenTypeItemList? ")" FunctionTypeTail?` | 611 |
| `ParenTypeItemList` | `ParenTypeItem ("," ParenTypeItem)* ","?` | 612 |
| `ParenTypeItem` | `TypeRef \| TypeRef "..." \| TypeRef "***"` | 613 |
| `FunctionTypeTail` | `"->" NonFunctionTypeRef ThrowsClause? EffectsClause?` | 614 |
| `SharpShapeType` | `"#" StaticDimensionList "[" TypeRef "]"` | 616 |
| `StaticDimensionList` | `StaticIntLiteral ("," StaticIntLiteral)*` | 617 |
| `ExistentialType` | `"any" QualifiedTypeReference AssociatedTypeConstraintList?` | 619 |
| `OpaqueType` | `"some" QualifiedTypeReference AssociatedTypeConstraintList?` | 620 |
| `TypeofType` | `"typeof" TypeofStaticSampleOperand` | 621 |
| `AssociatedProjection` | `"<" TypeRef "as" QualifiedTypeReference ">" "::" Identifier` | 622 |
| `TypeofStaticSampleOperand` | `Literal \| ListLiteral \| StaticPrefixedCollectionSample \| NumericArrayLiteral \| MeasureLiteralExpr` | 625 |
| `StaticPrefixedCollectionSample` | `MapLiteral \| SetLiteral \| MutListLiteral` | 630 |
| `PrattType` | `TYPE_PRATT_ENTRY` | 633 |
| `PrattNonFunctionType` | `NON_FUNCTION_TYPE_PRATT_ENTRY` | 634 |
| `Pattern` | `OrPattern` | 642 |
| `OrPattern` | `AliasPattern ("\|" AliasPattern)*` | 643 |
| `AliasPattern` | `MovePattern ("as" Identifier)?` | 644 |
| `MovePattern` | `"move"? PatternPrimary` | 645 |
| `PatternPrimary` | `TypedBindingPattern \| Identifier \| RecordPattern \| ListPattern \| VariantPattern \| "_" \| UnitSyntax \| Literal \| ParenthesizedPattern` | 647 |
| `TypedBindingPattern` | `Identifier ":" TypeRef` | 657 |
| `ParenthesizedPattern` | `"(" Pattern ")"` | 658 |
| `BindingPattern` | `BindingOrPattern TypeAnnotation?` | 670 |
| `BindingOrPattern` | `BindingAliasPattern ("\|" BindingAliasPattern)*` | 671 |
| `BindingAliasPattern` | `BindingMovePattern ("as" Identifier)?` | 672 |
| `BindingMovePattern` | `"move"? BindingPatternPrimary` | 673 |
| `BindingPatternPrimary` | `Identifier \| RecordPattern \| ListPattern \| VariantPattern \| "_" \| UnitSyntax \| Literal \| ParenthesizedPattern` | 674 |
| `RecordPattern` | `"${" PatternFieldList? "}"` | 683 |
| `PatternFieldList` | `PatternField ("," PatternField)* ","?` | 684 |
| `PatternField` | `Identifier \| Identifier ":" Pattern` | 685 |
| `ListPattern` | `"[" (ListPatternPrefix ("," IgnoredListRest)? ","? \| IgnoredListRest ","?)? "]"` | 689 |
| `ListPatternPrefix` | `Pattern ("," Pattern)*` | 690 |
| `IgnoredListRest` | `".." "_"` | 691 |
| `VariantPattern` | `VariantQualifier Identifier VariantPatternPayload?` | 693 |
| `VariantQualifier` | `TypeRef "::" \| "::"` | 694 |
| `VariantPatternPayload` | `"(" PatternList? ")"` | 695 |
| `Stmt` | `ForLoop \| WhileLoop \| RepeatLoop \| AsyncForLoop \| TaskGroupStmt \| MatchStatement \| IfStmt \| LocalBindingStmt \| ControlTransferStmt \| TryStmt \| DeferStmt \| ScopedUseStmt \| ExprStmt \| ScopedImportStmt` | 703 |
| `ExprStmt` | `Expr StatementBoundary` | 718 |
| `Block` | `"{" BlockPrologue? BlockSequence "}"` | 720 |
| `BlockPrologue` | `(UseDecl \| ImportDecl)+` | 721 |
| `BlockSequence` | `BlockItem* BlockFinalItem?` | 722 |
| `BlockItem` | `LocalFunctionDecl \| Stmt` | 723 |
| `BlockFinalItem` | `ControlTransfer \| BindingCore \| Expr` | 726 |
| `ValueBody` | `SingleExpressionValueBody \| ExplicitRetValueBody` | 729 |
| `SingleExpressionValueBody` | `"{" Expr "}"` | 730 |
| `ExplicitRetValueBody` | `"{" BlockItem* RetTransfer "}"` | 731 |
| `RetTransfer` | `"ret" Expr? GuardClause?` | 732 |
| `BindingCore` | `("let" \| "var") BindingPattern "=" Expr` | 737 |
| `LocalBindingStmt` | `BindingCore StatementBoundary \| RightwardLocalBindingSurface \| LazyBindingStmt \| GuardedBindingStmt` | 738 |
| `LazyBindingStmt` | `"let" HashTag Identifier TypeAnnotation? "=" Expr StatementBoundary` | 739 |
| `GuardedBindingStmt` | `"let" BindingPattern "=" Expr "else" GuardedBindingFailure StatementBoundary?` | 740 |
| `GuardedBindingFailure` | `GuardedBindingExit \| Pattern "=>" GuardedBindingExit` | 742 |
| `GuardedBindingExit` | `GuardedReturnExit \| GuardedThrowExit \| GuardedBreakExit \| GuardedContinueExit` | 743 |
| `GuardedReturnExit` | `"return" Expr?` | 744 |
| `GuardedThrowExit` | `"throw" Expr` | 745 |
| `GuardedBreakExit` | `("break")+ Expr?` | 746 |
| `GuardedContinueExit` | `("break")* "continue"` | 747 |
| `ControlTransferStmt` | `ControlTransfer StatementBoundary` | 750 |
| `ControlTransfer` | `ReturnTransfer \| ThrowTransfer \| BreakTransfer \| ContinueTransfer \| YieldTransfer` | 751 |
| `ReturnTransfer` | `"return" Expr? GuardClause?` | 752 |
| `ThrowTransfer` | `"throw" Expr GuardClause?` | 753 |
| `BreakTransfer` | `("break")+ Expr? GuardClause?` | 754 |
| `ContinueTransfer` | `("break")* "continue" GuardClause?` | 755 |
| `YieldTransfer` | `"yield" Expr? (GuardClause \| YieldResponseBinding)?` | 756 |
| `YieldResponseBinding` | `"->" DollarLocalBinding` | 757 |
| `DollarLocalBinding` | `"$" Identifier TypeAnnotation? \| "$$" Identifier TypeAnnotation?` | 758 |
| `GuardClause` | `PositiveGuard \| NegativeGuard` | 760 |
| `PositiveGuard` | `"if" Expr` | 761 |
| `NegativeGuard` | `"!" "if" Expr` | 762 |
| `IfStmt` | `"if" PatternControlCondition Block ("else" (IfStmt \| Block))?` | 764 |
| `PatternControlCondition` | `Expr \| "let" Pattern "=" Expr` | 765 |
| `ForLoop` | `"for" ("let" Pattern \| Pattern) "in" Expr GuardClause? Block MatchStatement?` | 769 |
| `WhileLoop` | `"while" PatternControlCondition Block MatchStatement?` | 770 |
| `RepeatLoop` | `"repeat" Block "while" Expr MatchStatement?` | 771 |
| `AsyncForLoop` | `"for" "await" ("let" Pattern \| Pattern) "in" Expr GuardClause? Block` | 772 |
| `MatchStatement` | `"match" MatchCore` | 774 |
| `MatchCore` | `MatchSubjectSlot MatchBody` | 775 |
| `MatchSubjectSlot` | `MATCH_SUBJECT_BY_INPUT_SUPPLY_POLICY` | 776 |
| `MatchBody` | `"{" LineBreakBoundary? MatchArmSequence "}"` | 777 |
| `MatchArmSequence` | `MatchArm (MatchArmSeparator MatchArm)* MatchArmSeparator?` | 778 |
| `MatchArm` | `MatchHead GuardClause? "=>" MatchArmBodySlot` | 779 |
| `MatchHead` | `Pattern \| "otherwise"` | 780 |
| `MatchArmSeparator` | `MATCH_ARM_SEPARATOR_BY_CONTEXT` | 781 |
| `MatchArmBodySlot` | `MATCH_ARM_BODY_BY_CONTEXT` | 782 |
| `TryStmt` | `"try" Block (CatchClause+ FinallyClause? \| FinallyClause)` | 786 |
| `CatchClause` | `"catch" Pattern? Block` | 787 |
| `ValueCatchClause` | `"catch" Pattern? ValueBody` | 788 |
| `FinallyClause` | `"finally" Block` | 789 |
| `DeferStmt` | `"defer" DeferredCleanupInvocation StatementBoundary` | 791 |
| `DeferredCleanupInvocation` | `DeferredDirectCall \| DeferredMessageCall` | 794 |
| `DeferredDirectCall` | `DeferredReceiver ArgumentList` | 795 |
| `DeferredMessageCall` | `DeferredReceiver "~" MessageSelector TildeArgumentSequence?` | 796 |
| `DeferredReceiver` | `DeferredPrimary DeferTargetSuffix*` | 797 |
| `DeferredPrimary` | `Identifier \| QualifiedStaticExpr` | 798 |
| `DeferTargetSuffix` | `IndexSuffix \| MemberSuffix` | 799 |
| `RightwardLocalBindingSurface` | `Expr "->" DollarLocalBinding StatementBoundary` | 803 |
| `ScopedUseStmt` | `"use" ScopedPathList "in" Block` | 804 |
| `ScopedImportStmt` | `"import" ScopedPathList "in" Block` | 805 |
| `ScopedPathList` | `QualifiedPath ("," QualifiedPath)*` | 806 |
| `TaskGroupStmt` | `"task" "group" Identifier? Block` | 807 |
| `Expr` | `PrattExpr` | 815 |
| `PredicateExpr` | `PrattPredicateExpr` | 816 |
| `SliceIndexExpr` | `PrattSliceIndexExpr` | 817 |
| `ExpressionPrefixParselet` | `"+" \| "-" \| "not" \| "~~" \| "move" \| "borrow" \| "&" \| "await"` | 823 |
| `ExpressionPostfixParselet` | `CallSuffix \| TildeCallLed \| TupleOrdinalSuffix \| IndexSuffix \| MemberSuffix \| NumericArrayTransposeSuffix \| ConstructorCallSuffix \| NamedConstructorCallSuffix \| PrototypeDerivationSuffix \| CastSuffix` | 825 |
| `PrimaryExpr` | `Literal \| Identifier \| ImplicitAtExpr \| ParenExprSyntax \| ListLiteral \| BoundedListLiteral \| ComprehensionExpr \| MaterializationBody \| TypedMaterializationExpr \| MapLiteral \| SetLiteral \| MutListLiteral \| MapComprehensionExpr \| SetComprehensionExpr \| NumericArrayLiteral \| MeasureLiteralExpr \| QualifiedStaticExpr \| ExpectedVariantExpr \| AtControlExpr \| MatchExpr \| ClosureExpr \| GeneratorExpr \| SpawnExpr \| StructuredTaskScope \| UnsafeBlockExpr \| FacetExpr` | 836 |
| `ParenExprSyntax` | `"(" ParenExprContent? ")"` | 864 |
| `ParenExprContent` | `Expr ParenExprTail?` | 865 |
| `ParenExprTail` | `"," \| "," Expr ("," Expr)* ","?` | 866 |
| `ImplicitAtExpr` | `"@"` | 867 |
| `ExpectedVariantExpr` | `"::" Identifier` | 868 |
| `CallSuffix` | `ArgumentList TrailingClosureGroup? \| AtomicCallArgument TrailingClosureGroup` | 872 |
| `ArgumentList` | `"(" ")" \| "(" CommaArgumentSequence ")" \| "(" LayoutArgumentSequence ")"` | 875 |
| `CommaArgumentSequence` | `Argument ("," Argument)* ","?` | 878 |
| `LayoutArgumentSequence` | `LineBreakBoundary NamedLayoutArgument LineBreakBoundary NamedLayoutArgument (LineBreakBoundary NamedLayoutArgument)* LineBreakBoundary?` | 880 |
| `NamedLayoutArgument` | `NamedArgument \| NamedUnfoldArgument` | 882 |
| `Argument` | `ContextArgument \| WitnessArgument \| NamedArgument \| PositionalUnfoldArgument \| NamedUnfoldArgument \| Expr` | 883 |
| `ContextArgument` | `"context" Expr` | 889 |
| `WitnessArgument` | `"using" WitnessArgumentValue` | 890 |
| `WitnessArgumentValue` | `Identifier \| ConformanceEvidenceSelector \| NamedConformanceEvidenceSelector` | 891 |
| `NamedArgument` | `Identifier ":" Expr` | 892 |
| `PositionalUnfoldArgument` | `"*" Expr` | 893 |
| `NamedUnfoldArgument` | `"**" Expr` | 894 |
| `AtomicCallArgument` | `Literal \| Identifier \| QualifiedStaticExpr \| ExpectedVariantExpr` | 895 |
| `TrailingClosureGroup` | `TrailingClosureArgument+` | 899 |
| `TrailingClosureArgument` | `ClosureExpr \| Identifier ":" ClosureExpr` | 900 |
| `IndexSuffix` | `"[" SliceAxisList "]"` | 904 |
| `SliceAxisList` | `SliceAxis (";" SliceAxis)*` | 905 |
| `SliceAxis` | `SliceRange \| SliceIndexExpr \| AxisWildcard` | 906 |
| `SliceRange` | `SliceBound (".." \| "..<") SliceBound` | 909 |
| `SliceBound` | `SliceIndexExpr \| "^" \| "$" \| "^" OffsetExpr \| "$" OffsetExpr` | 910 |
| `OffsetExpr` | `("+" \| "-") NumericLiteral` | 911 |
| `AxisWildcard` | `"*"` | 912 |
| `TupleOrdinalSuffix` | `"." StaticIntLiteral` | 914 |
| `MemberSuffix` | `"." Identifier \| "." "\\\\" NAME_TOKEN` | 915 |
| `TildeCallLed` | `TildeCallToken MessageSelector TildeArgumentSequence? TrailingClosureGroup?` | 921 |
| `TildeCallToken` | `"~" \| ":~"` | 923 |
| `MessageSelector` | `Identifier \| QualifiedMessageSelector` | 924 |
| `QualifiedMessageSelector` | `TypeRef "::" Identifier ("::" Identifier)?` | 925 |
| `QualifiedExtensionSelector` | `TypeRef "::" Identifier "::" Identifier` | 926 |
| `TildeArgumentSequence` | `TildeArgument ("," TildeArgument)*` | 927 |
| `TildeArgument` | `ContextArgument \| WitnessArgument \| NamedArgument \| PositionalUnfoldArgument \| NamedUnfoldArgument \| Expr` | 928 |
| `NumericArrayTransposeSuffix` | `"^"` | 935 |
| `ConstructorCallSuffix` | `"!" ArgumentList` | 936 |
| `NamedConstructorCallSuffix` | `"!" Identifier ArgumentList` | 937 |
| `PrototypeDerivationSuffix` | `("!" \| "!!") DerivationBody` | 938 |
| `DerivationBody` | `"{" MaterializationEntryList? "}"` | 939 |
| `CastSuffix` | `"as" "?" TypeRef \| "as" "!" TypeRef` | 941 |
| `QualifiedStaticExpr` | `StaticQualifier "::" Identifier \| TraitQualifiedAssociatedSelector` | 943 |
| `StaticQualifier` | `QualifiedTypeReference \| AssociatedProjection` | 945 |
| `TraitQualifiedAssociatedSelector` | `"<" TypeRef "as" QualifiedTypeReference ">" "::" Identifier` | 946 |
| `AtControlExpr` | `AtIfExpr \| AtTryExpr \| AtScopeExpr` | 952 |
| `AtIfExpr` | `"@" "if" Expr ValueBody ("else" ValueBody)?` | 954 |
| `AtTryExpr` | `"@" "try" ValueBody (ValueCatchClause+ FinallyClause? \| FinallyClause)` | 955 |
| `AtScopeExpr` | `"@" "scope" ScopeModifier* ValueBody` | 956 |
| `ScopeModifier` | `"isolated" \| "cancellable" \| "shielded"` | 957 |
| `MatchExpr` | `"@" "match" MatchCore` | 959 |
| `ClosureExpr` | `CaptureList? HashTag* "{" ClosureContent "}"` | 963 |
| `ClosureContent` | `ExplicitLambdaContent \| LambdaBody?` | 964 |
| `ExplicitLambdaContent` | `LambdaParameterList? "=>" LambdaBody` | 965 |
| `LambdaParameterList` | `LambdaParameter ("," LambdaParameter)* ","?` | 966 |
| `LambdaParameter` | `ParameterMode? Identifier TypeAnnotation?` | 967 |
| `LambdaBody` | `Expr \| LineBreakBoundary LambdaBlockContent` | 968 |
| `LambdaBlockContent` | `BlockItem* LambdaFinalItem?` | 969 |
| `LambdaFinalItem` | `RetTransfer \| Expr` | 970 |
| `CaptureList` | `"[" CaptureItemList? "]"` | 972 |
| `CaptureItemList` | `CaptureItem ("," CaptureItem)* ","?` | 973 |
| `CaptureItem` | `("let" \| "var") Identifier "=" Expr \| CaptureMode Identifier \| Identifier` | 974 |
| `CaptureMode` | `"borrow" \| "inout" \| "move" \| "clone" \| "deep" \| "copy" \| "once"` | 977 |
| `GeneratorExpr` | `CaptureList? GeneratorCore` | 982 |
| `GeneratorCore` | `"@" "for" Pattern "in" Expr Block \| "@" "while" Expr Block \| "@" "repeat" Block "while" Expr` | 983 |
| `SpawnExpr` | `"spawn" TaskBody` | 987 |
| `TaskBody` | `"{" "=>" TaskBodySequence "}" \| "async" "{" "=>" TaskBodySequence "}"` | 988 |
| `TaskBodySequence` | `LineBreakBoundary? BlockSequence` | 990 |
| `StructuredTaskScope` | `"task" "scope" Block` | 991 |
| `UnsafeBlockExpr` | `"unsafe" Block` | 992 |
| `FacetExpr` | `"facet" "[" "borrow" Expr "as" QualifiedTypeReference AssociatedTypeConstraintList? "]"` | 995 |
| `ConformanceEvidenceSelector` | `"conformance" "(" TypeRef "conforms" QualifiedTypeReference ")"` | 997 |
| `NamedConformanceEvidenceSelector` | `ConformanceEvidenceSelector "::" Identifier` | 998 |
| `PrattExpr` | `EXPRESSION_PRATT_ENTRY` | 1001 |
| `PrattPredicateExpr` | `PREDICATE_PRATT_ENTRY` | 1002 |
| `PrattSliceIndexExpr` | `SLICE_INDEX_PRATT_ENTRY` | 1003 |
| `Literal` | `BoolLiteral \| NumericLiteral \| ImaginaryLiteralExpr \| RationalLiteralExpr \| StringLiteralExpr \| CharLiteralExpr \| BytesLiteral` | 1011 |
| `BoolLiteral` | `"true" \| "false"` | 1018 |
| `NumericLiteral` | `NUMERIC_LITERAL` | 1019 |
| `ImaginaryLiteralExpr` | `IMAGINARY_LITERAL` | 1020 |
| `RationalLiteralExpr` | `RATIONAL_LITERAL` | 1021 |
| `CharLiteralExpr` | `CHAR_LITERAL` | 1022 |
| `BytesLiteral` | `BYTES_LITERAL` | 1023 |
| `StringLiteralExpr` | `PLAIN_STRING_LITERAL \| RAW_STRING_LITERAL \| MULTILINE_STRING_LITERAL \| InterpolatedString` | 1026 |
| `InterpolatedString` | `STRING_START InterpolatedStringPart* STRING_END` | 1027 |
| `InterpolatedStringPart` | `STRING_TEXT \| STRING_ESCAPE \| InterpolationExpr \| InterpolationPath` | 1028 |
| `InterpolationExpr` | `INTERPOLATION_OPEN Expr InterpolationFormat? INTERPOLATION_CLOSE` | 1032 |
| `InterpolationFormat` | `":" INTERPOLATION_FORMAT_TEXT` | 1033 |
| `InterpolationPath` | `"$" InterpolationPathRoot InterpolationPathSelector* INTERPOLATION_BOUNDARY?` | 1038 |
| `InterpolationPathRoot` | `Identifier \| "@"` | 1039 |
| `InterpolationPathSelector` | `"." Identifier \| "." StaticIntLiteral \| "[" InterpolationIndex "]"` | 1040 |
| `InterpolationIndex` | `StaticIntLiteral \| Identifier` | 1043 |
| `ListLiteral` | `"[" ExpressionList? "]"` | 1048 |
| `BoundedListLiteral` | `"[" StaticIntLiteral ".." StaticIntLiteral ":" ExpressionList? "]"` | 1049 |
| `ComprehensionExpr` | `"[" Expr ComprehensionClause+ "]"` | 1051 |
| `TypedMaterializationExpr` | `TypeRef MaterializationBody` | 1054 |
| `MaterializationBody` | `"${" MaterializationEntryList? "}"` | 1055 |
| `MaterializationEntryList` | `MaterializationEntry (MaterializationSeparator MaterializationEntry)* MaterializationSeparator?` | 1056 |
| `MaterializationEntry` | `Identifier \| Identifier ":" Expr \| StringLiteralExpr ":" Expr \| NamedUnfoldArgument` | 1057 |
| `MaterializationSeparator` | `"," LineBreakBoundary? \| LineBreakBoundary` | 1061 |
| `MapLiteral` | `"#" "map" "{" MapEntryList? "}"` | 1064 |
| `MapEntryList` | `MapEntry (MaterializationSeparator MapEntry)* MaterializationSeparator?` | 1065 |
| `MapEntry` | `Expr ":" Expr \| NamedUnfoldArgument` | 1066 |
| `SetLiteral` | `"#" "set" "{" ExpressionList? "}"` | 1067 |
| `MutListLiteral` | `"#" "mut" "[" ExpressionList? "]"` | 1068 |
| `MapComprehensionExpr` | `"#" "map" "{" MapEntry ComprehensionClause+ "}"` | 1069 |
| `SetComprehensionExpr` | `"#" "set" "{" Expr ComprehensionClause+ "}"` | 1070 |
| `ComprehensionClause` | `ForClause \| PositiveGuard \| IfLetClause \| UnfoldClause` | 1072 |
| `ForClause` | `"for" Pattern "in" Expr` | 1073 |
| `IfLetClause` | `"if" "let" Pattern "=" Expr` | 1074 |
| `UnfoldClause` | `"for" "..." Pattern "in" Expr` | 1075 |
| `NumericArrayLiteral` | `ShapeInferredArrayLiteral \| ShapeInferredColumnVectorLiteral \| ExactShapeArrayLiteral` | 1078 |
| `ShapeInferredArrayLiteral` | `"#" "[" ExpressionList? "]"` | 1081 |
| `ShapeInferredColumnVectorLiteral` | `"#" "[" Expr (";" Expr)+ "]"` | 1082 |
| `ExactShapeArrayLiteral` | `"#" StaticDimensionList "[" ArrayInitializer? "]"` | 1083 |
| `ArrayInitializer` | `ShapedRepeatInitializer \| ShapedGeneratorInitializer \| ShapedElementSequence` | 1084 |
| `ShapedRepeatInitializer` | `"repeat" ":" Expr` | 1087 |
| `ShapedGeneratorInitializer` | `"generate" ":" Expr` | 1088 |
| `ShapedElementSequence` | `Expr (ShapedElementSeparator Expr)* ShapedElementSeparator?` | 1089 |
| `ShapedElementSeparator` | `"," \| ShapedAxisBoundary` | 1090 |
| `ShapedAxisBoundary` | `";" ";"*` | 1091 |
| `MeasureLiteralExpr` | `NumericLiteral "[" UnitExpr "]"` | 1094 |
| `UnitExpr` | `PrattUnitExpr` | 1095 |
| `UnitPrimary` | `Identifier \| QualifiedPath \| "(" UnitExpr ")"` | 1096 |
| `UnitPostfixParselet` | `"^" SignedStaticInt` | 1097 |
| `UnitInfixOperator` | `"*" \| "/"` | 1098 |
| `PrattUnitExpr` | `UNIT_PRATT_ENTRY` | 1099 |

## `PREVIEW` 프로파일 — 13개

| 문법 production | 정확한 EBNF 오른쪽 항 | 원천 줄 |
|---|---|---:|
| `DeeplusPreview` | `PreviewLibrarySourceFile \| PreviewExecutableSourceFile \| PreviewScriptSourceFile` | 1107 |
| `PreviewLibrarySourceFile` | `PreviewGate ModuleDecl? PreviewLibraryItem*` | 1108 |
| `PreviewExecutableSourceFile` | `PreviewGate ModuleDecl? PreviewExecutableItem*` | 1109 |
| `PreviewScriptSourceFile` | `Shebang? PreviewGate ModuleDecl? PreviewScriptItem*` | 1110 |
| `PreviewLibraryItem` | `LibrarySourceItem \| PreviewFfiDecl` | 1112 |
| `PreviewExecutableItem` | `ExecutableSourceItem \| PreviewFfiDecl` | 1113 |
| `PreviewScriptItem` | `ScriptSourceItem \| PreviewFfiDecl` | 1114 |
| `PreviewGate` | `"#" "preview" "(" PreviewFeatureList ")" LineBreakBoundary` | 1116 |
| `PreviewFeatureList` | `Identifier ("," Identifier)*` | 1117 |
| `PreviewFfiDecl` | `PreviewFfiFunctionDecl \| PreviewFfiBlockDecl` | 1120 |
| `PreviewFfiFunctionDecl` | `"extern" "#" "C" "def" "#" "unsafe" Identifier ParameterList ReturnClause? ThrowsClause? EffectsClause? StatementBoundary` | 1121 |
| `PreviewFfiBlockDecl` | `"extern" "c" "(" PLAIN_STRING_LITERAL ")" "{" PreviewFfiBlockMember* "}"` | 1123 |
| `PreviewFfiBlockMember` | `"unsafe" "def" Identifier ParameterList ReturnClause? ThrowsClause? EffectsClause? StatementBoundary` | 1125 |

## `RECOVERY` 프로파일 — 15개

| 문법 production | 정확한 EBNF 오른쪽 항 | 원천 줄 |
|---|---|---:|
| `RecoverySyntax` | `RecoveryGenericEntryFunctionDecl \| RecoveryFacetPackExpr \| RecoveryFacetType \| RecoveryNullLiteral \| RecoveryEmptyIndexSuffix \| RecoveryCustomOperatorDeclaration \| RecoveryNamedRestDoubleStar \| RecoveryFunctionTypeNamedRestDoubleStar \| RecoveryLazyBindingAt \| RecoveryUnitMiddleDot \| RecoveryQuarantineScope` | 1134 |
| `RecoveryNullLiteral` | `"null"` | 1148 |
| `RecoveryEmptyIndexSuffix` | `"[" "]"` | 1152 |
| `RecoveryCustomOperatorDeclaration` | `"operator" RecoveryOperatorSymbol ("precedence" StaticIntLiteral)? StatementBoundary` | 1153 |
| `RecoveryOperatorSymbol` | `ScannerRecoveryOperatorSymbol` | 1158 |
| `RecoveryGenericEntryFunctionDecl` | `"def" "#" "entry" Identifier TypeParameterList ParameterList ReturnClause? ThrowsClause? EffectsClause? ContractClause* FunctionBody \| "def" "#" "entry" "#" "async" Identifier TypeParameterList ParameterList ReturnClause? ThrowsClause? EffectsClause? ContractClause* FunctionBody` | 1161 |
| `RecoveryFacetPackExpr` | `"facet" "[" ("inout" \| "move") Expr "as" QualifiedTypeReference AssociatedTypeConstraintList? "]"` | 1167 |
| `RecoveryFacetType` | `"Facet" "<" ("inout" \| "move") "any" QualifiedTypeReference AssociatedTypeConstraintList? ">"` | 1169 |
| `RecoveryNamedRestDoubleStar` | `Identifier "**" TypeAnnotation` | 1174 |
| `RecoveryFunctionTypeNamedRestDoubleStar` | `TypeRef "**"` | 1175 |
| `RecoveryLazyBindingAt` | `"let" "@" "lazy" Identifier TypeAnnotation? "=" Expr StatementBoundary` | 1178 |
| `RecoveryUnitMiddleDot` | `UnitPrimary "·" UnitPrimary` | 1181 |
| `RecoveryQuarantineScope` | `"@" "scope" "#" ("dynamic" \| "unsafe") Block QuarantineExport?` | 1184 |
| `QuarantineExport` | `"->" "$" Identifier TypeAnnotation \| "->" "$" "(" QuarantineExportField ("," QuarantineExportField)* ")"` | 1185 |
| `QuarantineExportField` | `Identifier TypeAnnotation` | 1187 |
