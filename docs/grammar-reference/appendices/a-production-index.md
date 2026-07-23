<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# 부록 A — 정확한 문법 production 참조

권위 원천은 `spec/grammar/deeplus.ebnf`입니다. 이름만 나열하지 않고 모든 production의 정확한 오른쪽 항을 주석을 제외한 정규화된 EBNF로 한 번씩 투영합니다. 줄 번호는 원천을 찾아가기 위한 보조 정보이며 이 부록 자체가 별도 문법 권위는 아닙니다.

## `LEXICAL` 프로파일 — 89개

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
| `INTEGER_LITERAL` | `BinaryInteger IntegerSuffix? \| OctalInteger IntegerSuffix? \| HexInteger IntegerSuffix? \| DECIMAL_INTEGER IntegerSuffix?` | 66 |
| `FLOAT_LITERAL` | `DecimalFraction ExponentPart? FloatSuffix? \| DECIMAL_INTEGER ExponentPart FloatSuffix? \| DECIMAL_INTEGER FloatSuffix` | 71 |
| `BinaryInteger` | `("0b" \| "0B") BinaryDigits` | 74 |
| `OctalInteger` | `("0o" \| "0O") OctalDigits` | 75 |
| `HexInteger` | `("0x" \| "0X") HexDigits` | 76 |
| `DECIMAL_INTEGER` | `DecimalDigits` | 77 |
| `DecimalFraction` | `DecimalDigits "." DecimalDigits` | 78 |
| `ExponentPart` | `("e" \| "E") ("+" \| "-")? DecimalDigits` | 79 |
| `IntegerSuffix` | `"i8" \| "i16" \| "i32" \| "i64" \| "i128" \| "isize" \| "u8" \| "u16" \| "u32" \| "u64" \| "u128" \| "usize"` | 80 |
| `FloatSuffix` | `"f32" \| "f64"` | 82 |
| `BinaryDigits` | `BinaryDigit ("_"? BinaryDigit)*` | 83 |
| `OctalDigits` | `OctalDigit ("_"? OctalDigit)*` | 84 |
| `DecimalDigits` | `DecimalDigit ("_"? DecimalDigit)*` | 85 |
| `HexDigits` | `HexDigit ("_"? HexDigit)*` | 86 |
| `BinaryDigit` | `"0" \| "1"` | 87 |
| `OctalDigit` | `"0" \| "1" \| "2" \| "3" \| "4" \| "5" \| "6" \| "7"` | 88 |
| `DecimalDigit` | `"0" \| "1" \| "2" \| "3" \| "4" \| "5" \| "6" \| "7" \| "8" \| "9"` | 89 |
| `HexDigit` | `DecimalDigit \| "a" \| "b" \| "c" \| "d" \| "e" \| "f" \| "A" \| "B" \| "C" \| "D" \| "E" \| "F"` | 90 |
| `CHAR_LITERAL` | `"'" CharScalar "'"` | 93 |
| `CharScalar` | `DirectCharScalar \| SimpleCharEscape \| UnicodeScalarEscape \| NamedUnicodeEscape` | 94 |
| `SimpleCharEscape` | `"\\\\0" \| "\\\\n" \| "\\\\r" \| "\\\\t" \| "\\\\'" \| "\\\\\\\\"` | 95 |
| `UnicodeScalarEscape` | `"\\\\u{" HexScalarDigits "}"` | 96 |
| `NamedUnicodeEscape` | `"\\\\N{" UnicodeName "}"` | 97 |
| `HexScalarDigits` | `HexDigit HexDigit? HexDigit? HexDigit? HexDigit? HexDigit?` | 98 |
| `PLAIN_STRING_LITERAL` | `ScannerPlainStringLiteral` | 101 |
| `STRING_START` | `ScannerInterpolatedStringStart` | 102 |
| `STRING_TEXT` | `ScannerInterpolatedStringText` | 103 |
| `STRING_ESCAPE` | `ScannerStringEscape` | 104 |
| `INTERPOLATION_BOUNDARY` | `ScannerInterpolationBoundary` | 105 |
| `INTERPOLATION_OPEN` | `ScannerInterpolationOpen` | 106 |
| `INTERPOLATION_CLOSE` | `ScannerInterpolationClose` | 107 |
| `INTERPOLATION_FORMAT_TEXT` | `ScannerInterpolationFormatText` | 108 |
| `STRING_END` | `ScannerInterpolatedStringEnd` | 109 |
| `RAW_STRING_LITERAL` | `ScannerRawStringLiteral` | 112 |
| `MULTILINE_STRING_LITERAL` | `ScannerMultilineStringLiteral` | 113 |
| `BYTES_LITERAL` | `ScannerBytesLiteral` | 114 |
| `PATH_SEP` | `"::"` | 117 |
| `FAT_ARROW` | `"=>"` | 118 |
| `ARROW` | `"->"` | 119 |
| `DOT_DOT` | `".."` | 120 |
| `DOT_DOT_LT` | `"..<"` | 121 |
| `DOT_DOT_GT` | `"..>"` | 122 |
| `ELLIPSIS` | `"..."` | 123 |
| `TRIPLE_STAR` | `"***"` | 124 |
| `DOUBLE_STAR` | `"**"` | 125 |
| `STAR_PLUS` | `"*+"` | 126 |
| `STAR_DOT` | `"*."` | 127 |
| `AMP_AMP` | `"&&"` | 128 |
| `PIPE_PIPE` | `"\|\|"` | 129 |
| `CARET_CARET` | `"^^"` | 130 |
| `QUESTION_COLON` | `"?:"` | 131 |
| `DOUBLE_DOLLAR` | `"$$"` | 132 |
| `EQ_EQ` | `"=="` | 133 |
| `BANG_EQ` | `"!="` | 134 |
| `LT_EQ` | `"<="` | 135 |
| `GT_EQ` | `">="` | 136 |
| `PLUS_EQ` | `"+="` | 137 |
| `MINUS_EQ` | `"-="` | 138 |
| `STAR_EQ` | `"*="` | 139 |
| `SLASH_EQ` | `"/="` | 140 |
| `PERCENT_EQ` | `"%="` | 141 |
| `TILDE_TILDE` | `"~~"` | 142 |
| `COLON_EQ` | `":="` | 143 |
| `BANG_BANG` | `"!!"` | 144 |
| `DOUBLE_L_BRACE` | `"{{"` | 145 |
| `DOUBLE_R_BRACE` | `"}}"` | 146 |
| `DOLLAR_L_BRACE` | `"${"` | 147 |
| `Trivia` | `HorizontalSpace \| LineTerminator \| LineComment \| NestedBlockComment \| DocLineComment \| DocBlockComment \| WordComment` | 152 |
| `EOF_TOKEN` | `EOF` | 155 |
| `NAME_TOKEN` | `ScannerEscapedNameToken` | 157 |
| `EOF` | `ScannerEndOfInput` | 158 |

## `STABLE` 프로파일 — 443개

