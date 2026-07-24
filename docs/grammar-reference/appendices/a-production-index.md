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

## `STABLE` 프로파일 — 454개

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
| `EnumDecl` | `TopLevelVisibility? "enum" Identifier TypeParameterList? EnumBody` | 481 |
| `EnumBody` | `"{" (EnumCommaCaseSequence \| EnumLayoutBody)? "}"` | 482 |
| `EnumCommaCaseSequence` | `EnumCaseCore ("," EnumCaseCore)+ ","?` | 483 |
| `EnumLayoutBody` | `EnumCaseDecl* EnumMemberDecl*` | 484 |
| `EnumCaseDecl` | `EnumCaseCore StatementBoundary?` | 485 |
| `EnumCaseCore` | `Identifier EnumCasePayload?` | 486 |
| `EnumCasePayload` | `"(" EnumCaseFieldList? ")"` | 487 |
| `EnumCaseFieldList` | `EnumCaseField ("," EnumCaseField)* ","?` | 488 |
| `EnumCaseField` | `Identifier TypeAnnotation \| TypeRef` | 489 |
| `EnumMemberDecl` | `MemberFunctionDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl` | 490 |
| `SchemaDecl` | `TopLevelVisibility? "schema" Identifier TypeParameterList? SchemaBody` | 497 |
| `SchemaBody` | `"{" SchemaFieldSequence? "}"` | 498 |
| `SchemaFieldSequence` | `CommaSchemaFields \| LayoutSchemaFields` | 499 |
| `CommaSchemaFields` | `SchemaFieldDecl ("," SchemaFieldDecl)* ","?` | 500 |
| `LayoutSchemaFields` | `LineBreakBoundary LayoutSchemaFieldDecl (LineBreakBoundary LayoutSchemaFieldDecl)* LineBreakBoundary?` | 501 |
| `SchemaFieldDecl` | `Identifier TypeAnnotation Initializer? SchemaConstraint* StatementBoundary?` | 502 |
| `LayoutSchemaFieldDecl` | `Identifier TypeAnnotation Initializer? SchemaConstraint*` | 503 |
| `SchemaConstraint` | `"where" Expr` | 504 |
| `TypeAliasDecl` | `TopLevelVisibility? "type" Identifier TypeParameterList? "=" TypeAliasRhs StatementBoundary` | 506 |
| `TypeAliasRhs` | `TypeRef RefinementClause? \| StaticRangeType` | 507 |
| `StaticRangeType` | `StaticIntLiteral ".." StaticIntLiteral` | 508 |
| `TopLevelBindingDecl` | `TopLevelVisibility? ("let" \| "var") Identifier TypeAnnotation? "=" Expr StatementBoundary` | 510 |
| `NamedEffectCapabilityDecl` | `TopLevelVisibility? "capability" Identifier "for" EffectRow StatementBoundary` | 511 |
| `ActorDecl` | `TopLevelVisibility? "actor" MailboxClause? Identifier ActorBody` | 515 |
| `MailboxClause` | `HashTag "(" "capacity" ":" StaticIntLiteral ")"` | 516 |
| `ActorBody` | `"{" ActorItem* "}"` | 517 |
| `ActorItem` | `ActorOnDecl \| ActorRequestDecl \| MemberDecl` | 518 |
| `ActorOnDecl` | `MemberVisibility? "on" Identifier ParameterList? ThrowsClause? EffectsClause? FunctionBody` | 519 |
| `ActorRequestDecl` | `MemberVisibility? "request" Identifier ParameterList? ReturnClause ThrowsClause? EffectsClause? FunctionBody` | 520 |
| `ActorProtocolDecl` | `TopLevelVisibility? "protocol" Identifier ActorProtocolBody` | 522 |
| `ActorProtocolBody` | `"{" ActorProtocolItem* "}"` | 523 |
| `ActorProtocolItem` | `ActorProtocolSendRequirement \| ActorProtocolRequestRequirement` | 524 |
| `ActorProtocolSendRequirement` | `"send" Identifier ParameterList? ThrowsClause? EffectsClause? StatementBoundary` | 525 |
| `ActorProtocolRequestRequirement` | `"request" Identifier ParameterList? ReturnClause ThrowsClause? EffectsClause? StatementBoundary` | 526 |
| `TypestateResourceDecl` | `TopLevelVisibility? "typestate" Identifier TypeParameterList? TypestateBody` | 530 |
| `TypestateBody` | `"{" TypestateTransitionDecl* "}"` | 531 |
| `TypestateTransitionDecl` | `Identifier "->" Identifier FunctionBody?` | 532 |
| `UnitCatalogDecl` | `TopLevelVisibility? "unit" "catalog" Identifier UnitCatalogBody` | 534 |
| `UnitCatalogBody` | `"{" UnitCatalogEntry* "}"` | 535 |
| `UnitCatalogEntry` | `ExactRatioUnitConversionDecl \| Identifier "=" UnitExpr StatementBoundary` | 536 |
| `ExactRatioUnitConversionDecl` | `"unit" Identifier "equalsRatio" MeasureLiteralExpr "/" StaticIntLiteral StatementBoundary` | 537 |
| `ModuleInterfaceDecl` | `ModuleSignatureDecl \| OpaqueModuleFacadeDecl` | 539 |
| `ModuleSignatureDecl` | `TopLevelVisibility? "module" "signature" QualifiedPath ModuleInterfaceBody` | 540 |
| `OpaqueModuleFacadeDecl` | `TopLevelVisibility? "opaque" "module" QualifiedPath ModuleInterfaceBody` | 541 |
| `ModuleInterfaceBody` | `"{" ModuleInterfaceItem* "}"` | 542 |
| `ModuleInterfaceItem` | `ExportDecl \| UseExportDecl \| OpaqueModuleFacadeDecl` | 543 |
| `CleanupBudgetClause` | `"cleanup" "budget" "{" CleanupBudgetItem* "}"` | 547 |
| `CleanupBudgetItem` | `EffectsBudget \| ErrorsBudget` | 548 |
| `EffectsBudget` | `"effects" "{" IdentifierList? "}"` | 549 |
| `ErrorsBudget` | `"errors" TypeRef` | 550 |
| `BitfieldDecl` | `TopLevelVisibility? BitfieldIntroducer Identifier BitfieldBackingClause BitfieldOrderClause BitfieldBody` | 554 |
| `BitfieldIntroducer` | `"bitfield" HashTag?` | 556 |
| `BitfieldBackingClause` | `"backing" TypeRef` | 557 |
| `BitfieldOrderClause` | `"order" "::" "lsb0"` | 558 |
| `BitfieldBody` | `"{" BitfieldLayoutSection BitfieldMemberDecl* "}"` | 559 |
| `BitfieldLayoutSection` | `BitfieldSlotDecl+ \| FlagSlotDecl+` | 560 |
| `BitfieldSlotDecl` | `BitfieldNamedSlot StatementBoundary \| BitfieldReservedSlot StatementBoundary` | 561 |
| `FlagSlotDecl` | `FlagNamedSlot StatementBoundary \| BitfieldReservedSlot StatementBoundary` | 562 |
| `BitfieldNamedSlot` | `MemberVisibility? Identifier ":" StaticIntLiteral BitfieldDefault?` | 563 |
| `BitfieldReservedSlot` | `"_" ":" StaticIntLiteral` | 564 |
| `FlagNamedSlot` | `MemberVisibility? Identifier` | 565 |
| `BitfieldDefault` | `"=" Literal` | 566 |
| `BitfieldMemberDecl` | `MemberFunctionDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| LawDecl` | 567 |
| `TypeRef` | `PrattType` | 579 |
| `NonFunctionTypeRef` | `PrattNonFunctionType` | 580 |
| `TypePrimary` | `QualifiedTypeReference \| FacetType \| ParenTypeSyntax \| SharpShapeType \| ExistentialType \| OpaqueType \| TypeofType \| AssociatedProjection` | 583 |
| `TypePrefixParselet` | `OwnershipQualifier` | 591 |
| `TypePostfixParselet` | `"?"` | 592 |
| `TypeInfixOperator` | `"&" \| "\|"` | 593 |
| `QualifiedTypeReference` | `QualifiedPath TypeArgumentList?` | 595 |
| `FacetType` | `"Facet" "<" "borrow" "any" QualifiedTypeReference AssociatedTypeConstraintList? ">"` | 597 |
| `OwnershipQualifier` | `"owned" \| "borrowed" \| "mut" \| "inout"` | 598 |
| `ParenTypeSyntax` | `HashTag* "(" ParenTypeItemList? ")" FunctionTypeTail?` | 602 |
| `ParenTypeItemList` | `ParenTypeItem ("," ParenTypeItem)* ","?` | 603 |
| `ParenTypeItem` | `TypeRef \| TypeRef "..." \| TypeRef "***"` | 604 |
| `FunctionTypeTail` | `"->" NonFunctionTypeRef ThrowsClause? EffectsClause?` | 605 |
| `SharpShapeType` | `"#" StaticDimensionList "[" TypeRef "]"` | 607 |
| `StaticDimensionList` | `StaticIntLiteral ("," StaticIntLiteral)*` | 608 |
| `ExistentialType` | `"any" QualifiedTypeReference AssociatedTypeConstraintList?` | 610 |
| `OpaqueType` | `"some" QualifiedTypeReference AssociatedTypeConstraintList?` | 611 |
| `TypeofType` | `"typeof" TypeofStaticSampleOperand` | 612 |
| `AssociatedProjection` | `"<" TypeRef "as" QualifiedTypeReference ">" "::" Identifier` | 613 |
| `TypeofStaticSampleOperand` | `Literal \| ListLiteral \| StaticPrefixedCollectionSample \| NumericArrayLiteral \| MeasureLiteralExpr` | 616 |
| `StaticPrefixedCollectionSample` | `MapLiteral \| SetLiteral \| MutListLiteral` | 621 |
| `PrattType` | `TYPE_PRATT_ENTRY` | 624 |
| `PrattNonFunctionType` | `NON_FUNCTION_TYPE_PRATT_ENTRY` | 625 |
| `Pattern` | `OrPattern` | 633 |
| `OrPattern` | `AliasPattern ("\|" AliasPattern)*` | 634 |
| `AliasPattern` | `MovePattern ("as" Identifier)?` | 635 |
| `MovePattern` | `"move"? PatternPrimary` | 636 |
| `PatternPrimary` | `TypedBindingPattern \| Identifier \| RecordPattern \| ListPattern \| VariantPattern \| "_" \| UnitSyntax \| Literal \| ParenthesizedPattern` | 638 |
| `TypedBindingPattern` | `Identifier ":" TypeRef` | 648 |
| `ParenthesizedPattern` | `"(" Pattern ")"` | 649 |
| `BindingPattern` | `BindingOrPattern TypeAnnotation?` | 661 |
| `BindingOrPattern` | `BindingAliasPattern ("\|" BindingAliasPattern)*` | 662 |
| `BindingAliasPattern` | `BindingMovePattern ("as" Identifier)?` | 663 |
| `BindingMovePattern` | `"move"? BindingPatternPrimary` | 664 |
| `BindingPatternPrimary` | `Identifier \| RecordPattern \| ListPattern \| VariantPattern \| "_" \| UnitSyntax \| Literal \| ParenthesizedPattern` | 665 |
| `RecordPattern` | `"${" PatternFieldList? "}"` | 674 |
| `PatternFieldList` | `PatternField ("," PatternField)* ","?` | 675 |
| `PatternField` | `Identifier \| Identifier ":" Pattern` | 676 |
| `ListPattern` | `"[" (ListPatternPrefix ("," IgnoredListRest)? ","? \| IgnoredListRest ","?)? "]"` | 680 |
| `ListPatternPrefix` | `Pattern ("," Pattern)*` | 681 |
| `IgnoredListRest` | `".." "_"` | 682 |
| `VariantPattern` | `VariantQualifier Identifier VariantPatternPayload?` | 684 |
| `VariantQualifier` | `TypeRef "::" \| "::"` | 685 |
| `VariantPatternPayload` | `"(" PatternList? ")"` | 686 |
| `Stmt` | `ForLoop \| WhileLoop \| RepeatLoop \| AsyncForLoop \| TaskGroupStmt \| MatchStatement \| IfStmt \| LocalBindingStmt \| ControlTransferStmt \| TryStmt \| DeferStmt \| ScopedUseStmt \| ExprStmt \| ScopedImportStmt` | 694 |
| `ExprStmt` | `Expr StatementBoundary` | 709 |
| `Block` | `"{" BlockPrologue? BlockSequence "}"` | 711 |
| `BlockPrologue` | `(UseDecl \| ImportDecl)+` | 712 |
| `BlockSequence` | `BlockItem* BlockFinalItem?` | 713 |
| `BlockItem` | `LocalFunctionDecl \| Stmt` | 714 |
| `BlockFinalItem` | `ControlTransfer \| BindingCore \| Expr` | 717 |
| `ValueBody` | `SingleExpressionValueBody \| ExplicitRetValueBody` | 720 |
| `SingleExpressionValueBody` | `"{" Expr "}"` | 721 |
| `ExplicitRetValueBody` | `"{" BlockItem* RetTransfer "}"` | 722 |
| `RetTransfer` | `"ret" Expr? GuardClause?` | 723 |
| `BindingCore` | `("let" \| "var") BindingPattern "=" Expr` | 728 |
| `LocalBindingStmt` | `BindingCore StatementBoundary \| RightwardLocalBindingSurface \| LazyBindingStmt \| GuardedBindingStmt` | 729 |
| `LazyBindingStmt` | `"let" HashTag Identifier TypeAnnotation? "=" Expr StatementBoundary` | 730 |
| `GuardedBindingStmt` | `"let" BindingPattern "=" Expr "else" GuardedBindingFailure StatementBoundary?` | 731 |
| `GuardedBindingFailure` | `GuardedBindingExit \| Pattern "=>" GuardedBindingExit` | 733 |
| `GuardedBindingExit` | `GuardedReturnExit \| GuardedThrowExit \| GuardedBreakExit \| GuardedContinueExit` | 734 |
| `GuardedReturnExit` | `"return" Expr?` | 735 |
| `GuardedThrowExit` | `"throw" Expr` | 736 |
| `GuardedBreakExit` | `("break")+ Expr?` | 737 |
| `GuardedContinueExit` | `("break")* "continue"` | 738 |
| `ControlTransferStmt` | `ControlTransfer StatementBoundary` | 741 |
| `ControlTransfer` | `ReturnTransfer \| ThrowTransfer \| BreakTransfer \| ContinueTransfer \| YieldTransfer` | 742 |
| `ReturnTransfer` | `"return" Expr? GuardClause?` | 743 |
| `ThrowTransfer` | `"throw" Expr GuardClause?` | 744 |
| `BreakTransfer` | `("break")+ Expr? GuardClause?` | 745 |
| `ContinueTransfer` | `("break")* "continue" GuardClause?` | 746 |
| `YieldTransfer` | `"yield" Expr? (GuardClause \| YieldResponseBinding)?` | 747 |
| `YieldResponseBinding` | `"->" DollarLocalBinding` | 748 |
| `DollarLocalBinding` | `"$" Identifier TypeAnnotation? \| "$$" Identifier TypeAnnotation?` | 749 |
| `GuardClause` | `PositiveGuard \| NegativeGuard` | 751 |
| `PositiveGuard` | `"if" Expr` | 752 |
| `NegativeGuard` | `"!" "if" Expr` | 753 |
| `IfStmt` | `"if" PatternControlCondition Block ("else" (IfStmt \| Block))?` | 755 |
| `PatternControlCondition` | `Expr \| "let" Pattern "=" Expr` | 756 |
| `ForLoop` | `"for" ("let" Pattern \| Pattern) "in" Expr GuardClause? Block MatchStatement?` | 760 |
| `WhileLoop` | `"while" PatternControlCondition Block MatchStatement?` | 761 |
| `RepeatLoop` | `"repeat" Block "while" Expr MatchStatement?` | 762 |
| `AsyncForLoop` | `"for" "await" ("let" Pattern \| Pattern) "in" Expr GuardClause? Block` | 763 |
| `MatchStatement` | `"match" MatchCore` | 765 |
| `MatchCore` | `MatchSubjectSlot MatchBody` | 766 |
| `MatchSubjectSlot` | `MATCH_SUBJECT_BY_INPUT_SUPPLY_POLICY` | 767 |
| `MatchBody` | `"{" LineBreakBoundary? MatchArmSequence "}"` | 768 |
| `MatchArmSequence` | `MatchArm (MatchArmSeparator MatchArm)* MatchArmSeparator?` | 769 |
| `MatchArm` | `MatchHead GuardClause? "=>" MatchArmBodySlot` | 770 |
| `MatchHead` | `Pattern \| "otherwise"` | 771 |
| `MatchArmSeparator` | `MATCH_ARM_SEPARATOR_BY_CONTEXT` | 772 |
| `MatchArmBodySlot` | `MATCH_ARM_BODY_BY_CONTEXT` | 773 |
| `TryStmt` | `"try" Block (CatchClause+ FinallyClause? \| FinallyClause)` | 777 |
| `CatchClause` | `"catch" Pattern? Block` | 778 |
| `ValueCatchClause` | `"catch" Pattern? ValueBody` | 779 |
| `FinallyClause` | `"finally" Block` | 780 |
| `DeferStmt` | `"defer" DeferredCleanupInvocation StatementBoundary` | 782 |
| `DeferredCleanupInvocation` | `DeferredDirectCall \| DeferredMessageCall` | 785 |
| `DeferredDirectCall` | `DeferredReceiver ArgumentList` | 786 |
| `DeferredMessageCall` | `DeferredReceiver "~" MessageSelector MessagePayload?` | 787 |
| `DeferredReceiver` | `DeferredPrimary DeferTargetSuffix*` | 788 |
| `DeferredPrimary` | `Identifier \| QualifiedStaticExpr` | 789 |
| `DeferTargetSuffix` | `IndexSuffix \| MemberSuffix` | 790 |
| `RightwardLocalBindingSurface` | `Expr "->" DollarLocalBinding StatementBoundary` | 794 |
| `ScopedUseStmt` | `"use" ScopedPathList "in" Block` | 795 |
| `ScopedImportStmt` | `"import" ScopedPathList "in" Block` | 796 |
| `ScopedPathList` | `QualifiedPath ("," QualifiedPath)*` | 797 |
| `TaskGroupStmt` | `"task" "group" Identifier? Block` | 798 |
| `Expr` | `PrattExpr` | 806 |
| `PredicateExpr` | `PrattPredicateExpr` | 807 |
| `SliceIndexExpr` | `PrattSliceIndexExpr` | 808 |
| `ExpressionPrefixParselet` | `"+" \| "-" \| "not" \| "~~" \| "move" \| "borrow" \| "&" \| "await"` | 814 |
| `ExpressionPostfixParselet` | `CallSuffix \| TupleOrdinalSuffix \| IndexSuffix \| MemberSuffix \| MessageSuffix \| NumericArrayTransposeSuffix \| ConstructorCallSuffix \| NamedConstructorCallSuffix \| PrototypeDerivationSuffix \| CastSuffix` | 816 |
| `PrimaryExpr` | `Literal \| Identifier \| ImplicitAtExpr \| ParenExprSyntax \| ListLiteral \| BoundedListLiteral \| ComprehensionExpr \| MaterializationBody \| TypedMaterializationExpr \| MapLiteral \| SetLiteral \| MutListLiteral \| MapComprehensionExpr \| SetComprehensionExpr \| NumericArrayLiteral \| MeasureLiteralExpr \| QualifiedStaticExpr \| ExpectedVariantExpr \| AtControlExpr \| MatchExpr \| ClosureExpr \| GeneratorExpr \| SpawnExpr \| StructuredTaskScope \| UnsafeBlockExpr \| FacetExpr` | 827 |
| `ParenExprSyntax` | `"(" ParenExprContent? ")"` | 855 |
| `ParenExprContent` | `Expr ParenExprTail?` | 856 |
| `ParenExprTail` | `"," \| "," Expr ("," Expr)* ","?` | 857 |
| `ImplicitAtExpr` | `"@"` | 858 |
| `ExpectedVariantExpr` | `"::" Identifier` | 859 |
| `CallSuffix` | `ArgumentList TrailingClosureGroup? \| AtomicCallArgument TrailingClosureGroup` | 863 |
| `ArgumentList` | `"(" ")" \| "(" CommaArgumentSequence ")" \| "(" LayoutArgumentSequence ")"` | 866 |
| `CommaArgumentSequence` | `Argument ("," Argument)* ","?` | 869 |
| `LayoutArgumentSequence` | `LineBreakBoundary NamedLayoutArgument LineBreakBoundary NamedLayoutArgument (LineBreakBoundary NamedLayoutArgument)* LineBreakBoundary?` | 871 |
| `NamedLayoutArgument` | `NamedArgument \| NamedUnfoldArgument` | 873 |
| `Argument` | `ContextArgument \| WitnessArgument \| NamedArgument \| PositionalUnfoldArgument \| NamedUnfoldArgument \| Expr` | 874 |
| `ContextArgument` | `"context" Expr` | 880 |
| `WitnessArgument` | `"using" WitnessArgumentValue` | 881 |
| `WitnessArgumentValue` | `Identifier \| ConformanceEvidenceSelector \| NamedConformanceEvidenceSelector` | 882 |
| `NamedArgument` | `Identifier ":" Expr` | 883 |
| `PositionalUnfoldArgument` | `"*" Expr` | 884 |
| `NamedUnfoldArgument` | `"**" Expr` | 885 |
| `AtomicCallArgument` | `Literal \| Identifier \| QualifiedStaticExpr \| ExpectedVariantExpr` | 886 |
| `TrailingClosureGroup` | `TrailingClosureArgument+` | 890 |
| `TrailingClosureArgument` | `ClosureExpr \| Identifier ":" ClosureExpr` | 891 |
| `IndexSuffix` | `"[" SliceAxisList "]"` | 895 |
| `SliceAxisList` | `SliceAxis (";" SliceAxis)*` | 896 |
| `SliceAxis` | `SliceRange \| SliceIndexExpr \| AxisWildcard` | 897 |
| `SliceRange` | `SliceBound (".." \| "..<") SliceBound` | 900 |
| `SliceBound` | `SliceIndexExpr \| "^" \| "$" \| "^" OffsetExpr \| "$" OffsetExpr` | 901 |
| `OffsetExpr` | `("+" \| "-") NumericLiteral` | 902 |
| `AxisWildcard` | `"*"` | 903 |
| `TupleOrdinalSuffix` | `"." StaticIntLiteral` | 905 |
| `MemberSuffix` | `"." Identifier \| "." "\\\\" NAME_TOKEN` | 906 |
| `MessageSuffix` | `"~" MessageSelector MessagePayload? TrailingClosureGroup?` | 912 |
| `MessageSelector` | `Identifier \| QualifiedMessageSelector` | 913 |
| `QualifiedMessageSelector` | `TypeRef "::" Identifier ("::" Identifier)?` | 914 |
| `QualifiedExtensionSelector` | `TypeRef "::" Identifier "::" Identifier` | 915 |
| `MessagePayload` | `AtomicCallArgument \| MessagePayloadEnvelope` | 916 |
| `MessagePayloadEnvelope` | `"(" ")" \| "(" Expr ")" \| "(" Expr "," Expr ("," Expr)* ","? ")" \| "(" MessageNamedPayloadEntry ("," MessageNamedPayloadEntry)* ","? ")"` | 917 |
| `MessageNamedPayloadEntry` | `Identifier ":" Expr` | 922 |
| `NumericArrayTransposeSuffix` | `"^"` | 924 |
| `ConstructorCallSuffix` | `"!" ArgumentList` | 925 |
| `NamedConstructorCallSuffix` | `"!" Identifier ArgumentList` | 926 |
| `PrototypeDerivationSuffix` | `("!" \| "!!") DerivationBody` | 927 |
| `DerivationBody` | `"{" MaterializationEntryList? "}"` | 928 |
| `CastSuffix` | `"as" "?" TypeRef \| "as" "!" TypeRef` | 930 |
| `QualifiedStaticExpr` | `StaticQualifier "::" Identifier \| TraitQualifiedAssociatedSelector` | 932 |
| `StaticQualifier` | `QualifiedTypeReference \| AssociatedProjection` | 934 |
| `TraitQualifiedAssociatedSelector` | `"<" TypeRef "as" QualifiedTypeReference ">" "::" Identifier` | 935 |
| `AtControlExpr` | `AtIfExpr \| AtTryExpr \| AtScopeExpr` | 941 |
| `AtIfExpr` | `"@" "if" Expr ValueBody ("else" ValueBody)?` | 943 |
| `AtTryExpr` | `"@" "try" ValueBody (ValueCatchClause+ FinallyClause? \| FinallyClause)` | 944 |
| `AtScopeExpr` | `"@" "scope" ScopeModifier* ValueBody` | 945 |
| `ScopeModifier` | `"isolated" \| "cancellable" \| "shielded"` | 946 |
| `MatchExpr` | `"@" "match" MatchCore` | 948 |
| `ClosureExpr` | `CaptureList? HashTag* "{" ClosureContent "}"` | 952 |
| `ClosureContent` | `ExplicitLambdaContent \| LambdaBody?` | 953 |
| `ExplicitLambdaContent` | `LambdaParameterList? "=>" LambdaBody` | 954 |
| `LambdaParameterList` | `LambdaParameter ("," LambdaParameter)* ","?` | 955 |
| `LambdaParameter` | `ParameterMode? Identifier TypeAnnotation?` | 956 |
| `LambdaBody` | `Expr \| LineBreakBoundary LambdaBlockContent` | 957 |
| `LambdaBlockContent` | `BlockItem* LambdaFinalItem?` | 958 |
| `LambdaFinalItem` | `RetTransfer \| Expr` | 959 |
| `CaptureList` | `"[" CaptureItemList? "]"` | 961 |
| `CaptureItemList` | `CaptureItem ("," CaptureItem)* ","?` | 962 |
| `CaptureItem` | `("let" \| "var") Identifier "=" Expr \| CaptureMode Identifier \| Identifier` | 963 |
| `CaptureMode` | `"borrow" \| "inout" \| "move" \| "clone" \| "deep" \| "copy" \| "once"` | 966 |
| `GeneratorExpr` | `CaptureList? GeneratorCore` | 971 |
| `GeneratorCore` | `"@" "for" Pattern "in" Expr Block \| "@" "while" Expr Block \| "@" "repeat" Block "while" Expr` | 972 |
| `SpawnExpr` | `"spawn" TaskBody` | 976 |
| `TaskBody` | `"{" "=>" TaskBodySequence "}" \| "async" "{" "=>" TaskBodySequence "}"` | 977 |
| `TaskBodySequence` | `LineBreakBoundary? BlockSequence` | 979 |
| `StructuredTaskScope` | `"task" "scope" Block` | 980 |
| `UnsafeBlockExpr` | `"unsafe" Block` | 981 |
| `FacetExpr` | `"facet" "[" "borrow" Expr "as" QualifiedTypeReference AssociatedTypeConstraintList? "]"` | 984 |
| `ConformanceEvidenceSelector` | `"conformance" "(" TypeRef "conforms" QualifiedTypeReference ")"` | 986 |
| `NamedConformanceEvidenceSelector` | `ConformanceEvidenceSelector "::" Identifier` | 987 |
| `PrattExpr` | `EXPRESSION_PRATT_ENTRY` | 990 |
| `PrattPredicateExpr` | `PREDICATE_PRATT_ENTRY` | 991 |
| `PrattSliceIndexExpr` | `SLICE_INDEX_PRATT_ENTRY` | 992 |
| `Literal` | `BoolLiteral \| NumericLiteral \| ImaginaryLiteralExpr \| RationalLiteralExpr \| StringLiteralExpr \| CharLiteralExpr \| BytesLiteral` | 1000 |
| `BoolLiteral` | `"true" \| "false"` | 1007 |
| `NumericLiteral` | `NUMERIC_LITERAL` | 1008 |
| `ImaginaryLiteralExpr` | `IMAGINARY_LITERAL` | 1009 |
| `RationalLiteralExpr` | `RATIONAL_LITERAL` | 1010 |
| `CharLiteralExpr` | `CHAR_LITERAL` | 1011 |
| `BytesLiteral` | `BYTES_LITERAL` | 1012 |
| `StringLiteralExpr` | `PLAIN_STRING_LITERAL \| RAW_STRING_LITERAL \| MULTILINE_STRING_LITERAL \| InterpolatedString` | 1015 |
| `InterpolatedString` | `STRING_START InterpolatedStringPart* STRING_END` | 1016 |
| `InterpolatedStringPart` | `STRING_TEXT \| STRING_ESCAPE \| InterpolationExpr \| InterpolationPath` | 1017 |
| `InterpolationExpr` | `INTERPOLATION_OPEN Expr InterpolationFormat? INTERPOLATION_CLOSE` | 1021 |
| `InterpolationFormat` | `":" INTERPOLATION_FORMAT_TEXT` | 1022 |
| `InterpolationPath` | `"$" InterpolationPathRoot InterpolationPathSelector* INTERPOLATION_BOUNDARY?` | 1027 |
| `InterpolationPathRoot` | `Identifier \| "@"` | 1028 |
| `InterpolationPathSelector` | `"." Identifier \| "." StaticIntLiteral \| "[" InterpolationIndex "]"` | 1029 |
| `InterpolationIndex` | `StaticIntLiteral \| Identifier` | 1032 |
| `ListLiteral` | `"[" ExpressionList? "]"` | 1037 |
| `BoundedListLiteral` | `"[" StaticIntLiteral ".." StaticIntLiteral ":" ExpressionList? "]"` | 1038 |
| `ComprehensionExpr` | `"[" Expr ComprehensionClause+ "]"` | 1040 |
| `TypedMaterializationExpr` | `TypeRef MaterializationBody` | 1043 |
| `MaterializationBody` | `"${" MaterializationEntryList? "}"` | 1044 |
| `MaterializationEntryList` | `MaterializationEntry (MaterializationSeparator MaterializationEntry)* MaterializationSeparator?` | 1045 |
| `MaterializationEntry` | `Identifier \| Identifier ":" Expr \| StringLiteralExpr ":" Expr \| NamedUnfoldArgument` | 1046 |
| `MaterializationSeparator` | `"," LineBreakBoundary? \| LineBreakBoundary` | 1050 |
| `MapLiteral` | `"#" "map" "{" MapEntryList? "}"` | 1053 |
| `MapEntryList` | `MapEntry (MaterializationSeparator MapEntry)* MaterializationSeparator?` | 1054 |
| `MapEntry` | `Expr ":" Expr \| NamedUnfoldArgument` | 1055 |
| `SetLiteral` | `"#" "set" "{" ExpressionList? "}"` | 1056 |
| `MutListLiteral` | `"#" "mut" "[" ExpressionList? "]"` | 1057 |
| `MapComprehensionExpr` | `"#" "map" "{" MapEntry ComprehensionClause+ "}"` | 1058 |
| `SetComprehensionExpr` | `"#" "set" "{" Expr ComprehensionClause+ "}"` | 1059 |
| `ComprehensionClause` | `ForClause \| PositiveGuard \| IfLetClause \| UnfoldClause` | 1061 |
| `ForClause` | `"for" Pattern "in" Expr` | 1062 |
| `IfLetClause` | `"if" "let" Pattern "=" Expr` | 1063 |
| `UnfoldClause` | `"for" "..." Pattern "in" Expr` | 1064 |
| `NumericArrayLiteral` | `ShapeInferredArrayLiteral \| ShapeInferredColumnVectorLiteral \| ExactShapeArrayLiteral` | 1067 |
| `ShapeInferredArrayLiteral` | `"#" "[" ExpressionList? "]"` | 1070 |
| `ShapeInferredColumnVectorLiteral` | `"#" "[" Expr (";" Expr)+ "]"` | 1071 |
| `ExactShapeArrayLiteral` | `"#" StaticDimensionList "[" ArrayInitializer? "]"` | 1072 |
| `ArrayInitializer` | `ShapedRepeatInitializer \| ShapedGeneratorInitializer \| ShapedElementSequence` | 1073 |
| `ShapedRepeatInitializer` | `"repeat" ":" Expr` | 1076 |
| `ShapedGeneratorInitializer` | `"generate" ":" Expr` | 1077 |
| `ShapedElementSequence` | `Expr (ShapedElementSeparator Expr)* ShapedElementSeparator?` | 1078 |
| `ShapedElementSeparator` | `"," \| ShapedAxisBoundary` | 1079 |
| `ShapedAxisBoundary` | `";" ";"*` | 1080 |
| `MeasureLiteralExpr` | `NumericLiteral "[" UnitExpr "]"` | 1083 |
| `UnitExpr` | `PrattUnitExpr` | 1084 |
| `UnitPrimary` | `Identifier \| QualifiedPath \| "(" UnitExpr ")"` | 1085 |
| `UnitPostfixParselet` | `"^" SignedStaticInt` | 1086 |
| `UnitInfixOperator` | `"*" \| "/"` | 1087 |
| `PrattUnitExpr` | `UNIT_PRATT_ENTRY` | 1088 |

