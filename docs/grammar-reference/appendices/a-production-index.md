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

## `STABLE` 프로파일 — 516개

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
| `ReturnClause` | `"->" ReturnTypeSurface` | 239 |
| `ReturnTypeSurface` | `NonFunctionTypeRef \| BareTupleTypeSurface` | 240 |
| `BareTupleTypeSurface` | `NonFunctionTypeRef "," NonFunctionTypeRef ("," NonFunctionTypeRef)*` | 241 |
| `ThrowsClause` | `"throws" ErrorSet` | 242 |
| `EffectsClause` | `"effects" EffectRow` | 243 |
| `ContractClause` | `RequiresClause \| EnsuresClause` | 244 |
| `RequiresClause` | `"requires" PredicateExpr` | 245 |
| `EnsuresClause` | `"ensures" PredicateExpr` | 246 |
| `LineBreakBoundary` | `LINE_BREAK_IN_TRIVIA` | 251 |
| `StatementBoundary` | `STATEMENT_BOUNDARY_BY_CONTEXT` | 252 |
| `IdentifierList` | `Identifier ("," Identifier)* ","?` | 254 |
| `ExpressionList` | `Expr ("," Expr)* ","?` | 255 |
| `PatternList` | `Pattern ("," Pattern)* ","?` | 256 |
| `StaticIntLiteral` | `DECIMAL_INTEGER` | 258 |
| `UnitSyntax` | `"(" ")"` | 261 |
| `SignedStaticInt` | `("+" \| "-")? StaticIntLiteral` | 262 |
| `LawDecl` | `"law" Identifier LawBody? StatementBoundary` | 264 |
| `LawBody` | `"{" LawBodyItem* "}"` | 267 |
| `LawBodyItem` | `LawAssertion StatementBoundary` | 268 |
| `LawAssertion` | `("requires" \| "ensures" \| "invariant")? PredicateExpr` | 269 |
| `Deeplus` | `LibrarySourceFile \| ExecutableSourceFile \| ScriptSourceFile` | 277 |
| `LibrarySourceFile` | `ModuleDecl? LibrarySourceItem*` | 279 |
| `ExecutableSourceFile` | `ModuleDecl? ExecutableSourceItem*` | 280 |
| `ScriptSourceFile` | `Shebang? ModuleDecl? ScriptSourceItem*` | 281 |
| `LibrarySourceItem` | `AnnotationAttachment LibraryAnnotatableDecl \| ImportOrUseDecl \| TopLevelDecl` | 283 |
| `ExecutableSourceItem` | `AnnotationAttachment ExecutableAnnotatableDecl \| ImportOrUseDecl \| NonBindingTopLevelDecl \| EntryFunctionDecl` | 286 |
| `ScriptSourceItem` | `AnnotationAttachment ScriptAnnotatableDecl \| ImportOrUseDecl \| NonBindingTopLevelDecl \| Stmt` | 290 |
| `LibraryAnnotatableDecl` | `ImportOrUseDecl \| TopLevelDecl` | 295 |
| `ExecutableAnnotatableDecl` | `ImportOrUseDecl \| NonBindingTopLevelDecl \| EntryFunctionDecl` | 296 |
| `ScriptAnnotatableDecl` | `ImportOrUseDecl \| NonBindingTopLevelDecl` | 297 |
| `ModuleDecl` | `"module" QualifiedPath StatementBoundary` | 299 |
| `ImportOrUseDecl` | `ImportDecl \| UseDecl \| UseExportDecl` | 301 |
| `ImportDecl` | `"import" QualifiedPath ImportTail? StatementBoundary` | 302 |
| `ImportTail` | `ImportAlias \| ImportSelection` | 303 |
| `ImportAlias` | `NameAliasClause` | 304 |
| `ImportSelection` | `"::" "{" IdentifierList "}"` | 305 |
| `UseDecl` | `"use" QualifiedPath StatementBoundary` | 306 |
| `UseExportDecl` | `"use" "export" QualifiedPath StatementBoundary` | 307 |
| `ExportDecl` | `"export" ExportItem StatementBoundary?` | 310 |
| `ExportItem` | `ExportableModuleFunctionDecl \| TypeDecl \| Identifier` | 311 |
| `ExportableModuleFunctionDecl` | `TopLevelVisibility? "def" Identifier FunctionRest` | 312 |
| `TopLevelDecl` | `NonBindingTopLevelDecl \| TopLevelBindingDecl` | 320 |
| `NonBindingTopLevelDecl` | `TypeDecl \| ModuleFunctionDecl \| ExtensionFunctionDecl \| ActorDecl \| ActorProtocolDecl \| TypestateResourceDecl \| NamedEffectCapabilityDecl \| ExtensionSetDecl \| ExtensionPackDecl \| UnitCatalogDecl \| ModuleInterfaceDecl \| ConformanceDecl \| SchemaDecl \| BitfieldDecl` | 321 |
| `TypeDecl` | `ClassDecl \| TraitDecl \| EnumDecl \| TypeAliasDecl` | 336 |
| `DefIntroducer` | `"def" HashTag*` | 340 |
| `ModuleFunctionDecl` | `TopLevelVisibility? DefIntroducer Identifier FunctionRest` | 342 |
| `EntryFunctionDecl` | `DefIntroducer Identifier EntryFunctionRest` | 343 |
| `ExtensionFunctionDecl` | `TopLevelVisibility? DefIntroducer TypeRef ExtensionFunctionTarget Identifier FunctionRest` | 344 |
| `ExtensionFunctionTarget` | `"~" \| "::"` | 345 |
| `LocalFunctionDecl` | `CaptureList? DefIntroducer Identifier FunctionRest` | 346 |
| `FunctionRest` | `TypeParameterList? ParameterList FunctionTail` | 348 |
| `EntryFunctionRest` | `ParameterList ReturnClause? ThrowsClause? EffectsClause? ContractClause* FunctionBody` | 349 |
| `FunctionTail` | `ReturnClause? ThrowsClause? EffectsClause? ContractClause* WhereClause? FunctionBody` | 350 |
| `TraitFunctionTail` | `ReturnClause? ThrowsClause? EffectsClause? ContractClause* WhereClause? (FunctionBody \| StatementBoundary)` | 351 |
| `FunctionBody` | `"=" FunctionBodyContent` | 353 |
| `FunctionBodyContent` | `CallableBlock \| ReturnShorthand \| ClauseFunctionBody` | 354 |
| `CallableBlock` | `"{" BlockPrologue? FunctionStaticActivation? BlockSequence "}"` | 360 |
| `FunctionStaticActivation` | `"static" Block` | 361 |
| `ReturnShorthand` | `"return" ReturnValueSurface StatementBoundary` | 362 |
| `ClauseFunctionBody` | `"{{" LineBreakBoundary? MatchArmSequence "}}"` | 363 |
| `MemberFunctionDecl` | `MemberVisibility? DefIntroducer Identifier ClassDispatchMarker FunctionRest` | 365 |
| `TypeSideMemberFunctionDecl` | `MemberVisibility? "def" "::" Identifier FunctionRest` | 366 |
| `ConstructorDecl` | `MemberVisibility? "def" "!" Identifier ParameterList ConstructorSignatureTail? ConstructorDelegationClause? "=" Block` | 368 |
| `ConstructorSignatureTail` | `ThrowsClause EffectsClause? ContractClause* WhereClause? \| EffectsClause ContractClause* WhereClause? \| ContractClause+ WhereClause? \| WhereClause` | 370 |
| `ConstructorDelegationClause` | `":" ConstructorDelegationArm+` | 374 |
| `ConstructorDelegationArm` | `ConstructorDelegationTarget PositiveGuard?` | 375 |
| `ConstructorDelegationTarget` | `Identifier ArgumentList \| "super" "!" Identifier? ArgumentList` | 376 |
| `CleanupDecl` | `DefIntroducer "(" ")" ThrowsClause? EffectsClause? FunctionBody` | 379 |
| `ParameterList` | `"(" ParameterSequence? ")"` | 383 |
| `ParameterSequence` | `CommaParameterSequence \| LayoutParameterSequence` | 384 |
| `CommaParameterSequence` | `Parameter ("," Parameter)* ","?` | 385 |
| `LayoutParameterSequence` | `LineBreakBoundary Parameter (LineBreakBoundary Parameter)* LineBreakBoundary?` | 386 |
| `Parameter` | `StoredParameter \| ContextParameter \| WitnessParameter \| RepeatedParameter \| NamedRestParameter \| ValueParameter` | 388 |
| `ValueParameter` | `ParameterMode? ParameterPatternSlot TypeAnnotation` | 394 |
| `ParameterPatternSlot` | `Identifier IrrefutableParameterPattern?` | 399 |
| `IrrefutableParameterPattern` | `TuplePattern \| ListPattern \| RecordPattern \| NominalPattern` | 400 |
| `ParameterMode` | `"borrow" \| "mut" \| "move" \| "inout"` | 404 |
| `ContextParameter` | `"context" Identifier ":" TypeRef` | 405 |
| `WitnessParameter` | `"using" Identifier ":" "witness" TypeRef` | 406 |
| `RepeatedParameter` | `Identifier "..." TypeAnnotation` | 407 |
| `NamedRestParameter` | `Identifier "***" TypeAnnotation` | 408 |
| `StoredParameter` | `MemberVisibility? ("let" \| "var") Identifier TypeAnnotation?` | 412 |
| `ClassDecl` | `OrdinaryClassDecl \| DataClassDecl` | 416 |
| `OrdinaryClassDecl` | `TopLevelVisibility? ClassFlavor? ClassModifierSequence? "class" Identifier TypeParameterList? ParameterList? InheritanceClause? WhereClause? CleanupBudgetClause? ClassBody` | 417 |
| `DataClassDecl` | `TopLevelVisibility? "data" "class" Identifier TypeParameterList? ParameterList? InheritanceClause? WhereClause? CleanupBudgetClause? ClassBody?` | 420 |
| `ClassFlavor` | `"value" \| "resource"` | 422 |
| `ClassModifierSequence` | `"final" \| "open" \| "abstract" \| "sealed" \| "abstract" "sealed"` | 423 |
| `InheritanceClause` | `":" TypeRef` | 424 |
| `ClassBody` | `"{" MemberDecl* "}"` | 425 |
| `MemberDecl` | `FieldDecl \| MemberFunctionDecl \| ConstructorDecl \| CleanupDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| ForwardDecl` | 427 |
| `FieldDecl` | `MemberVisibility? ("let" \| "var") Identifier TypeAnnotation? Initializer? StatementBoundary` | 436 |
| `TypeSideFieldDecl` | `MemberVisibility? "let" "::" Identifier TypeAnnotation? Initializer? StatementBoundary` | 438 |
| `AccessorPropertyDecl` | `("let" \| "var") Identifier TypeAnnotation ":=" AccessorSpec` | 440 |
| `AccessorSpec` | `AccessorDecl \| "{" AccessorDecl+ "}"` | 441 |
| `AccessorDecl` | `MemberVisibility? "get" Block \| MemberVisibility? "set" "(" Identifier ")" Block` | 442 |
| `ForwardDecl` | `MemberVisibility? "forward" ForwardMemberSpec "to" Expr StatementBoundary` | 444 |
| `ForwardMemberSpec` | `Identifier \| "{" Identifier ("," Identifier)* ","? "}"` | 445 |
| `TraitDecl` | `TopLevelVisibility? "trait" Identifier TypeParameterList? SuperTraitClause? TraitBody?` | 449 |
| `SuperTraitClause` | `"requires" TraitReferenceList` | 450 |
| `TraitBody` | `"{" TraitItem* "}"` | 451 |
| `TraitItem` | `TraitMethodDecl \| AssociatedRequirementDecl \| LawDecl` | 452 |
| `TraitMethodDecl` | `MemberVisibility? DefIntroducer Identifier TraitWitnessMarker TypeParameterList? ParameterList TraitFunctionTail` | 454 |
| `AssociatedRequirementDecl` | `AssociatedTypeRequirementDecl \| AssociatedValueRequirementDecl \| AssociatedFunctionRequirementDecl` | 456 |
| `AssociatedTypeRequirementDecl` | `"type" Identifier AssociatedTypeConstraintList? StatementBoundary` | 459 |
| `AssociatedValueRequirementDecl` | `"let" "::" Identifier TypeAnnotation StatementBoundary` | 460 |
| `AssociatedFunctionRequirementDecl` | `"def" "::" Identifier ParameterList ReturnClause? ThrowsClause? EffectsClause? StatementBoundary` | 461 |
| `ConformanceDecl` | `TopLevelVisibility? "conformance" TypeRef "conforms" QualifiedTypeReference NameAliasClause? ConformanceViaClause? WhereClause? ConformanceBody` | 464 |
| `ConformanceViaClause` | `"via" QualifiedPath` | 466 |
| `ConformanceBody` | `"{" ConformanceItem* "}"` | 467 |
| `ConformanceMethodDecl` | `MemberVisibility? DefIntroducer Identifier TraitWitnessMarker FunctionRest` | 468 |
| `ConformanceItem` | `ConformanceMethodDecl \| TypeSideMemberFunctionDecl \| AssociatedRequirementBinding \| ExtensionDelegationDecl \| LawDecl` | 469 |
| `AssociatedRequirementBinding` | `"type" Identifier "=" TypeRef StatementBoundary \| "let" "::" Identifier "=" Expr StatementBoundary` | 474 |
| `ExtensionDelegationDecl` | `"delegate" Identifier "to" QualifiedExtensionSelector StatementBoundary` | 476 |
| `ExtensionSetDecl` | `TopLevelVisibility? "extension" TypeRef "as" Identifier ExtensionSetBody` | 480 |
| `ExtensionSetBody` | `"{" ExtensionSetItem* "}"` | 481 |
| `ExtensionSetItem` | `ExtensionSetFunctionDecl \| TypeSideMemberFunctionDecl` | 482 |
| `ExtensionSetFunctionDecl` | `MemberVisibility? "def" Identifier ParameterList? ReturnClause? ThrowsClause? EffectsClause? WhereClause? FunctionBody` | 483 |
| `ExtensionPackDecl` | `"extension" "pack" QualifiedPath ExtensionPackBody` | 485 |
| `ExtensionPackBody` | `"{" UseExportDecl* "}"` | 486 |
| `EnumDecl` | `TopLevelVisibility? "enum" EnumOrderRole? Identifier TypeParameterList? EnumBody` | 490 |
| `EnumOrderRole` | `"#" ("increasing" \| "decreasing")` | 491 |
| `EnumBody` | `"{" (EnumCommaCaseSequence \| EnumLayoutBody)? "}"` | 492 |
| `EnumCommaCaseSequence` | `EnumCaseCore ("," EnumCaseCore)+ ","?` | 493 |
| `EnumLayoutBody` | `EnumCaseDecl* EnumMemberDecl*` | 494 |
| `EnumCaseDecl` | `EnumCaseCore StatementBoundary?` | 495 |
| `EnumCaseCore` | `Identifier EnumCasePayload? EnumCaseDisplayMapping?` | 496 |
| `EnumCasePayload` | `"(" EnumCaseFieldList? ")"` | 497 |
| `EnumCaseFieldList` | `EnumCaseField ("," EnumCaseField)* ","?` | 498 |
| `EnumCaseField` | `Identifier TypeAnnotation \| TypeRef` | 499 |
| `EnumMemberDecl` | `MemberFunctionDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| EnumVariantSubsetAliasDecl` | 500 |
| `EnumCaseDisplayMapping` | `"~>" RestrictedEnumDisplayTemplate` | 505 |
| `RestrictedEnumDisplayTemplate` | `PLAIN_STRING_LITERAL \| MULTILINE_STRING_LITERAL \| InterpolatedString` | 506 |
| `EnumVariantSubsetAliasDecl` | `"+" "type" Identifier "=" EnumVariantSubsetRhs StatementBoundary?` | 509 |
| `EnumVariantSubsetRhs` | `Identifier ("\|" Identifier)*` | 511 |
| `SchemaDecl` | `TopLevelVisibility? "schema" Identifier TypeParameterList? SchemaBody` | 515 |
| `SchemaBody` | `"{" SchemaFieldSequence? "}"` | 516 |
| `SchemaFieldSequence` | `CommaSchemaFields \| LayoutSchemaFields` | 517 |
| `CommaSchemaFields` | `SchemaFieldDecl ("," SchemaFieldDecl)* ","?` | 518 |
| `LayoutSchemaFields` | `LineBreakBoundary LayoutSchemaFieldDecl (LineBreakBoundary LayoutSchemaFieldDecl)* LineBreakBoundary?` | 519 |
| `SchemaFieldDecl` | `Identifier TypeAnnotation Initializer? SchemaConstraint* StatementBoundary?` | 520 |
| `LayoutSchemaFieldDecl` | `Identifier TypeAnnotation Initializer? SchemaConstraint*` | 521 |
| `SchemaConstraint` | `"where" Expr` | 522 |
| `TypeAliasDecl` | `TopLevelVisibility? "type" Identifier TypeParameterList? "=" TypeAliasRhs StatementBoundary` | 524 |
| `TypeAliasRhs` | `TypeRef RefinementClause? \| StaticRangeType` | 525 |
| `StaticRangeType` | `StaticIntLiteral ".." StaticIntLiteral` | 526 |
| `TopLevelBindingDecl` | `TopLevelVisibility? ("let" \| "var") Identifier TypeAnnotation? "=" Expr StatementBoundary` | 528 |
| `NamedEffectCapabilityDecl` | `TopLevelVisibility? "capability" Identifier "for" EffectRow StatementBoundary` | 529 |
| `ActorDecl` | `TopLevelVisibility? "actor" MailboxClause? Identifier ActorBody` | 533 |
| `MailboxClause` | `HashTag "(" "capacity" ":" StaticIntLiteral ")"` | 534 |
| `ActorBody` | `"{" ActorItem* "}"` | 535 |
| `ActorItem` | `ActorOnDecl \| ActorRequestDecl \| MemberDecl` | 536 |
| `ActorOnDecl` | `MemberVisibility? "on" Identifier ParameterList? ThrowsClause? EffectsClause? FunctionBody` | 537 |
| `ActorRequestDecl` | `MemberVisibility? "request" Identifier ParameterList? ReturnClause ThrowsClause? EffectsClause? FunctionBody` | 538 |
| `ActorProtocolDecl` | `TopLevelVisibility? "protocol" Identifier ActorProtocolBody` | 540 |
| `ActorProtocolBody` | `"{" ActorProtocolItem* "}"` | 541 |
| `ActorProtocolItem` | `ActorProtocolSendRequirement \| ActorProtocolRequestRequirement` | 542 |
| `ActorProtocolSendRequirement` | `"send" Identifier ParameterList? ThrowsClause? EffectsClause? StatementBoundary` | 543 |
| `ActorProtocolRequestRequirement` | `"request" Identifier ParameterList? ReturnClause ThrowsClause? EffectsClause? StatementBoundary` | 544 |
| `TypestateResourceDecl` | `TopLevelVisibility? "typestate" Identifier TypeParameterList? TypestateBody` | 548 |
| `TypestateBody` | `"{" TypestateTransitionDecl* "}"` | 549 |
| `TypestateTransitionDecl` | `Identifier "->" Identifier FunctionBody?` | 550 |
| `UnitCatalogDecl` | `TopLevelVisibility? "unit" "catalog" Identifier UnitCatalogBody` | 552 |
| `UnitCatalogBody` | `"{" UnitCatalogEntry* "}"` | 553 |
| `UnitCatalogEntry` | `ExactRatioUnitConversionDecl \| Identifier "=" UnitExpr StatementBoundary` | 554 |
| `ExactRatioUnitConversionDecl` | `"unit" Identifier "equalsRatio" MeasureLiteralExpr "/" StaticIntLiteral StatementBoundary` | 555 |
| `ModuleInterfaceDecl` | `ModuleSignatureDecl \| OpaqueModuleFacadeDecl` | 557 |
| `ModuleSignatureDecl` | `TopLevelVisibility? "module" "signature" QualifiedPath ModuleInterfaceBody` | 558 |
| `OpaqueModuleFacadeDecl` | `TopLevelVisibility? "opaque" "module" QualifiedPath ModuleInterfaceBody` | 559 |
| `ModuleInterfaceBody` | `"{" ModuleInterfaceItem* "}"` | 560 |
| `ModuleInterfaceItem` | `ExportDecl \| UseExportDecl \| OpaqueModuleFacadeDecl` | 561 |
| `CleanupBudgetClause` | `"cleanup" "budget" "{" CleanupBudgetItem* "}"` | 565 |
| `CleanupBudgetItem` | `EffectsBudget \| ErrorsBudget` | 566 |
| `EffectsBudget` | `"effects" "{" IdentifierList? "}"` | 567 |
| `ErrorsBudget` | `"errors" TypeRef` | 568 |
| `BitfieldDecl` | `TopLevelVisibility? BitfieldIntroducer Identifier BitfieldBackingClause BitfieldOrderClause BitfieldBody` | 572 |
| `BitfieldIntroducer` | `"bitfield" HashTag?` | 574 |
| `BitfieldBackingClause` | `"backing" TypeRef` | 575 |
| `BitfieldOrderClause` | `"order" "::" "lsb0"` | 576 |
| `BitfieldBody` | `"{" BitfieldLayoutSection BitfieldMemberDecl* "}"` | 577 |
| `BitfieldLayoutSection` | `BitfieldSlotDecl+ \| FlagSlotDecl+` | 578 |
| `BitfieldSlotDecl` | `BitfieldNamedSlot StatementBoundary \| BitfieldReservedSlot StatementBoundary` | 579 |
| `FlagSlotDecl` | `FlagNamedSlot StatementBoundary \| BitfieldReservedSlot StatementBoundary` | 580 |
| `BitfieldNamedSlot` | `MemberVisibility? Identifier ":" StaticIntLiteral BitfieldDefault?` | 581 |
| `BitfieldReservedSlot` | `"_" ":" StaticIntLiteral` | 582 |
| `FlagNamedSlot` | `MemberVisibility? Identifier` | 583 |
| `BitfieldDefault` | `"=" Literal` | 584 |
| `BitfieldMemberDecl` | `MemberFunctionDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| LawDecl` | 585 |
| `TypeRef` | `PrattType` | 597 |
| `NonFunctionTypeRef` | `PrattNonFunctionType` | 598 |
| `TypePrimary` | `QualifiedTypeReference \| FacetType \| ParenTypeSyntax \| SharpShapeType \| ExistentialType \| OpaqueType \| TypeofType \| AssociatedProjection` | 601 |
| `TypePrefixParselet` | `OwnershipQualifier` | 609 |
| `TypePostfixParselet` | `"?"` | 610 |
| `TypeInfixOperator` | `"&" \| "\|"` | 611 |
| `QualifiedTypeReference` | `QualifiedPath TypeArgumentList?` | 613 |
| `FacetType` | `"Facet" "<" "borrow" "any" QualifiedTypeReference AssociatedTypeConstraintList? ">"` | 615 |
| `OwnershipQualifier` | `"owned" \| "borrowed" \| "mut" \| "inout"` | 616 |
| `ParenTypeSyntax` | `HashTag* "(" ParenTypeItemList? ")" FunctionTypeTail?` | 620 |
| `ParenTypeItemList` | `ParenTypeItem ("," ParenTypeItem)* ","?` | 621 |
| `ParenTypeItem` | `TypeRef \| TypeRef "..." \| TypeRef "***"` | 622 |
| `FunctionTypeTail` | `"->" ReturnTypeSurface ThrowsClause? EffectsClause?` | 623 |
| `SharpShapeType` | `"#" StaticDimensionList "[" TypeRef "]"` | 625 |
| `StaticDimensionList` | `StaticIntLiteral ("," StaticIntLiteral)*` | 626 |
| `ExistentialType` | `"any" QualifiedTypeReference AssociatedTypeConstraintList?` | 628 |
| `OpaqueType` | `"some" QualifiedTypeReference AssociatedTypeConstraintList?` | 629 |
| `TypeofType` | `"typeof" TypeofStaticSampleOperand` | 630 |
| `AssociatedProjection` | `"<" TypeRef "as" QualifiedTypeReference ">" "::" Identifier` | 631 |
| `TypeofStaticSampleOperand` | `Literal \| ListLiteral \| StaticPrefixedCollectionSample \| NumericArrayLiteral \| MeasureLiteralExpr` | 634 |
| `StaticPrefixedCollectionSample` | `MapLiteral \| SetLiteral \| MutListLiteral` | 639 |
| `PrattType` | `TYPE_PRATT_ENTRY` | 642 |
| `PrattNonFunctionType` | `NON_FUNCTION_TYPE_PRATT_ENTRY` | 643 |
| `Pattern` | `OrPattern` | 651 |
| `OrPattern` | `AliasPattern ("\|" AliasPattern)*` | 652 |
| `AliasPattern` | `MovePattern ("as" Identifier)?` | 653 |
| `MovePattern` | `"move"? PatternPrimary` | 654 |
| `PatternPrimary` | `TypedBindingPattern \| Identifier \| PinPattern \| RangePattern \| RelationalPattern \| TuplePattern \| RecordPattern \| ListPattern \| MapPattern \| VariantPattern \| NominalPattern \| "_" \| UnitSyntax \| Literal \| ParenthesizedPattern` | 656 |
| `TypedBindingPattern` | `Identifier ":" TypeRef` | 672 |
| `ParenthesizedPattern` | `"(" Pattern ")"` | 673 |
| `PinPattern` | `"^" StablePatternValue` | 674 |
| `StablePatternValue` | `Identifier \| QualifiedStaticExpr \| Literal` | 675 |
| `RangePattern` | `PatternBound (".." \| "..<") PatternBound` | 676 |
| `RelationalPattern` | `("<" \| "<=" \| ">" \| ">=") PatternBound` | 677 |
| `PatternBound` | `Literal \| PinPattern` | 678 |
| `TuplePattern` | `"(" TuplePatternItems ")"` | 682 |
| `TuplePatternItems` | `Pattern "," \| Pattern "," Pattern ("," Pattern)* ","?` | 683 |
| `BindingPattern` | `BindingOrPattern TypeAnnotation?` | 695 |
| `BindingOrPattern` | `BindingAliasPattern ("\|" BindingAliasPattern)*` | 696 |
| `BindingAliasPattern` | `BindingMovePattern ("as" Identifier)?` | 697 |
| `BindingMovePattern` | `"move"? BindingPatternPrimary` | 698 |
| `BindingPatternPrimary` | `Identifier \| PinPattern \| RangePattern \| RelationalPattern \| TuplePattern \| RecordPattern \| ListPattern \| MapPattern \| VariantPattern \| NominalPattern \| "_" \| UnitSyntax \| Literal \| ParenthesizedPattern` | 699 |
| `RecordPattern` | `"${" RecordPatternEntries? "}"` | 718 |
| `RecordPatternEntries` | `RecordPatternEntry (PatternEntrySeparator RecordPatternEntry)* PatternEntrySeparator?` | 719 |
| `RecordPatternEntry` | `Identifier \| RecordDestination ":" Identifier \| RecordRestPattern` | 721 |
| `RecordDestination` | `Pattern` | 722 |
| `RecordRestPattern` | `".." RestBinder` | 723 |
| `MapPattern` | `"#" "map" "{" MapPatternEntries? "}"` | 725 |
| `MapPatternEntries` | `MapPatternEntry (PatternEntrySeparator MapPatternEntry)* PatternEntrySeparator?` | 726 |
| `MapPatternEntry` | `MapDestination ":" MapKeyPattern \| MapRestPattern` | 728 |
| `MapDestination` | `Pattern` | 729 |
| `MapKeyPattern` | `Literal \| PinPattern` | 730 |
| `MapRestPattern` | `".." RestBinder` | 731 |
| `PatternEntrySeparator` | `"," LineBreakBoundary? \| LineBreakBoundary` | 732 |
| `ListPattern` | `"[" ListPatternBody? "]"` | 738 |
| `ListPatternBody` | `IgnoredAllListRest \| ExactListPattern \| PrefixRestListPattern \| SuffixRestListPattern \| MiddleRestListPattern` | 739 |
| `ExactListPattern` | `Pattern ("," Pattern)* ","?` | 744 |
| `PrefixRestListPattern` | `PrefixListRest "," Pattern ("," Pattern)* ","?` | 745 |
| `SuffixRestListPattern` | `Pattern ("," Pattern)* "," SuffixListRest ","?` | 746 |
| `MiddleRestListPattern` | `Pattern ("," Pattern)* "," MiddleListRest "," Pattern ("," Pattern)* ","?` | 747 |
| `PrefixListRest` | `RestBinder ".."` | 749 |
| `SuffixListRest` | `".." RestBinder` | 750 |
| `MiddleListRest` | `".." RestBinder ".."` | 751 |
| `IgnoredAllListRest` | `".." "_" ","?` | 752 |
| `RestBinder` | `Identifier \| "_"` | 753 |
| `VariantPattern` | `VariantQualifier Identifier VariantPatternPayload?` | 755 |
| `VariantQualifier` | `TypeRef "::" \| "::"` | 756 |
| `VariantPatternPayload` | `VariantPositionalPatternPayload \| RecordPattern` | 757 |
| `VariantPositionalPatternPayload` | `"(" PatternList? ")"` | 758 |
| `NominalPattern` | `TypeRef RecordPattern` | 763 |
| `Stmt` | `ForLoop \| WhileLoop \| RepeatLoop \| AsyncForLoop \| TaskGroupStmt \| MatchStatement \| IfStmt \| LocalBindingStmt \| AssertiveBindingStmt \| PatternAssignmentStmt \| ParallelAssignmentStmt \| ControlTransferStmt \| TryStmt \| DeferStmt \| ScopedUseStmt \| ExprStmt \| ScopedImportStmt` | 771 |
| `ExprStmt` | `Expr StatementBoundary` | 789 |
| `Block` | `"{" BlockPrologue? BlockSequence "}"` | 791 |
| `BlockPrologue` | `(UseDecl \| ImportDecl)+` | 792 |
| `BlockSequence` | `BlockItem* BlockFinalItem?` | 793 |
| `BlockItem` | `LocalFunctionDecl \| Stmt` | 794 |
| `BlockFinalItem` | `ControlTransfer \| BindingCore \| Expr` | 797 |
| `ValueBody` | `SingleExpressionValueBody \| ExplicitRetValueBody` | 800 |
| `SingleExpressionValueBody` | `"{" ReturnValueSurface "}"` | 801 |
| `ExplicitRetValueBody` | `"{" BlockItem* RetTransfer "}"` | 802 |
| `RetTransfer` | `"ret" ReturnValueSurface? GuardClause?` | 803 |
| `BindingCore` | `("let" \| "var") BindingHead "=" BindingValueSurface` | 808 |
| `BindingHead` | `BindingPattern \| BareTupleBindingSurface` | 809 |
| `BareTupleBindingSurface` | `BindingPattern "," BindingPattern ("," BindingPattern)*` | 810 |
| `BindingValueSurface` | `Expr \| BareTupleValueSurface` | 811 |
| `ReturnValueSurface` | `Expr \| BareTupleValueSurface` | 812 |
| `BareTupleValueSurface` | `Expr "," Expr ("," Expr)*` | 813 |
| `LocalBindingStmt` | `BindingCore StatementBoundary \| RightwardLocalBindingSurface \| LazyBindingStmt \| GuardedBindingStmt` | 814 |
| `LazyBindingStmt` | `"let" HashTag Identifier TypeAnnotation? "=" Expr StatementBoundary` | 815 |
| `GuardedBindingStmt` | `("let" \| "var") BindingPattern "=" Expr "else" GuardedBindingFailure StatementBoundary?` | 816 |
| `AssertiveBindingStmt` | `("let" \| "var") "!" BindingPattern "=" Expr StatementBoundary` | 817 |
| `GuardedBindingFailure` | `GuardedBindingExit \| Pattern "=>" GuardedBindingExit` | 819 |
| `GuardedBindingExit` | `GuardedReturnExit \| GuardedThrowExit \| GuardedBreakExit \| GuardedContinueExit` | 820 |
| `GuardedReturnExit` | `"return" Expr?` | 821 |
| `GuardedThrowExit` | `"throw" Expr` | 822 |
| `GuardedBreakExit` | `("break")+ Expr?` | 823 |
| `GuardedContinueExit` | `("break")* "continue"` | 824 |
| `ControlTransferStmt` | `ControlTransfer StatementBoundary` | 827 |
| `ControlTransfer` | `ReturnTransfer \| ThrowTransfer \| BreakTransfer \| ContinueTransfer \| YieldTransfer` | 828 |
| `ReturnTransfer` | `"return" ReturnValueSurface? GuardClause?` | 829 |
| `ThrowTransfer` | `"throw" Expr GuardClause?` | 830 |
| `BreakTransfer` | `("break")+ Expr? GuardClause?` | 831 |
| `ContinueTransfer` | `("break")* "continue" GuardClause?` | 832 |
| `YieldTransfer` | `"yield" Expr? (GuardClause \| YieldResponseBinding)?` | 833 |
| `YieldResponseBinding` | `"->" DollarLocalBinding` | 834 |
| `DollarLocalBinding` | `"$" Identifier TypeAnnotation? \| "$$" Identifier TypeAnnotation?` | 835 |
| `GuardClause` | `PositiveGuard \| NegativeGuard` | 837 |
| `PositiveGuard` | `"if" Expr` | 838 |
| `NegativeGuard` | `"!" "if" Expr` | 839 |
| `IfStmt` | `"if" PatternConditionChain Block ("else" (IfStmt \| Block))?` | 841 |
| `PatternConditionChain` | `PatternControlCondition ("and" "then" PatternControlCondition)*` | 844 |
| `PatternControlCondition` | `Expr \| "let" Pattern "=" Expr` | 846 |
| `ForLoop` | `"for" ("let" Pattern \| Pattern) "in" Expr GuardClause? Block MatchStatement?` | 850 |
| `WhileLoop` | `"while" PatternConditionChain Block MatchStatement?` | 851 |
| `RepeatLoop` | `"repeat" Block "while" Expr MatchStatement?` | 852 |
| `AsyncForLoop` | `"for" "await" ("let" Pattern \| Pattern) "in" Expr GuardClause? Block` | 853 |
| `MatchStatement` | `"match" MatchCore` | 855 |
| `MatchCore` | `MatchSubjectSlot MatchBody` | 856 |
| `MatchSubjectSlot` | `MATCH_SUBJECT_BY_INPUT_SUPPLY_POLICY` | 857 |
| `MatchBody` | `"{" LineBreakBoundary? MatchArmSequence "}"` | 858 |
| `MatchArmSequence` | `MatchArm (MatchArmSeparator MatchArm)* MatchArmSeparator?` | 859 |
| `MatchArm` | `MatchHead GuardClause? "=>" MatchArmBodySlot` | 860 |
| `MatchHead` | `Pattern \| "otherwise"` | 861 |
| `MatchArmSeparator` | `MATCH_ARM_SEPARATOR_BY_CONTEXT` | 862 |
| `MatchArmBodySlot` | `MATCH_ARM_BODY_BY_CONTEXT` | 863 |
| `TryStmt` | `"try" Block (CatchClause+ FinallyClause? \| FinallyClause)` | 867 |
| `CatchClause` | `"catch" Pattern? GuardClause? Block` | 868 |
| `ValueCatchClause` | `"catch" Pattern? GuardClause? ValueBody` | 869 |
| `FinallyClause` | `"finally" Block` | 870 |
| `DeferStmt` | `"defer" DeferredCleanupInvocation StatementBoundary` | 872 |
| `DeferredCleanupInvocation` | `DeferredDirectCall \| DeferredMessageCall` | 875 |
| `DeferredDirectCall` | `DeferredReceiver ArgumentList` | 876 |
| `DeferredMessageCall` | `DeferredReceiver "~" MessageSelector TildeArgumentSequence?` | 877 |
| `DeferredReceiver` | `DeferredPrimary DeferTargetSuffix*` | 878 |
| `DeferredPrimary` | `Identifier \| QualifiedStaticExpr` | 879 |
| `DeferTargetSuffix` | `IndexSuffix \| MemberSuffix` | 880 |
| `RightwardLocalBindingSurface` | `Expr "->" DollarLocalBinding StatementBoundary` | 884 |
| `PatternAssignmentStmt` | `AssigneePattern "=" Expr StatementBoundary` | 888 |
| `AssigneePattern` | `AssigneeTuplePattern \| AssigneeListPattern \| AssigneeRecordPattern \| AssigneeNominalPattern` | 889 |
| `AssigneePrimary` | `Identifier \| "_"` | 893 |
| `AssigneeTuplePattern` | `"(" AssigneeTupleItems ")"` | 894 |
| `AssigneeTupleItems` | `AssigneePatternItem "," \| AssigneePatternItem "," AssigneePatternItem ("," AssigneePatternItem)* ","?` | 895 |
| `AssigneePatternItem` | `AssigneePrimary \| AssigneeTuplePattern \| AssigneeListPattern \| AssigneeRecordPattern` | 898 |
| `AssigneeListPattern` | `"[" AssigneeListBody? "]"` | 902 |
| `AssigneeListBody` | `AssigneeIgnoredAllRest \| AssigneeExactList \| AssigneePrefixRestList \| AssigneeSuffixRestList \| AssigneeMiddleRestList` | 903 |
| `AssigneeExactList` | `AssigneePatternItem ("," AssigneePatternItem)* ","?` | 908 |
| `AssigneePrefixRestList` | `Identifier ".." "," AssigneeExactList` | 909 |
| `AssigneeSuffixRestList` | `AssigneeExactList "," ".." Identifier ","?` | 910 |
| `AssigneeMiddleRestList` | `AssigneeExactList "," ".." Identifier ".." "," AssigneeExactList` | 911 |
| `AssigneeIgnoredAllRest` | `".." "_" ","?` | 913 |
| `AssigneeRestPattern` | `".." ("_" \| Identifier)` | 914 |
| `AssigneeRecordPattern` | `"${" AssigneeRecordEntries? "}"` | 915 |
| `AssigneeRecordEntries` | `AssigneeRecordEntry (PatternEntrySeparator AssigneeRecordEntry)* PatternEntrySeparator?` | 916 |
| `AssigneeRecordEntry` | `Identifier \| AssigneePrimary ":" Identifier \| AssigneeRestPattern` | 919 |
| `AssigneeNominalPattern` | `TypeRef AssigneeRecordPattern` | 920 |
| `ParallelAssignmentStmt` | `BareTuplePlaceSurface "=" AssignmentValueSurface StatementBoundary` | 921 |
| `BareTuplePlaceSurface` | `Identifier "," Identifier ("," Identifier)*` | 922 |
| `AssignmentValueSurface` | `Expr \| BareTupleValueSurface` | 923 |
| `ScopedUseStmt` | `"use" ScopedPathList "in" Block` | 924 |
| `ScopedImportStmt` | `"import" ScopedPathList "in" Block` | 925 |
| `ScopedPathList` | `QualifiedPath ("," QualifiedPath)*` | 926 |
| `TaskGroupStmt` | `"task" "group" Identifier? Block` | 927 |
| `Expr` | `PrattExpr` | 935 |
| `PredicateExpr` | `PrattPredicateExpr` | 936 |
| `SliceIndexExpr` | `PrattSliceIndexExpr` | 937 |
| `ExpressionPrefixParselet` | `"+" \| "-" \| "not" \| "~~" \| "move" \| "borrow" \| "&" \| "await"` | 943 |
| `ExpressionPostfixParselet` | `CallSuffix \| TildeCallLed \| TupleOrdinalSuffix \| IndexSuffix \| MemberSuffix \| NumericArrayTransposeSuffix \| ConstructorCallSuffix \| NamedConstructorCallSuffix \| PrototypeDerivationSuffix \| CastSuffix` | 945 |
| `PrimaryExpr` | `Literal \| Identifier \| ImplicitAtExpr \| ParenExprSyntax \| ListLiteral \| BoundedListLiteral \| ComprehensionExpr \| MaterializationBody \| TypedMaterializationExpr \| MapLiteral \| SetLiteral \| MutListLiteral \| MapComprehensionExpr \| SetComprehensionExpr \| NumericArrayLiteral \| MeasureLiteralExpr \| QualifiedStaticExpr \| ExpectedVariantExpr \| AtControlExpr \| MatchExpr \| ClosureExpr \| GeneratorExpr \| SpawnExpr \| StructuredTaskScope \| UnsafeBlockExpr \| FacetExpr` | 956 |
| `ParenExprSyntax` | `"(" ParenExprContent? ")"` | 984 |
| `ParenExprContent` | `Expr ParenExprTail?` | 985 |
| `ParenExprTail` | `"," \| "," Expr ("," Expr)* ","?` | 986 |
| `ImplicitAtExpr` | `"@"` | 987 |
| `ExpectedVariantExpr` | `"::" Identifier` | 988 |
| `CallSuffix` | `ArgumentList TrailingClosureGroup? \| AtomicCallArgument TrailingClosureGroup` | 992 |
| `ArgumentList` | `"(" ")" \| "(" CommaArgumentSequence ")" \| "(" LayoutArgumentSequence ")"` | 995 |
| `CommaArgumentSequence` | `Argument ("," Argument)* ","?` | 998 |
| `LayoutArgumentSequence` | `LineBreakBoundary NamedLayoutArgument LineBreakBoundary NamedLayoutArgument (LineBreakBoundary NamedLayoutArgument)* LineBreakBoundary?` | 1000 |
| `NamedLayoutArgument` | `NamedArgument \| NamedUnfoldArgument` | 1002 |
| `Argument` | `ContextArgument \| WitnessArgument \| NamedArgument \| PositionalUnfoldArgument \| NamedUnfoldArgument \| Expr` | 1003 |
| `ContextArgument` | `"context" Expr` | 1009 |
| `WitnessArgument` | `"using" WitnessArgumentValue` | 1010 |
| `WitnessArgumentValue` | `Identifier \| ConformanceEvidenceSelector \| NamedConformanceEvidenceSelector` | 1011 |
| `NamedArgument` | `Identifier ":" Expr` | 1012 |
| `PositionalUnfoldArgument` | `"*" Expr` | 1013 |
| `NamedUnfoldArgument` | `"**" Expr` | 1014 |
| `AtomicCallArgument` | `Literal \| Identifier \| QualifiedStaticExpr \| ExpectedVariantExpr` | 1015 |
| `TrailingClosureGroup` | `TrailingClosureArgument+` | 1019 |
| `TrailingClosureArgument` | `ClosureExpr \| Identifier ":" ClosureExpr` | 1020 |
| `IndexSuffix` | `"[" SliceAxisList "]"` | 1024 |
| `SliceAxisList` | `SliceAxis (";" SliceAxis)*` | 1025 |
| `SliceAxis` | `SliceRange \| SliceIndexExpr \| AxisWildcard` | 1026 |
| `SliceRange` | `SliceBound (".." \| "..<") SliceBound` | 1029 |
| `SliceBound` | `SliceIndexExpr \| "^" \| "$" \| "^" OffsetExpr \| "$" OffsetExpr` | 1030 |
| `OffsetExpr` | `("+" \| "-") NumericLiteral` | 1031 |
| `AxisWildcard` | `"*"` | 1032 |
| `TupleOrdinalSuffix` | `"." StaticIntLiteral` | 1034 |
| `MemberSuffix` | `"." Identifier \| "." "\\\\" NAME_TOKEN` | 1035 |
| `TildeCallLed` | `TildeCallToken MessageSelector TildeArgumentSequence? TrailingClosureGroup?` | 1041 |
| `TildeCallToken` | `"~" \| ":~"` | 1043 |
| `MessageSelector` | `Identifier \| QualifiedMessageSelector` | 1044 |
| `QualifiedMessageSelector` | `TypeRef "::" Identifier ("::" Identifier)?` | 1045 |
| `QualifiedExtensionSelector` | `TypeRef "::" Identifier "::" Identifier` | 1046 |
| `TildeArgumentSequence` | `TildeArgument ("," TildeArgument)*` | 1047 |
| `TildeArgument` | `ContextArgument \| WitnessArgument \| NamedArgument \| PositionalUnfoldArgument \| NamedUnfoldArgument \| Expr` | 1048 |
| `NumericArrayTransposeSuffix` | `"^"` | 1055 |
| `ConstructorCallSuffix` | `"!" ArgumentList` | 1056 |
| `NamedConstructorCallSuffix` | `"!" Identifier ArgumentList` | 1057 |
| `PrototypeDerivationSuffix` | `("!" \| "!!") DerivationBody` | 1058 |
| `DerivationBody` | `"{" MaterializationEntryList? "}"` | 1059 |
| `CastSuffix` | `"as" "?" TypeRef \| "as" "!" TypeRef` | 1061 |
| `QualifiedStaticExpr` | `StaticQualifier "::" Identifier \| TraitQualifiedAssociatedSelector` | 1063 |
| `StaticQualifier` | `QualifiedTypeReference \| AssociatedProjection` | 1065 |
| `TraitQualifiedAssociatedSelector` | `"<" TypeRef "as" QualifiedTypeReference ">" "::" Identifier` | 1066 |
| `AtControlExpr` | `AtIfExpr \| AtTryExpr \| AtScopeExpr` | 1072 |
| `AtIfExpr` | `"@" "if" Expr ValueBody "else" ValueBody` | 1074 |
| `AtTryExpr` | `"@" "try" ValueBody (ValueCatchClause+ FinallyClause? \| FinallyClause)` | 1075 |
| `AtScopeExpr` | `"@" "scope" ScopeModifier* ValueBody` | 1076 |
| `ScopeModifier` | `"isolated" \| "cancellable" \| "shielded"` | 1077 |
| `MatchExpr` | `"@" "match" MatchCore` | 1079 |
| `ClosureExpr` | `CaptureList? HashTag* "{" ClosureContent "}"` | 1083 |
| `ClosureContent` | `ExplicitLambdaContent \| LambdaBody?` | 1084 |
| `ExplicitLambdaContent` | `LambdaParameterList? "=>" LambdaBody` | 1085 |
| `LambdaParameterList` | `LambdaParameter ("," LambdaParameter)* ","?` | 1086 |
| `LambdaParameter` | `ParameterMode? LambdaParameterPattern TypeAnnotation?` | 1087 |
| `LambdaParameterPattern` | `Identifier \| IrrefutableParameterPattern` | 1088 |
| `LambdaBody` | `ReturnValueSurface \| LineBreakBoundary LambdaBlockContent` | 1089 |
| `LambdaBlockContent` | `BlockItem* LambdaFinalItem?` | 1090 |
| `LambdaFinalItem` | `RetTransfer \| Expr` | 1091 |
| `CaptureList` | `"[" CaptureItemList? "]"` | 1093 |
| `CaptureItemList` | `CaptureItem ("," CaptureItem)* ","?` | 1094 |
| `CaptureItem` | `("let" \| "var") Identifier "=" Expr \| CaptureMode Identifier \| Identifier` | 1095 |
| `CaptureMode` | `"borrow" \| "inout" \| "move" \| "clone" \| "deep" \| "copy" \| "once"` | 1098 |
| `GeneratorExpr` | `CaptureList? GeneratorCore` | 1111 |
| `GeneratorCore` | `"@" "for" Pattern "in" Expr Block \| "@" "while" Expr Block \| "@" "repeat" Block "while" Expr` | 1112 |
| `SpawnExpr` | `"spawn" TaskBody` | 1116 |
| `TaskBody` | `"{" "=>" TaskBodySequence "}" \| "async" "{" "=>" TaskBodySequence "}"` | 1117 |
| `TaskBodySequence` | `LineBreakBoundary? BlockSequence` | 1119 |
| `StructuredTaskScope` | `"task" "scope" Block` | 1120 |
| `UnsafeBlockExpr` | `"unsafe" Block` | 1121 |
| `FacetExpr` | `"facet" "[" "borrow" Expr "as" QualifiedTypeReference AssociatedTypeConstraintList? "]"` | 1124 |
| `ConformanceEvidenceSelector` | `"conformance" "(" TypeRef "conforms" QualifiedTypeReference ")"` | 1126 |
| `NamedConformanceEvidenceSelector` | `ConformanceEvidenceSelector "::" Identifier` | 1127 |
| `PrattExpr` | `EXPRESSION_PRATT_ENTRY` | 1130 |
| `PrattPredicateExpr` | `PREDICATE_PRATT_ENTRY` | 1131 |
| `PrattSliceIndexExpr` | `SLICE_INDEX_PRATT_ENTRY` | 1132 |
| `Literal` | `BoolLiteral \| NumericLiteral \| ImaginaryLiteralExpr \| RationalLiteralExpr \| StringLiteralExpr \| CharLiteralExpr \| BytesLiteral` | 1140 |
| `BoolLiteral` | `"true" \| "false"` | 1147 |
| `NumericLiteral` | `NUMERIC_LITERAL` | 1148 |
| `ImaginaryLiteralExpr` | `IMAGINARY_LITERAL` | 1149 |
| `RationalLiteralExpr` | `RATIONAL_LITERAL` | 1150 |
| `CharLiteralExpr` | `CHAR_LITERAL` | 1151 |
| `BytesLiteral` | `BYTES_LITERAL` | 1152 |
| `StringLiteralExpr` | `PLAIN_STRING_LITERAL \| RAW_STRING_LITERAL \| MULTILINE_STRING_LITERAL \| InterpolatedString` | 1155 |
| `InterpolatedString` | `STRING_START InterpolatedStringPart* STRING_END` | 1156 |
| `InterpolatedStringPart` | `STRING_TEXT \| STRING_ESCAPE \| InterpolationExpr \| InterpolationPath` | 1157 |
| `InterpolationExpr` | `INTERPOLATION_OPEN Expr InterpolationFormat? INTERPOLATION_CLOSE` | 1161 |
| `InterpolationFormat` | `":" INTERPOLATION_FORMAT_TEXT` | 1162 |
| `InterpolationPath` | `"$" InterpolationPathRoot InterpolationPathSelector* INTERPOLATION_BOUNDARY?` | 1167 |
| `InterpolationPathRoot` | `Identifier \| "@"` | 1168 |
| `InterpolationPathSelector` | `"." Identifier \| "." StaticIntLiteral \| "[" InterpolationIndex "]"` | 1169 |
| `InterpolationIndex` | `StaticIntLiteral \| Identifier` | 1172 |
| `ListLiteral` | `"[" ExpressionList? "]"` | 1177 |
| `BoundedListLiteral` | `"[" StaticIntLiteral ".." StaticIntLiteral ":" ExpressionList? "]"` | 1178 |
| `ComprehensionExpr` | `"[" Expr ComprehensionClause+ "]"` | 1180 |
| `TypedMaterializationExpr` | `TypeRef MaterializationBody` | 1183 |
| `MaterializationBody` | `"${" MaterializationEntryList? "}"` | 1184 |
| `MaterializationEntryList` | `MaterializationEntry (MaterializationSeparator MaterializationEntry)* MaterializationSeparator?` | 1185 |
| `MaterializationEntry` | `Identifier \| Identifier ":" Expr \| StringLiteralExpr ":" Expr \| NamedUnfoldArgument` | 1186 |
| `MaterializationSeparator` | `"," LineBreakBoundary? \| LineBreakBoundary` | 1190 |
| `MapLiteral` | `"#" "map" "{" MapEntryList? "}"` | 1193 |
| `MapEntryList` | `MapEntry (MaterializationSeparator MapEntry)* MaterializationSeparator?` | 1194 |
| `MapEntry` | `Expr ":" Expr \| NamedUnfoldArgument` | 1195 |
| `SetLiteral` | `"#" "set" "{" ExpressionList? "}"` | 1196 |
| `MutListLiteral` | `"#" "mut" "[" ExpressionList? "]"` | 1197 |
| `MapComprehensionExpr` | `"#" "map" "{" MapEntry ComprehensionClause+ "}"` | 1198 |
| `SetComprehensionExpr` | `"#" "set" "{" Expr ComprehensionClause+ "}"` | 1199 |
| `ComprehensionClause` | `ForClause \| PositiveGuard \| IfLetClause \| UnfoldClause` | 1201 |
| `ForClause` | `"for" Pattern "in" Expr` | 1202 |
| `IfLetClause` | `"if" "let" Pattern "=" Expr` | 1203 |
| `UnfoldClause` | `"for" "..." Pattern "in" Expr` | 1204 |
| `NumericArrayLiteral` | `ShapeInferredArrayLiteral \| ShapeInferredColumnVectorLiteral \| ExactShapeArrayLiteral` | 1207 |
| `ShapeInferredArrayLiteral` | `"#" "[" ExpressionList? "]"` | 1210 |
| `ShapeInferredColumnVectorLiteral` | `"#" "[" Expr (";" Expr)+ "]"` | 1211 |
| `ExactShapeArrayLiteral` | `"#" StaticDimensionList "[" ArrayInitializer? "]"` | 1212 |
| `ArrayInitializer` | `ShapedRepeatInitializer \| ShapedGeneratorInitializer \| ShapedElementSequence` | 1213 |
| `ShapedRepeatInitializer` | `"repeat" ":" Expr` | 1216 |
| `ShapedGeneratorInitializer` | `"generate" ":" Expr` | 1217 |
| `ShapedElementSequence` | `Expr (ShapedElementSeparator Expr)* ShapedElementSeparator?` | 1218 |
| `ShapedElementSeparator` | `"," \| ShapedAxisBoundary` | 1219 |
| `ShapedAxisBoundary` | `";" ";"*` | 1220 |
| `MeasureLiteralExpr` | `NumericLiteral "[" UnitExpr "]"` | 1223 |
| `UnitExpr` | `PrattUnitExpr` | 1224 |
| `UnitPrimary` | `Identifier \| QualifiedPath \| "(" UnitExpr ")"` | 1225 |
| `UnitPostfixParselet` | `"^" SignedStaticInt` | 1226 |
| `UnitInfixOperator` | `"*" \| "/"` | 1227 |
| `PrattUnitExpr` | `UNIT_PRATT_ENTRY` | 1228 |