| 문법 production | 정확한 EBNF 오른쪽 항 | 원천 줄 |
|---|---|---:|
| `Identifier` | `IDENTIFIER` | 166 |
| `QualifiedPath` | `Identifier ("::" Identifier)*` | 167 |
| `TopLevelVisibility` | `"public" \| "private" \| "common"` | 169 |
| `MemberVisibility` | `"+" \| "-" \| "#"` | 178 |
| `ClassDispatchMarker` | `"." \| "+" \| "*." \| "*+"` | 179 |
| `TraitWitnessMarker` | `"." \| "+" \| "*." \| "*+"` | 180 |
| `VarianceMarker` | `"out" \| "in"` | 181 |
| `AnnotationAttachment` | `Annotation+` | 183 |
| `Annotation` | `"@" Identifier ArgumentList? LineBreakBoundary` | 184 |
| `RoleWord` | `Identifier \| HARD_KEYWORD` | 189 |
| `HashTag` | `"#" RoleWord` | 190 |
| `TypeParameterList` | `"<" TypeParameter ("," TypeParameter)* ","? ">"` | 193 |
| `TypeParameter` | `VarianceMarker? Identifier TypeParameterKindAnnotation?` | 194 |
| `TypeParameterKindAnnotation` | `":" TypeParameterKind` | 195 |
| `TypeParameterKind` | `"type" \| "StaticInt" \| "EffectRow" \| "ErrorSet"` | 196 |
| `TypeArgumentList` | `"<" TypeArgument ("," TypeArgument)* ","? ">"` | 198 |
| `TypeArgument` | `TypeRef \| StaticIntLiteral \| ErrorTypeArgument` | 199 |
| `ErrorTypeArgument` | `"error" TypeRef` | 200 |
| `TraitReferenceList` | `QualifiedTypeReference ("," QualifiedTypeReference)*` | 202 |
| `AssociatedTypeConstraintList` | `"where" AssociatedTypeConstraint ("," AssociatedTypeConstraint)*` | 203 |
| `AssociatedTypeConstraint` | `Identifier "==" TypeRef \| Identifier "conforms" QualifiedTypeReference` | 204 |
| `WhereClause` | `"where" WherePredicate ("," WherePredicate)*` | 207 |
| `WherePredicate` | `TypeRef "conforms" QualifiedTypeReference \| TypeRef "==" TypeRef \| RowPredicate` | 208 |
| `RowPredicate` | `Identifier "<=" EffectRow` | 211 |
| `EffectRow` | `EffectRowTerm ("\|" EffectRowTerm)*` | 213 |
| `EffectRowTerm` | `Identifier \| QualifiedTypeReference \| EffectSetLiteral` | 214 |
| `ErrorSet` | `ErrorSetTerm ("\|" ErrorSetTerm)*` | 215 |
| `ErrorSetTerm` | `Identifier \| QualifiedTypeReference` | 216 |
| `EffectSetLiteral` | `"{" IdentifierList? "}"` | 217 |
| `TypeAnnotation` | `":" TypeRef RefinementClause?` | 219 |
| `RefinementClause` | `"where" PredicateExpr` | 220 |
| `Initializer` | `"=" Expr` | 221 |
| `NameAliasClause` | `"as" Identifier` | 222 |
| `ReturnClause` | `"->" NonFunctionTypeRef` | 225 |
| `ThrowsClause` | `"throws" ErrorSet` | 226 |
| `EffectsClause` | `"effects" EffectRow` | 227 |
| `ContractClause` | `RequiresClause \| EnsuresClause` | 228 |
| `RequiresClause` | `"requires" PredicateExpr` | 229 |
| `EnsuresClause` | `"ensures" PredicateExpr` | 230 |
| `LineBreakBoundary` | `LINE_BREAK_IN_TRIVIA` | 235 |
| `StatementBoundary` | `STATEMENT_BOUNDARY_BY_CONTEXT` | 236 |
| `IdentifierList` | `Identifier ("," Identifier)* ","?` | 238 |
| `ExpressionList` | `Expr ("," Expr)* ","?` | 239 |
| `PatternList` | `Pattern ("," Pattern)* ","?` | 240 |
| `StaticIntLiteral` | `DECIMAL_INTEGER` | 242 |
| `UnitSyntax` | `"(" ")"` | 245 |
| `SignedStaticInt` | `("+" \| "-")? StaticIntLiteral` | 246 |
| `LawDecl` | `"law" Identifier LawBody? StatementBoundary` | 248 |
| `LawBody` | `"{" LawBodyItem* "}"` | 251 |
| `LawBodyItem` | `LawAssertion StatementBoundary` | 252 |
| `LawAssertion` | `("requires" \| "ensures" \| "invariant")? PredicateExpr` | 253 |
| `Deeplus` | `LibrarySourceFile \| ExecutableSourceFile \| ScriptSourceFile` | 261 |
| `LibrarySourceFile` | `ModuleDecl? LibrarySourceItem*` | 263 |
| `ExecutableSourceFile` | `ModuleDecl? ExecutableSourceItem*` | 264 |
| `ScriptSourceFile` | `Shebang? ModuleDecl? ScriptSourceItem*` | 265 |
| `LibrarySourceItem` | `AnnotationAttachment LibraryAnnotatableDecl \| ImportOrUseDecl \| TopLevelDecl` | 267 |
| `ExecutableSourceItem` | `AnnotationAttachment ExecutableAnnotatableDecl \| ImportOrUseDecl \| NonBindingTopLevelDecl \| EntryFunctionDecl` | 270 |
| `ScriptSourceItem` | `AnnotationAttachment ScriptAnnotatableDecl \| ImportOrUseDecl \| NonBindingTopLevelDecl \| Stmt` | 274 |
| `LibraryAnnotatableDecl` | `ImportOrUseDecl \| TopLevelDecl` | 279 |
| `ExecutableAnnotatableDecl` | `ImportOrUseDecl \| NonBindingTopLevelDecl \| EntryFunctionDecl` | 280 |
| `ScriptAnnotatableDecl` | `ImportOrUseDecl \| NonBindingTopLevelDecl` | 281 |
| `ModuleDecl` | `"module" QualifiedPath StatementBoundary` | 283 |
| `ImportOrUseDecl` | `ImportDecl \| UseDecl \| UseExportDecl` | 285 |
| `ImportDecl` | `"import" QualifiedPath ImportTail? StatementBoundary` | 286 |
| `ImportTail` | `ImportAlias \| ImportSelection` | 287 |
| `ImportAlias` | `NameAliasClause` | 288 |
| `ImportSelection` | `"::" "{" IdentifierList "}"` | 289 |
| `UseDecl` | `"use" QualifiedPath StatementBoundary` | 290 |
| `UseExportDecl` | `"use" "export" QualifiedPath StatementBoundary` | 291 |
| `ExportDecl` | `"export" ExportItem StatementBoundary?` | 294 |
| `ExportItem` | `ExportableModuleFunctionDecl \| TypeDecl \| Identifier` | 295 |
| `ExportableModuleFunctionDecl` | `TopLevelVisibility? "def" Identifier FunctionRest` | 296 |
| `TopLevelDecl` | `NonBindingTopLevelDecl \| TopLevelBindingDecl` | 304 |
| `NonBindingTopLevelDecl` | `TypeDecl \| ModuleFunctionDecl \| ExtensionFunctionDecl \| ActorDecl \| ActorProtocolDecl \| TypestateResourceDecl \| NamedEffectCapabilityDecl \| ExtensionSetDecl \| ExtensionPackDecl \| UnitCatalogDecl \| ModuleInterfaceDecl \| ConformanceDecl \| SchemaDecl \| BitfieldDecl` | 305 |
| `TypeDecl` | `ClassDecl \| TraitDecl \| EnumDecl \| TypeAliasDecl` | 320 |
| `DefIntroducer` | `"def" HashTag*` | 324 |
| `ModuleFunctionDecl` | `TopLevelVisibility? DefIntroducer Identifier FunctionRest` | 326 |
| `EntryFunctionDecl` | `DefIntroducer Identifier EntryFunctionRest` | 327 |
| `ExtensionFunctionDecl` | `TopLevelVisibility? DefIntroducer TypeRef ExtensionFunctionTarget Identifier FunctionRest` | 328 |
| `ExtensionFunctionTarget` | `"~" \| "::"` | 329 |
| `LocalFunctionDecl` | `CaptureList? DefIntroducer Identifier FunctionRest` | 330 |
| `FunctionRest` | `TypeParameterList? ParameterList FunctionTail` | 332 |
| `EntryFunctionRest` | `ParameterList ReturnClause? ThrowsClause? EffectsClause? ContractClause* FunctionBody` | 333 |
| `FunctionTail` | `ReturnClause? ThrowsClause? EffectsClause? ContractClause* WhereClause? FunctionBody` | 334 |
| `TraitFunctionTail` | `ReturnClause? ThrowsClause? EffectsClause? ContractClause* WhereClause? (FunctionBody \| StatementBoundary)` | 335 |
| `FunctionBody` | `"=" FunctionBodyContent` | 337 |
| `FunctionBodyContent` | `Block \| ReturnShorthand \| ClauseFunctionBody` | 338 |
| `ReturnShorthand` | `"return" Expr StatementBoundary` | 339 |
| `ClauseFunctionBody` | `"{{" LineBreakBoundary? MatchArmSequence "}}"` | 340 |
| `MemberFunctionDecl` | `MemberVisibility? DefIntroducer Identifier ClassDispatchMarker FunctionRest` | 342 |
| `TypeSideMemberFunctionDecl` | `MemberVisibility? "def" "::" Identifier FunctionRest` | 343 |
| `ConstructorDecl` | `MemberVisibility? "def" "!" Identifier ParameterList ConstructorSignatureTail? ConstructorDelegationClause? "=" Block` | 345 |
| `ConstructorSignatureTail` | `ThrowsClause EffectsClause? ContractClause* WhereClause? \| EffectsClause ContractClause* WhereClause? \| ContractClause+ WhereClause? \| WhereClause` | 347 |
| `ConstructorDelegationClause` | `":" ConstructorDelegationArm+` | 351 |
| `ConstructorDelegationArm` | `ConstructorDelegationTarget PositiveGuard?` | 352 |
| `ConstructorDelegationTarget` | `Identifier ArgumentList \| "super" "!" Identifier? ArgumentList` | 353 |
| `CleanupDecl` | `DefIntroducer "(" ")" ThrowsClause? EffectsClause? FunctionBody` | 356 |
| `ParameterList` | `"(" ParameterSequence? ")"` | 360 |
| `ParameterSequence` | `CommaParameterSequence \| LayoutParameterSequence` | 361 |
| `CommaParameterSequence` | `Parameter ("," Parameter)* ","?` | 362 |
| `LayoutParameterSequence` | `LineBreakBoundary Parameter (LineBreakBoundary Parameter)* LineBreakBoundary?` | 363 |
| `Parameter` | `StoredParameter \| ContextParameter \| WitnessParameter \| RepeatedParameter \| NamedRestParameter \| ValueParameter` | 365 |
| `ValueParameter` | `ParameterMode? ParameterPatternSlot TypeAnnotation` | 371 |
| `ParameterPatternSlot` | `Identifier` | 374 |
| `ParameterMode` | `"borrow" \| "mut" \| "move" \| "inout"` | 375 |
| `ContextParameter` | `"context" Identifier ":" TypeRef` | 376 |
| `WitnessParameter` | `"using" Identifier ":" "witness" TypeRef` | 377 |
| `RepeatedParameter` | `Identifier "..." TypeAnnotation` | 378 |
| `NamedRestParameter` | `Identifier "***" TypeAnnotation` | 379 |
| `StoredParameter` | `MemberVisibility? ("let" \| "var") Identifier TypeAnnotation?` | 383 |
| `ClassDecl` | `OrdinaryClassDecl \| DataClassDecl` | 387 |
| `OrdinaryClassDecl` | `TopLevelVisibility? ClassFlavor? ClassModifierSequence? "class" Identifier TypeParameterList? ParameterList? InheritanceClause? WhereClause? CleanupBudgetClause? ClassBody` | 388 |
| `DataClassDecl` | `TopLevelVisibility? "data" "class" Identifier TypeParameterList? ParameterList? InheritanceClause? WhereClause? CleanupBudgetClause? ClassBody?` | 391 |
| `ClassFlavor` | `"value" \| "resource"` | 393 |
| `ClassModifierSequence` | `"final" \| "open" \| "abstract" \| "sealed" \| "abstract" "sealed"` | 394 |
| `InheritanceClause` | `":" TypeRef` | 395 |
| `ClassBody` | `"{" MemberDecl* "}"` | 396 |
| `MemberDecl` | `FieldDecl \| MemberFunctionDecl \| ConstructorDecl \| CleanupDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| ForwardDecl` | 398 |
| `FieldDecl` | `MemberVisibility? ("let" \| "var") Identifier TypeAnnotation? Initializer? StatementBoundary` | 407 |
| `TypeSideFieldDecl` | `MemberVisibility? "let" "::" Identifier TypeAnnotation? Initializer? StatementBoundary` | 409 |
| `AccessorPropertyDecl` | `("let" \| "var") Identifier TypeAnnotation ":=" AccessorSpec` | 411 |
| `AccessorSpec` | `AccessorDecl \| "{" AccessorDecl+ "}"` | 412 |
| `AccessorDecl` | `MemberVisibility? "get" Block \| MemberVisibility? "set" "(" Identifier ")" Block` | 413 |
| `ForwardDecl` | `MemberVisibility? "forward" ForwardMemberSpec "to" Expr StatementBoundary` | 415 |
| `ForwardMemberSpec` | `Identifier \| "{" Identifier ("," Identifier)* ","? "}"` | 416 |
| `TraitDecl` | `TopLevelVisibility? "trait" Identifier TypeParameterList? SuperTraitClause? TraitBody?` | 420 |
| `SuperTraitClause` | `"requires" TraitReferenceList` | 421 |
| `TraitBody` | `"{" TraitItem* "}"` | 422 |
| `TraitItem` | `TraitMethodDecl \| AssociatedRequirementDecl \| LawDecl` | 423 |
| `TraitMethodDecl` | `MemberVisibility? DefIntroducer Identifier TraitWitnessMarker TypeParameterList? ParameterList TraitFunctionTail` | 425 |
| `AssociatedRequirementDecl` | `AssociatedTypeRequirementDecl \| AssociatedValueRequirementDecl \| AssociatedFunctionRequirementDecl` | 427 |
| `AssociatedTypeRequirementDecl` | `"type" Identifier AssociatedTypeConstraintList? StatementBoundary` | 430 |
| `AssociatedValueRequirementDecl` | `"let" "::" Identifier TypeAnnotation StatementBoundary` | 431 |
| `AssociatedFunctionRequirementDecl` | `"def" "::" Identifier ParameterList ReturnClause? ThrowsClause? EffectsClause? StatementBoundary` | 432 |
| `ConformanceDecl` | `TopLevelVisibility? "conformance" TypeRef "conforms" QualifiedTypeReference NameAliasClause? ConformanceViaClause? WhereClause? ConformanceBody` | 435 |
| `ConformanceViaClause` | `"via" QualifiedPath` | 437 |
| `ConformanceBody` | `"{" ConformanceItem* "}"` | 438 |
| `ConformanceMethodDecl` | `MemberVisibility? DefIntroducer Identifier TraitWitnessMarker FunctionRest` | 439 |
| `ConformanceItem` | `ConformanceMethodDecl \| TypeSideMemberFunctionDecl \| AssociatedRequirementBinding \| ExtensionDelegationDecl \| LawDecl` | 440 |
| `AssociatedRequirementBinding` | `"type" Identifier "=" TypeRef StatementBoundary \| "let" "::" Identifier "=" Expr StatementBoundary` | 445 |
| `ExtensionDelegationDecl` | `"delegate" Identifier "to" QualifiedExtensionSelector StatementBoundary` | 447 |
| `ExtensionSetDecl` | `TopLevelVisibility? "extension" TypeRef "as" Identifier ExtensionSetBody` | 451 |
| `ExtensionSetBody` | `"{" ExtensionSetItem* "}"` | 452 |
| `ExtensionSetItem` | `ExtensionSetFunctionDecl \| TypeSideMemberFunctionDecl` | 453 |
| `ExtensionSetFunctionDecl` | `MemberVisibility? "def" Identifier ParameterList? ReturnClause? ThrowsClause? EffectsClause? WhereClause? FunctionBody` | 454 |
| `ExtensionPackDecl` | `"extension" "pack" QualifiedPath ExtensionPackBody` | 456 |
| `ExtensionPackBody` | `"{" UseExportDecl* "}"` | 457 |
| `EnumDecl` | `TopLevelVisibility? "enum" Identifier TypeParameterList? EnumBody` | 461 |
| `EnumBody` | `"{" (EnumCommaCaseSequence \| EnumLayoutBody)? "}"` | 462 |
| `EnumCommaCaseSequence` | `EnumCaseCore ("," EnumCaseCore)+ ","?` | 463 |
| `EnumLayoutBody` | `EnumCaseDecl* EnumMemberDecl*` | 464 |
| `EnumCaseDecl` | `EnumCaseCore StatementBoundary?` | 465 |
| `EnumCaseCore` | `Identifier EnumCasePayload?` | 466 |
| `EnumCasePayload` | `"(" EnumCaseFieldList? ")"` | 467 |
| `EnumCaseFieldList` | `EnumCaseField ("," EnumCaseField)* ","?` | 468 |
| `EnumCaseField` | `Identifier TypeAnnotation \| TypeRef` | 469 |
| `EnumMemberDecl` | `MemberFunctionDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl` | 470 |
| `SchemaDecl` | `TopLevelVisibility? "schema" Identifier TypeParameterList? SchemaBody` | 477 |
| `SchemaBody` | `"{" SchemaFieldSequence? "}"` | 478 |
| `SchemaFieldSequence` | `CommaSchemaFields \| LayoutSchemaFields` | 479 |
| `CommaSchemaFields` | `SchemaFieldDecl ("," SchemaFieldDecl)* ","?` | 480 |
| `LayoutSchemaFields` | `LineBreakBoundary LayoutSchemaFieldDecl (LineBreakBoundary LayoutSchemaFieldDecl)* LineBreakBoundary?` | 481 |
| `SchemaFieldDecl` | `Identifier TypeAnnotation Initializer? SchemaConstraint* StatementBoundary?` | 482 |
| `LayoutSchemaFieldDecl` | `Identifier TypeAnnotation Initializer? SchemaConstraint*` | 483 |
| `SchemaConstraint` | `"where" Expr` | 484 |
| `TypeAliasDecl` | `TopLevelVisibility? "type" Identifier TypeParameterList? "=" TypeAliasRhs StatementBoundary` | 486 |
| `TypeAliasRhs` | `TypeRef RefinementClause? \| StaticRangeType` | 487 |
| `StaticRangeType` | `StaticIntLiteral ".." StaticIntLiteral` | 488 |
| `TopLevelBindingDecl` | `TopLevelVisibility? ("let" \| "var") Identifier TypeAnnotation? "=" Expr StatementBoundary` | 490 |
| `NamedEffectCapabilityDecl` | `TopLevelVisibility? "capability" Identifier "for" EffectRow StatementBoundary` | 491 |
| `ActorDecl` | `TopLevelVisibility? "actor" MailboxClause? Identifier ActorBody` | 495 |
| `MailboxClause` | `HashTag "(" "capacity" ":" StaticIntLiteral ")"` | 496 |
| `ActorBody` | `"{" ActorItem* "}"` | 497 |
| `ActorItem` | `ActorOnDecl \| ActorRequestDecl \| MemberDecl` | 498 |
| `ActorOnDecl` | `MemberVisibility? "on" Identifier ParameterList? ThrowsClause? EffectsClause? FunctionBody` | 499 |
| `ActorRequestDecl` | `MemberVisibility? "request" Identifier ParameterList? ReturnClause ThrowsClause? EffectsClause? FunctionBody` | 500 |
| `ActorProtocolDecl` | `TopLevelVisibility? "protocol" Identifier ActorProtocolBody` | 502 |
| `ActorProtocolBody` | `"{" ActorProtocolItem* "}"` | 503 |
| `ActorProtocolItem` | `ActorProtocolSendRequirement \| ActorProtocolRequestRequirement` | 504 |
| `ActorProtocolSendRequirement` | `"send" Identifier ParameterList? ThrowsClause? EffectsClause? StatementBoundary` | 505 |
| `ActorProtocolRequestRequirement` | `"request" Identifier ParameterList? ReturnClause ThrowsClause? EffectsClause? StatementBoundary` | 506 |
| `TypestateResourceDecl` | `TopLevelVisibility? "typestate" Identifier TypeParameterList? TypestateBody` | 510 |
| `TypestateBody` | `"{" TypestateTransitionDecl* "}"` | 511 |
| `TypestateTransitionDecl` | `Identifier "->" Identifier FunctionBody?` | 512 |
| `UnitCatalogDecl` | `TopLevelVisibility? "unit" "catalog" Identifier UnitCatalogBody` | 514 |
| `UnitCatalogBody` | `"{" UnitCatalogEntry* "}"` | 515 |
| `UnitCatalogEntry` | `ExactRatioUnitConversionDecl \| Identifier "=" UnitExpr StatementBoundary` | 516 |
| `ExactRatioUnitConversionDecl` | `"unit" Identifier "equalsRatio" MeasureLiteralExpr "/" StaticIntLiteral StatementBoundary` | 517 |
| `ModuleInterfaceDecl` | `ModuleSignatureDecl \| OpaqueModuleFacadeDecl` | 519 |
| `ModuleSignatureDecl` | `TopLevelVisibility? "module" "signature" QualifiedPath ModuleInterfaceBody` | 520 |
| `OpaqueModuleFacadeDecl` | `TopLevelVisibility? "opaque" "module" QualifiedPath ModuleInterfaceBody` | 521 |
| `ModuleInterfaceBody` | `"{" ModuleInterfaceItem* "}"` | 522 |
| `ModuleInterfaceItem` | `ExportDecl \| UseExportDecl \| OpaqueModuleFacadeDecl` | 523 |
| `CleanupBudgetClause` | `"cleanup" "budget" "{" CleanupBudgetItem* "}"` | 527 |
| `CleanupBudgetItem` | `EffectsBudget \| ErrorsBudget` | 528 |
| `EffectsBudget` | `"effects" "{" IdentifierList? "}"` | 529 |
| `ErrorsBudget` | `"errors" TypeRef` | 530 |
| `BitfieldDecl` | `TopLevelVisibility? BitfieldIntroducer Identifier BitfieldBackingClause BitfieldOrderClause BitfieldBody` | 534 |
| `BitfieldIntroducer` | `"bitfield" HashTag?` | 536 |
| `BitfieldBackingClause` | `"backing" TypeRef` | 537 |
| `BitfieldOrderClause` | `"order" "::" "lsb0"` | 538 |
| `BitfieldBody` | `"{" BitfieldLayoutSection BitfieldMemberDecl* "}"` | 539 |
| `BitfieldLayoutSection` | `BitfieldSlotDecl+ \| FlagSlotDecl+` | 540 |
| `BitfieldSlotDecl` | `BitfieldNamedSlot StatementBoundary \| BitfieldReservedSlot StatementBoundary` | 541 |
| `FlagSlotDecl` | `FlagNamedSlot StatementBoundary \| BitfieldReservedSlot StatementBoundary` | 542 |
| `BitfieldNamedSlot` | `MemberVisibility? Identifier ":" StaticIntLiteral BitfieldDefault?` | 543 |
| `BitfieldReservedSlot` | `"_" ":" StaticIntLiteral` | 544 |
| `FlagNamedSlot` | `MemberVisibility? Identifier` | 545 |
| `BitfieldDefault` | `"=" Literal` | 546 |
| `BitfieldMemberDecl` | `MemberFunctionDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| LawDecl` | 547 |
| `TypeRef` | `PrattType` | 559 |
| `NonFunctionTypeRef` | `PrattNonFunctionType` | 560 |
| `TypePrimary` | `QualifiedTypeReference \| FacetType \| ParenTypeSyntax \| SharpShapeType \| ExistentialType \| OpaqueType \| TypeofType \| AssociatedProjection` | 563 |
| `TypePrefixParselet` | `OwnershipQualifier` | 571 |
| `TypePostfixParselet` | `"?"` | 572 |
| `TypeInfixOperator` | `"&" \| "\|"` | 573 |
| `QualifiedTypeReference` | `QualifiedPath TypeArgumentList?` | 575 |
| `FacetType` | `"Facet" "<" "borrow" "any" QualifiedTypeReference AssociatedTypeConstraintList? ">"` | 577 |
| `OwnershipQualifier` | `"owned" \| "borrowed" \| "mut" \| "inout"` | 578 |
| `ParenTypeSyntax` | `HashTag* "(" ParenTypeItemList? ")" FunctionTypeTail?` | 582 |
| `ParenTypeItemList` | `ParenTypeItem ("," ParenTypeItem)* ","?` | 583 |
| `ParenTypeItem` | `TypeRef \| TypeRef "..." \| TypeRef "***"` | 584 |
| `FunctionTypeTail` | `"->" NonFunctionTypeRef ThrowsClause? EffectsClause?` | 585 |
| `SharpShapeType` | `"#" StaticDimensionList "[" TypeRef "]"` | 587 |
| `StaticDimensionList` | `StaticIntLiteral ("," StaticIntLiteral)*` | 588 |
| `ExistentialType` | `"any" QualifiedTypeReference AssociatedTypeConstraintList?` | 590 |
| `OpaqueType` | `"some" QualifiedTypeReference AssociatedTypeConstraintList?` | 591 |
| `TypeofType` | `"typeof" TypeofStaticSampleOperand` | 592 |
| `AssociatedProjection` | `"<" TypeRef "as" QualifiedTypeReference ">" "::" Identifier` | 593 |
| `TypeofStaticSampleOperand` | `Literal \| ListLiteral \| StaticPrefixedCollectionSample \| NumericArrayLiteral \| MeasureLiteralExpr` | 596 |
| `StaticPrefixedCollectionSample` | `MapLiteral \| SetLiteral \| MutListLiteral` | 601 |
| `PrattType` | `TYPE_PRATT_ENTRY` | 604 |
| `PrattNonFunctionType` | `NON_FUNCTION_TYPE_PRATT_ENTRY` | 605 |
| `Pattern` | `OrPattern` | 613 |
| `OrPattern` | `AliasPattern ("\|" AliasPattern)*` | 614 |
| `AliasPattern` | `MovePattern ("as" Identifier)?` | 615 |
| `MovePattern` | `"move"? PatternPrimary` | 616 |
| `PatternPrimary` | `TypedBindingPattern \| Identifier \| RecordPattern \| ListPattern \| VariantPattern \| "_" \| UnitSyntax \| Literal \| ParenthesizedPattern` | 618 |
| `TypedBindingPattern` | `Identifier ":" TypeRef` | 628 |
| `ParenthesizedPattern` | `"(" Pattern ")"` | 629 |
| `BindingPattern` | `BindingOrPattern TypeAnnotation?` | 641 |
| `BindingOrPattern` | `BindingAliasPattern ("\|" BindingAliasPattern)*` | 642 |
| `BindingAliasPattern` | `BindingMovePattern ("as" Identifier)?` | 643 |
| `BindingMovePattern` | `"move"? BindingPatternPrimary` | 644 |
| `BindingPatternPrimary` | `Identifier \| RecordPattern \| ListPattern \| VariantPattern \| "_" \| UnitSyntax \| Literal \| ParenthesizedPattern` | 645 |
| `RecordPattern` | `"${" PatternFieldList? "}"` | 654 |
| `PatternFieldList` | `PatternField ("," PatternField)* ","?` | 655 |
| `PatternField` | `Identifier \| Identifier ":" Pattern` | 656 |
| `ListPattern` | `"[" (ListPatternPrefix ("," IgnoredListRest)? ","? \| IgnoredListRest ","?)? "]"` | 660 |
| `ListPatternPrefix` | `Pattern ("," Pattern)*` | 661 |
| `IgnoredListRest` | `".." "_"` | 662 |
| `VariantPattern` | `VariantQualifier Identifier VariantPatternPayload?` | 664 |
| `VariantQualifier` | `TypeRef "::" \| "::"` | 665 |
| `VariantPatternPayload` | `"(" PatternList? ")"` | 666 |
| `Stmt` | `ForLoop \| WhileLoop \| RepeatLoop \| AsyncForLoop \| TaskGroupStmt \| MatchStatement \| IfStmt \| LocalBindingStmt \| ControlTransferStmt \| TryStmt \| DeferStmt \| ScopedUseStmt \| ExprStmt \| ScopedImportStmt` | 674 |
| `ExprStmt` | `Expr StatementBoundary` | 689 |
| `Block` | `"{" BlockPrologue? BlockSequence "}"` | 691 |
| `BlockPrologue` | `(UseDecl \| ImportDecl)+` | 692 |
| `BlockSequence` | `BlockItem* BlockFinalItem?` | 693 |
| `BlockItem` | `LocalFunctionDecl \| Stmt` | 694 |
| `BlockFinalItem` | `ControlTransfer \| BindingCore \| Expr` | 697 |
| `ValueBody` | `SingleExpressionValueBody \| ExplicitRetValueBody` | 700 |
| `SingleExpressionValueBody` | `"{" Expr "}"` | 701 |
| `ExplicitRetValueBody` | `"{" BlockItem* RetTransfer "}"` | 702 |
| `RetTransfer` | `"ret" Expr? GuardClause?` | 703 |
| `BindingCore` | `("let" \| "var") BindingPattern "=" Expr` | 708 |
| `LocalBindingStmt` | `BindingCore StatementBoundary \| RightwardLocalBindingSurface \| LazyBindingStmt \| GuardedBindingStmt` | 709 |
| `LazyBindingStmt` | `"let" HashTag Identifier TypeAnnotation? "=" Expr StatementBoundary` | 710 |
| `GuardedBindingStmt` | `"let" BindingPattern "=" Expr "else" GuardedBindingFailure StatementBoundary?` | 711 |
| `GuardedBindingFailure` | `GuardedBindingExit \| Pattern "=>" GuardedBindingExit` | 713 |
| `GuardedBindingExit` | `GuardedReturnExit \| GuardedThrowExit \| GuardedBreakExit \| GuardedContinueExit` | 714 |
| `GuardedReturnExit` | `"return" Expr?` | 715 |
| `GuardedThrowExit` | `"throw" Expr` | 716 |
| `GuardedBreakExit` | `("break")+ Expr?` | 717 |
| `GuardedContinueExit` | `("break")* "continue"` | 718 |
| `ControlTransferStmt` | `ControlTransfer StatementBoundary` | 721 |
| `ControlTransfer` | `ReturnTransfer \| ThrowTransfer \| BreakTransfer \| ContinueTransfer \| YieldTransfer` | 722 |
| `ReturnTransfer` | `"return" Expr? GuardClause?` | 723 |
| `ThrowTransfer` | `"throw" Expr GuardClause?` | 724 |
| `BreakTransfer` | `("break")+ Expr? GuardClause?` | 725 |
| `ContinueTransfer` | `("break")* "continue" GuardClause?` | 726 |
| `YieldTransfer` | `"yield" Expr? (GuardClause \| YieldResponseBinding)?` | 727 |
| `YieldResponseBinding` | `"->" DollarLocalBinding` | 728 |
| `DollarLocalBinding` | `"$" Identifier TypeAnnotation? \| "$$" Identifier TypeAnnotation?` | 729 |
| `GuardClause` | `PositiveGuard \| NegativeGuard` | 731 |
| `PositiveGuard` | `"if" Expr` | 732 |
| `NegativeGuard` | `"!" "if" Expr` | 733 |
| `IfStmt` | `"if" PatternControlCondition Block ("else" (IfStmt \| Block))?` | 735 |
| `PatternControlCondition` | `Expr \| "let" Pattern "=" Expr` | 736 |
| `ForLoop` | `"for" ("let" Pattern \| Pattern) "in" Expr GuardClause? Block MatchStatement?` | 740 |
| `WhileLoop` | `"while" PatternControlCondition Block MatchStatement?` | 741 |
| `RepeatLoop` | `"repeat" Block "while" Expr MatchStatement?` | 742 |
| `AsyncForLoop` | `"for" "await" ("let" Pattern \| Pattern) "in" Expr GuardClause? Block` | 743 |
| `MatchStatement` | `"match" MatchCore` | 745 |
| `MatchCore` | `MatchSubjectSlot MatchBody` | 746 |
| `MatchSubjectSlot` | `MATCH_SUBJECT_BY_INPUT_SUPPLY_POLICY` | 747 |
| `MatchBody` | `"{" LineBreakBoundary? MatchArmSequence "}"` | 748 |
| `MatchArmSequence` | `MatchArm (MatchArmSeparator MatchArm)* MatchArmSeparator?` | 749 |
| `MatchArm` | `MatchHead GuardClause? "=>" MatchArmBodySlot` | 750 |
| `MatchHead` | `Pattern \| "otherwise"` | 751 |
| `MatchArmSeparator` | `MATCH_ARM_SEPARATOR_BY_CONTEXT` | 752 |
| `MatchArmBodySlot` | `MATCH_ARM_BODY_BY_CONTEXT` | 753 |
| `TryStmt` | `"try" Block (CatchClause+ FinallyClause? \| FinallyClause)` | 757 |
| `CatchClause` | `"catch" Pattern? Block` | 758 |
| `ValueCatchClause` | `"catch" Pattern? ValueBody` | 759 |
| `FinallyClause` | `"finally" Block` | 760 |
| `DeferStmt` | `"defer" DeferredCleanupInvocation StatementBoundary` | 762 |
| `DeferredCleanupInvocation` | `DeferredDirectCall \| DeferredMessageCall` | 765 |
| `DeferredDirectCall` | `DeferredReceiver ArgumentList` | 766 |
| `DeferredMessageCall` | `DeferredReceiver "~" MessageSelector MessageArguments?` | 767 |
| `DeferredReceiver` | `DeferredPrimary DeferTargetSuffix*` | 768 |
| `DeferredPrimary` | `Identifier \| QualifiedStaticExpr` | 769 |
| `DeferTargetSuffix` | `IndexSuffix \| MemberSuffix` | 770 |
| `RightwardLocalBindingSurface` | `Expr "->" DollarLocalBinding StatementBoundary` | 774 |
| `ScopedUseStmt` | `"use" ScopedPathList "in" Block` | 775 |
| `ScopedImportStmt` | `"import" ScopedPathList "in" Block` | 776 |
| `ScopedPathList` | `QualifiedPath ("," QualifiedPath)*` | 777 |
| `TaskGroupStmt` | `"task" "group" Identifier? Block` | 778 |
| `Expr` | `PrattExpr` | 786 |
| `PredicateExpr` | `PrattPredicateExpr` | 787 |
| `SliceIndexExpr` | `PrattSliceIndexExpr` | 788 |
| `ExpressionPrefixParselet` | `"+" \| "-" \| "not" \| "~~" \| "move" \| "borrow" \| "&" \| "await"` | 790 |
| `ExpressionPostfixParselet` | `CallSuffix \| TupleOrdinalSuffix \| IndexSuffix \| MemberSuffix \| MessageSuffix \| NumericArrayTransposeSuffix \| ConstructorCallSuffix \| NamedConstructorCallSuffix \| PrototypeDerivationSuffix \| CastSuffix` | 792 |
| `PrimaryExpr` | `Literal \| Identifier \| ImplicitAtExpr \| ParenExprSyntax \| ListLiteral \| BoundedListLiteral \| ComprehensionExpr \| MaterializationBody \| TypedMaterializationExpr \| MapLiteral \| SetLiteral \| MutListLiteral \| MapComprehensionExpr \| SetComprehensionExpr \| NumericArrayLiteral \| MeasureLiteralExpr \| QualifiedStaticExpr \| ExpectedVariantExpr \| AtControlExpr \| MatchExpr \| ClosureExpr \| GeneratorExpr \| SpawnExpr \| StructuredTaskScope \| UnsafeBlockExpr \| FacetExpr` | 803 |
| `ParenExprSyntax` | `"(" ParenExprContent? ")"` | 831 |
| `ParenExprContent` | `Expr ParenExprTail?` | 832 |
| `ParenExprTail` | `"," \| "," Expr ("," Expr)* ","?` | 833 |
| `ImplicitAtExpr` | `"@"` | 834 |
| `ExpectedVariantExpr` | `"::" Identifier` | 835 |
| `CallSuffix` | `ArgumentList ClosureExpr? \| AtomicCallArgument ClosureExpr` | 839 |
| `ArgumentList` | `"(" ")" \| "(" CommaArgumentSequence ")" \| "(" LayoutArgumentSequence ")"` | 842 |
| `CommaArgumentSequence` | `Argument ("," Argument)* ","?` | 845 |
| `LayoutArgumentSequence` | `LineBreakBoundary NamedLayoutArgument LineBreakBoundary NamedLayoutArgument (LineBreakBoundary NamedLayoutArgument)* LineBreakBoundary?` | 847 |
| `NamedLayoutArgument` | `NamedArgument \| NamedUnfoldArgument` | 849 |
| `Argument` | `ContextArgument \| WitnessArgument \| NamedArgument \| PositionalUnfoldArgument \| NamedUnfoldArgument \| Expr` | 850 |
| `ContextArgument` | `"context" Expr` | 856 |
| `WitnessArgument` | `"using" WitnessArgumentValue` | 857 |
| `WitnessArgumentValue` | `Identifier \| ConformanceEvidenceSelector \| NamedConformanceEvidenceSelector` | 858 |
| `NamedArgument` | `Identifier ":" Expr` | 859 |
| `PositionalUnfoldArgument` | `"*" Expr` | 860 |
| `NamedUnfoldArgument` | `"**" Expr` | 861 |
| `AtomicCallArgument` | `Literal \| Identifier \| QualifiedStaticExpr \| ExpectedVariantExpr` | 862 |
| `IndexSuffix` | `"[" SliceAxisList "]"` | 866 |
| `SliceAxisList` | `SliceAxis (";" SliceAxis)*` | 867 |
| `SliceAxis` | `SliceRange \| SliceIndexExpr \| AxisWildcard` | 868 |
| `SliceRange` | `SliceBound (".." \| "..<") SliceBound` | 871 |
| `SliceBound` | `SliceIndexExpr \| "^" \| "$" \| "^" OffsetExpr \| "$" OffsetExpr` | 872 |
| `OffsetExpr` | `("+" \| "-") NumericLiteral` | 873 |
| `AxisWildcard` | `"*"` | 874 |
| `TupleOrdinalSuffix` | `"." StaticIntLiteral` | 876 |
| `MemberSuffix` | `"." Identifier \| "." "\\\\" NAME_TOKEN` | 877 |
| `MessageSuffix` | `"~" MessageSelector MessageArguments? ClosureExpr?` | 878 |
| `MessageSelector` | `Identifier \| QualifiedExtensionSelector` | 879 |
| `QualifiedExtensionSelector` | `TypeRef "::" Identifier "::" Identifier` | 880 |
| `MessageArguments` | `ArgumentList \| AtomicCallArgument` | 881 |
| `NumericArrayTransposeSuffix` | `"^"` | 883 |
| `ConstructorCallSuffix` | `"!" ArgumentList` | 884 |
| `NamedConstructorCallSuffix` | `"!" Identifier ArgumentList` | 885 |
| `PrototypeDerivationSuffix` | `("!" \| "!!") DerivationBody` | 886 |
| `DerivationBody` | `"{" MaterializationEntryList? "}"` | 887 |
| `CastSuffix` | `"as" "?" TypeRef \| "as" "!" TypeRef` | 889 |
| `QualifiedStaticExpr` | `StaticQualifier "::" Identifier` | 891 |
| `StaticQualifier` | `QualifiedTypeReference \| AssociatedProjection` | 892 |
| `AtControlExpr` | `AtIfExpr \| AtTryExpr \| AtScopeExpr` | 897 |
| `AtIfExpr` | `"@" "if" Expr ValueBody ("else" ValueBody)?` | 899 |
| `AtTryExpr` | `"@" "try" ValueBody (ValueCatchClause+ FinallyClause? \| FinallyClause)` | 900 |
| `AtScopeExpr` | `"@" "scope" ScopeModifier* ValueBody` | 901 |
| `ScopeModifier` | `"isolated" \| "cancellable" \| "shielded"` | 902 |
| `MatchExpr` | `"@" "match" MatchCore` | 904 |
| `ClosureExpr` | `CaptureList? HashTag* "{" ClosureContent "}"` | 908 |
| `ClosureContent` | `ExplicitLambdaContent \| LambdaBody?` | 909 |
| `ExplicitLambdaContent` | `LambdaParameterList? "=>" LambdaBody` | 910 |
| `LambdaParameterList` | `LambdaParameter ("," LambdaParameter)* ","?` | 911 |
| `LambdaParameter` | `ParameterMode? Identifier TypeAnnotation?` | 912 |
| `LambdaBody` | `Expr \| LineBreakBoundary LambdaBlockContent` | 913 |
| `LambdaBlockContent` | `BlockItem* LambdaFinalItem?` | 914 |
| `LambdaFinalItem` | `RetTransfer \| Expr` | 915 |
| `CaptureList` | `"[" CaptureItemList? "]"` | 917 |
| `CaptureItemList` | `CaptureItem ("," CaptureItem)* ","?` | 918 |
| `CaptureItem` | `("let" \| "var") Identifier "=" Expr \| CaptureMode Identifier \| Identifier` | 919 |
| `CaptureMode` | `"borrow" \| "inout" \| "move" \| "clone" \| "deep" \| "copy" \| "once"` | 922 |
| `GeneratorExpr` | `CaptureList? GeneratorCore` | 927 |
| `GeneratorCore` | `"@" "for" Pattern "in" Expr Block \| "@" "while" Expr Block \| "@" "repeat" Block "while" Expr` | 928 |
| `SpawnExpr` | `"spawn" TaskBody` | 932 |
| `TaskBody` | `"{" "=>" TaskBodySequence "}" \| "async" "{" "=>" TaskBodySequence "}"` | 933 |
| `TaskBodySequence` | `LineBreakBoundary? BlockSequence` | 935 |
| `StructuredTaskScope` | `"task" "scope" Block` | 936 |
| `UnsafeBlockExpr` | `"unsafe" Block` | 937 |
| `FacetExpr` | `"facet" "[" "borrow" Expr "as" QualifiedTypeReference AssociatedTypeConstraintList? "]"` | 940 |
| `ConformanceEvidenceSelector` | `"conformance" "(" TypeRef "conforms" QualifiedTypeReference ")"` | 942 |
| `NamedConformanceEvidenceSelector` | `ConformanceEvidenceSelector "::" Identifier` | 943 |
| `PrattExpr` | `EXPRESSION_PRATT_ENTRY` | 946 |
| `PrattPredicateExpr` | `PREDICATE_PRATT_ENTRY` | 947 |
| `PrattSliceIndexExpr` | `SLICE_INDEX_PRATT_ENTRY` | 948 |
| `Literal` | `BoolLiteral \| NumericLiteral \| StringLiteralExpr \| CharLiteralExpr \| BytesLiteral` | 956 |
| `BoolLiteral` | `"true" \| "false"` | 957 |
| `NumericLiteral` | `NUMERIC_LITERAL` | 958 |
| `CharLiteralExpr` | `CHAR_LITERAL` | 959 |
| `BytesLiteral` | `BYTES_LITERAL` | 960 |
| `StringLiteralExpr` | `PLAIN_STRING_LITERAL \| RAW_STRING_LITERAL \| MULTILINE_STRING_LITERAL \| InterpolatedString` | 963 |
| `InterpolatedString` | `STRING_START InterpolatedStringPart* STRING_END` | 964 |
| `InterpolatedStringPart` | `STRING_TEXT \| STRING_ESCAPE \| InterpolationExpr \| InterpolationPath` | 965 |
| `InterpolationExpr` | `INTERPOLATION_OPEN Expr InterpolationFormat? INTERPOLATION_CLOSE` | 969 |
| `InterpolationFormat` | `":" INTERPOLATION_FORMAT_TEXT` | 970 |
| `InterpolationPath` | `"$" InterpolationPathRoot InterpolationPathSelector* INTERPOLATION_BOUNDARY?` | 975 |
| `InterpolationPathRoot` | `Identifier \| "@"` | 976 |
| `InterpolationPathSelector` | `"." Identifier \| "." StaticIntLiteral \| "[" InterpolationIndex "]"` | 977 |
| `InterpolationIndex` | `StaticIntLiteral \| Identifier` | 980 |
| `ListLiteral` | `"[" ExpressionList? "]"` | 985 |
| `BoundedListLiteral` | `"[" StaticIntLiteral ".." StaticIntLiteral ":" ExpressionList? "]"` | 986 |
| `ComprehensionExpr` | `"[" Expr ComprehensionClause+ "]"` | 988 |
| `TypedMaterializationExpr` | `TypeRef MaterializationBody` | 991 |
| `MaterializationBody` | `"${" MaterializationEntryList? "}"` | 992 |
| `MaterializationEntryList` | `MaterializationEntry (MaterializationSeparator MaterializationEntry)* MaterializationSeparator?` | 993 |
| `MaterializationEntry` | `Identifier \| Identifier ":" Expr \| StringLiteralExpr ":" Expr \| NamedUnfoldArgument` | 994 |
| `MaterializationSeparator` | `"," LineBreakBoundary? \| LineBreakBoundary` | 998 |
| `MapLiteral` | `"#" "map" "{" MapEntryList? "}"` | 1001 |
| `MapEntryList` | `MapEntry (MaterializationSeparator MapEntry)* MaterializationSeparator?` | 1002 |
| `MapEntry` | `Expr ":" Expr \| NamedUnfoldArgument` | 1003 |
| `SetLiteral` | `"#" "set" "{" ExpressionList? "}"` | 1004 |
| `MutListLiteral` | `"#" "mut" "[" ExpressionList? "]"` | 1005 |
| `MapComprehensionExpr` | `"#" "map" "{" MapEntry ComprehensionClause+ "}"` | 1006 |
| `SetComprehensionExpr` | `"#" "set" "{" Expr ComprehensionClause+ "}"` | 1007 |
| `ComprehensionClause` | `ForClause \| PositiveGuard \| IfLetClause \| UnfoldClause` | 1009 |
| `ForClause` | `"for" Pattern "in" Expr` | 1010 |
| `IfLetClause` | `"if" "let" Pattern "=" Expr` | 1011 |
| `UnfoldClause` | `"for" "..." Pattern "in" Expr` | 1012 |
| `NumericArrayLiteral` | `ShapeInferredArrayLiteral \| ShapeInferredColumnVectorLiteral \| ExactShapeArrayLiteral` | 1015 |
| `ShapeInferredArrayLiteral` | `"#" "[" ExpressionList? "]"` | 1018 |
| `ShapeInferredColumnVectorLiteral` | `"#" "[" Expr (";" Expr)+ "]"` | 1019 |
| `ExactShapeArrayLiteral` | `"#" StaticDimensionList "[" ArrayInitializer? "]"` | 1020 |
| `ArrayInitializer` | `ShapedRepeatInitializer \| ShapedGeneratorInitializer \| ShapedElementSequence` | 1021 |
| `ShapedRepeatInitializer` | `"repeat" ":" Expr` | 1024 |
| `ShapedGeneratorInitializer` | `"generate" ":" Expr` | 1025 |
| `ShapedElementSequence` | `Expr (ShapedElementSeparator Expr)* ShapedElementSeparator?` | 1026 |
| `ShapedElementSeparator` | `"," \| ShapedAxisBoundary` | 1027 |
| `ShapedAxisBoundary` | `";" ";"*` | 1028 |
| `MeasureLiteralExpr` | `NumericLiteral "[" UnitExpr "]"` | 1031 |
| `UnitExpr` | `PrattUnitExpr` | 1032 |
| `UnitPrimary` | `Identifier \| QualifiedPath \| "(" UnitExpr ")"` | 1033 |
| `UnitPostfixParselet` | `"^" SignedStaticInt` | 1034 |
| `UnitInfixOperator` | `"*" \| "/"` | 1035 |
| `PrattUnitExpr` | `UNIT_PRATT_ENTRY` | 1036 |