## `PREVIEW` 프로파일 — 13개

| 문법 production | 정확한 EBNF 오른쪽 항 | 원천 줄 |
|---|---|---:|
| `DeeplusPreview` | `PreviewLibrarySourceFile \| PreviewExecutableSourceFile \| PreviewScriptSourceFile` | 1096 |
| `PreviewLibrarySourceFile` | `PreviewGate ModuleDecl? PreviewLibraryItem*` | 1097 |
| `PreviewExecutableSourceFile` | `PreviewGate ModuleDecl? PreviewExecutableItem*` | 1098 |
| `PreviewScriptSourceFile` | `Shebang? PreviewGate ModuleDecl? PreviewScriptItem*` | 1099 |
| `PreviewLibraryItem` | `LibrarySourceItem \| PreviewFfiDecl` | 1101 |
| `PreviewExecutableItem` | `ExecutableSourceItem \| PreviewFfiDecl` | 1102 |
| `PreviewScriptItem` | `ScriptSourceItem \| PreviewFfiDecl` | 1103 |
| `PreviewGate` | `"#" "preview" "(" PreviewFeatureList ")" LineBreakBoundary` | 1105 |
| `PreviewFeatureList` | `Identifier ("," Identifier)*` | 1106 |
| `PreviewFfiDecl` | `PreviewFfiFunctionDecl \| PreviewFfiBlockDecl` | 1109 |
| `PreviewFfiFunctionDecl` | `"extern" "#" "C" "def" "#" "unsafe" Identifier ParameterList ReturnClause? ThrowsClause? EffectsClause? StatementBoundary` | 1110 |
| `PreviewFfiBlockDecl` | `"extern" "c" "(" PLAIN_STRING_LITERAL ")" "{" PreviewFfiBlockMember* "}"` | 1112 |
| `PreviewFfiBlockMember` | `"unsafe" "def" Identifier ParameterList ReturnClause? ThrowsClause? EffectsClause? StatementBoundary` | 1114 |