## `PREVIEW` 프로파일 — 13개

| 문법 production | 정확한 EBNF 오른쪽 항 | 원천 줄 |
|---|---|---:|
| `DeeplusPreview` | `PreviewLibrarySourceFile \| PreviewExecutableSourceFile \| PreviewScriptSourceFile` | 1237 |
| `PreviewLibrarySourceFile` | `PreviewGate ModuleDecl? PreviewLibraryItem*` | 1238 |
| `PreviewExecutableSourceFile` | `PreviewGate ModuleDecl? PreviewExecutableItem*` | 1239 |
| `PreviewScriptSourceFile` | `Shebang? PreviewGate ModuleDecl? PreviewScriptItem*` | 1240 |
| `PreviewLibraryItem` | `LibrarySourceItem \| PreviewFfiDecl` | 1242 |
| `PreviewExecutableItem` | `ExecutableSourceItem \| PreviewFfiDecl` | 1243 |
| `PreviewScriptItem` | `ScriptSourceItem \| PreviewFfiDecl` | 1244 |
| `PreviewGate` | `"#" "preview" "(" PreviewFeatureList ")" LineBreakBoundary` | 1246 |
| `PreviewFeatureList` | `Identifier ("," Identifier)*` | 1247 |
| `PreviewFfiDecl` | `PreviewFfiFunctionDecl \| PreviewFfiBlockDecl` | 1250 |
| `PreviewFfiFunctionDecl` | `"extern" "#" "C" "def" "#" "unsafe" Identifier ParameterList ReturnClause? ThrowsClause? EffectsClause? StatementBoundary` | 1251 |
| `PreviewFfiBlockDecl` | `"extern" "c" "(" PLAIN_STRING_LITERAL ")" "{" PreviewFfiBlockMember* "}"` | 1253 |
| `PreviewFfiBlockMember` | `"unsafe" "def" Identifier ParameterList ReturnClause? ThrowsClause? EffectsClause? StatementBoundary` | 1255 |