## `PREVIEW` 프로파일 — 13개

| 문법 production | 정확한 EBNF 오른쪽 항 | 원천 줄 |
|---|---|---:|
| `DeeplusPreview` | `PreviewLibrarySourceFile \| PreviewExecutableSourceFile \| PreviewScriptSourceFile` | 1044 |
| `PreviewLibrarySourceFile` | `PreviewGate ModuleDecl? PreviewLibraryItem*` | 1045 |
| `PreviewExecutableSourceFile` | `PreviewGate ModuleDecl? PreviewExecutableItem*` | 1046 |
| `PreviewScriptSourceFile` | `Shebang? PreviewGate ModuleDecl? PreviewScriptItem*` | 1047 |
| `PreviewLibraryItem` | `LibrarySourceItem \| PreviewFfiDecl` | 1049 |
| `PreviewExecutableItem` | `ExecutableSourceItem \| PreviewFfiDecl` | 1050 |
| `PreviewScriptItem` | `ScriptSourceItem \| PreviewFfiDecl` | 1051 |
| `PreviewGate` | `"#" "preview" "(" PreviewFeatureList ")" LineBreakBoundary` | 1053 |
| `PreviewFeatureList` | `Identifier ("," Identifier)*` | 1054 |
| `PreviewFfiDecl` | `PreviewFfiFunctionDecl \| PreviewFfiBlockDecl` | 1057 |
| `PreviewFfiFunctionDecl` | `"extern" "#" "C" "def" "#" "unsafe" Identifier ParameterList ReturnClause? ThrowsClause? EffectsClause? StatementBoundary` | 1058 |
| `PreviewFfiBlockDecl` | `"extern" "c" "(" PLAIN_STRING_LITERAL ")" "{" PreviewFfiBlockMember* "}"` | 1060 |
| `PreviewFfiBlockMember` | `"unsafe" "def" Identifier ParameterList ReturnClause? ThrowsClause? EffectsClause? StatementBoundary` | 1062 |