## `RECOVERY` 프로파일 — 15개

| 문법 production | 정확한 EBNF 오른쪽 항 | 원천 줄 |
|---|---|---:|
| `RecoverySyntax` | `RecoveryGenericEntryFunctionDecl \| RecoveryFacetPackExpr \| RecoveryFacetType \| RecoveryNullLiteral \| RecoveryEmptyIndexSuffix \| RecoveryCustomOperatorDeclaration \| RecoveryNamedRestDoubleStar \| RecoveryFunctionTypeNamedRestDoubleStar \| RecoveryLazyBindingAt \| RecoveryUnitMiddleDot \| RecoveryQuarantineScope` | 1123 |
| `RecoveryNullLiteral` | `"null"` | 1137 |
| `RecoveryEmptyIndexSuffix` | `"[" "]"` | 1141 |
| `RecoveryCustomOperatorDeclaration` | `"operator" RecoveryOperatorSymbol ("precedence" StaticIntLiteral)? StatementBoundary` | 1142 |
| `RecoveryOperatorSymbol` | `ScannerRecoveryOperatorSymbol` | 1147 |
| `RecoveryGenericEntryFunctionDecl` | `"def" "#" "entry" Identifier TypeParameterList ParameterList ReturnClause? ThrowsClause? EffectsClause? ContractClause* FunctionBody \| "def" "#" "entry" "#" "async" Identifier TypeParameterList ParameterList ReturnClause? ThrowsClause? EffectsClause? ContractClause* FunctionBody` | 1150 |
| `RecoveryFacetPackExpr` | `"facet" "[" ("inout" \| "move") Expr "as" QualifiedTypeReference AssociatedTypeConstraintList? "]"` | 1156 |
| `RecoveryFacetType` | `"Facet" "<" ("inout" \| "move") "any" QualifiedTypeReference AssociatedTypeConstraintList? ">"` | 1158 |
| `RecoveryNamedRestDoubleStar` | `Identifier "**" TypeAnnotation` | 1163 |
| `RecoveryFunctionTypeNamedRestDoubleStar` | `TypeRef "**"` | 1164 |
| `RecoveryLazyBindingAt` | `"let" "@" "lazy" Identifier TypeAnnotation? "=" Expr StatementBoundary` | 1167 |
| `RecoveryUnitMiddleDot` | `UnitPrimary "·" UnitPrimary` | 1170 |
| `RecoveryQuarantineScope` | `"@" "scope" "#" ("dynamic" \| "unsafe") Block QuarantineExport?` | 1173 |
| `QuarantineExport` | `"->" "$" Identifier TypeAnnotation \| "->" "$" "(" QuarantineExportField ("," QuarantineExportField)* ")"` | 1174 |
| `QuarantineExportField` | `Identifier TypeAnnotation` | 1176 |