## `RECOVERY` 프로파일 — 15개

| 문법 production | 정확한 EBNF 오른쪽 항 | 원천 줄 |
|---|---|---:|
| `RecoverySyntax` | `RecoveryGenericEntryFunctionDecl \| RecoveryFacetPackExpr \| RecoveryFacetType \| RecoveryNullLiteral \| RecoveryEmptyIndexSuffix \| RecoveryCustomOperatorDeclaration \| RecoveryNamedRestDoubleStar \| RecoveryFunctionTypeNamedRestDoubleStar \| RecoveryLazyBindingAt \| RecoveryUnitMiddleDot \| RecoveryQuarantineScope` | 1071 |
| `RecoveryNullLiteral` | `"null"` | 1085 |
| `RecoveryEmptyIndexSuffix` | `"[" "]"` | 1089 |
| `RecoveryCustomOperatorDeclaration` | `"operator" RecoveryOperatorSymbol ("precedence" StaticIntLiteral)? StatementBoundary` | 1090 |
| `RecoveryOperatorSymbol` | `ScannerRecoveryOperatorSymbol` | 1095 |
| `RecoveryGenericEntryFunctionDecl` | `"def" "#" "entry" Identifier TypeParameterList ParameterList ReturnClause? ThrowsClause? EffectsClause? ContractClause* FunctionBody \| "def" "#" "entry" "#" "async" Identifier TypeParameterList ParameterList ReturnClause? ThrowsClause? EffectsClause? ContractClause* FunctionBody` | 1098 |
| `RecoveryFacetPackExpr` | `"facet" "[" ("inout" \| "move") Expr "as" QualifiedTypeReference AssociatedTypeConstraintList? "]"` | 1104 |
| `RecoveryFacetType` | `"Facet" "<" ("inout" \| "move") "any" QualifiedTypeReference AssociatedTypeConstraintList? ">"` | 1106 |
| `RecoveryNamedRestDoubleStar` | `Identifier "**" TypeAnnotation` | 1111 |
| `RecoveryFunctionTypeNamedRestDoubleStar` | `TypeRef "**"` | 1112 |
| `RecoveryLazyBindingAt` | `"let" "@" "lazy" Identifier TypeAnnotation? "=" Expr StatementBoundary` | 1115 |
| `RecoveryUnitMiddleDot` | `UnitPrimary "·" UnitPrimary` | 1118 |
| `RecoveryQuarantineScope` | `"@" "scope" "#" ("dynamic" \| "unsafe") Block QuarantineExport?` | 1121 |
| `QuarantineExport` | `"->" "$" Identifier TypeAnnotation \| "->" "$" "(" QuarantineExportField ("," QuarantineExportField)* ")"` | 1122 |
| `QuarantineExportField` | `Identifier TypeAnnotation` | 1124 |
