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
| `NUMERIC_LITERAL` | `FLOAT_LITERAL \| INTEGER_LITERAL` | 68 |
| `IMAGINARY_LITERAL` | `ScannerImaginaryFloatLiteral` | 73 |
| `RATIONAL_LITERAL` | `ScannerRationalLiteralAtExpressionPrefix` | 78 |
| `INTEGER_LITERAL` | `BinaryInteger IntegerSuffix? \| OctalInteger IntegerSuffix? \| HexInteger IntegerSuffix? \| DECIMAL_INTEGER IntegerSuffix?` | 79 |
| `FLOAT_LITERAL` | `DecimalFraction ExponentPart? FloatSuffix? \| DECIMAL_INTEGER ExponentPart FloatSuffix? \| DECIMAL_INTEGER FloatSuffix` | 84 |
| `BinaryInteger` | `("0b" \| "0B") BinaryDigits` | 87 |
| `OctalInteger` | `("0o" \| "0O") OctalDigits` | 88 |
| `HexInteger` | `("0x" \| "0X") HexDigits` | 89 |
| `DECIMAL_INTEGER` | `DecimalDigits` | 90 |
| `DecimalFraction` | `DecimalDigits "." DecimalDigits` | 91 |
| `ExponentPart` | `("e" \| "E") ("+" \| "-")? DecimalDigits` | 92 |
| `IntegerSuffix` | `"i8" \| "i16" \| "i32" \| "i64" \| "i128" \| "isize" \| "u8" \| "u16" \| "u32" \| "u64" \| "u128" \| "usize"` | 93 |
| `FloatSuffix` | `"f32" \| "f64"` | 95 |
| `BinaryDigits` | `BinaryDigit ("_"? BinaryDigit)*` | 96 |
| `OctalDigits` | `OctalDigit ("_"? OctalDigit)*` | 97 |
| `DecimalDigits` | `DecimalDigit ("_"? DecimalDigit)*` | 98 |
| `HexDigits` | `HexDigit ("_"? HexDigit)*` | 99 |
| `BinaryDigit` | `"0" \| "1"` | 100 |
| `OctalDigit` | `"0" \| "1" \| "2" \| "3" \| "4" \| "5" \| "6" \| "7"` | 101 |
| `DecimalDigit` | `"0" \| "1" \| "2" \| "3" \| "4" \| "5" \| "6" \| "7" \| "8" \| "9"` | 102 |
| `HexDigit` | `DecimalDigit \| "a" \| "b" \| "c" \| "d" \| "e" \| "f" \| "A" \| "B" \| "C" \| "D" \| "E" \| "F"` | 103 |
| `CHAR_LITERAL` | `"'" CharScalar "'"` | 106 |
| `CharScalar` | `DirectCharScalar \| SimpleCharEscape \| UnicodeScalarEscape \| NamedUnicodeEscape` | 107 |
| `SimpleCharEscape` | `"\\\\0" \| "\\\\n" \| "\\\\r" \| "\\\\t" \| "\\\\'" \| "\\\\\\\\"` | 108 |
| `UnicodeScalarEscape` | `"\\\\u{" HexScalarDigits "}"` | 109 |
| `NamedUnicodeEscape` | `"\\\\N{" UnicodeName "}"` | 110 |
| `HexScalarDigits` | `HexDigit HexDigit? HexDigit? HexDigit? HexDigit? HexDigit?` | 111 |
| `PLAIN_STRING_LITERAL` | `ScannerPlainStringLiteral` | 114 |
| `STRING_START` | `ScannerInterpolatedStringStart` | 115 |
| `STRING_TEXT` | `ScannerInterpolatedStringText` | 116 |
| `STRING_ESCAPE` | `ScannerStringEscape` | 117 |
| `INTERPOLATION_BOUNDARY` | `ScannerInterpolationBoundary` | 118 |
| `INTERPOLATION_OPEN` | `ScannerInterpolationOpen` | 119 |
| `INTERPOLATION_CLOSE` | `ScannerInterpolationClose` | 120 |
| `INTERPOLATION_FORMAT_TEXT` | `ScannerInterpolationFormatText` | 121 |
| `STRING_END` | `ScannerInterpolatedStringEnd` | 122 |
| `RAW_STRING_LITERAL` | `ScannerRawStringLiteral` | 126 |
| `MULTILINE_STRING_LITERAL` | `ScannerMultilineStringLiteral` | 127 |
| `BYTES_LITERAL` | `ScannerBytesLiteral` | 128 |
| `PATH_SEP` | `"::"` | 131 |
| `FAT_ARROW` | `"=>"` | 132 |
| `ARROW` | `"->"` | 133 |
| `DOT_DOT` | `".."` | 134 |
| `DOT_DOT_LT` | `"..<"` | 135 |
| `DOT_DOT_GT` | `"..>"` | 136 |
| `ELLIPSIS` | `"..."` | 137 |
| `TRIPLE_STAR` | `"***"` | 138 |
| `DOUBLE_STAR` | `"**"` | 139 |
| `STAR_PLUS` | `"*+"` | 140 |
| `STAR_DOT` | `"*."` | 141 |
| `AMP_AMP` | `"&&"` | 142 |
| `PIPE_PIPE` | `"\|\|"` | 143 |
| `CARET_CARET` | `"^^"` | 144 |
| `QUESTION_COLON` | `"?:"` | 145 |
| `DOUBLE_DOLLAR` | `"$$"` | 146 |
| `EQ_EQ` | `"=="` | 147 |
| `BANG_EQ` | `"!="` | 148 |
| `LT_EQ` | `"<="` | 149 |
| `GT_EQ` | `">="` | 150 |
| `PLUS_EQ` | `"+="` | 151 |
| `MINUS_EQ` | `"-="` | 152 |
| `STAR_EQ` | `"*="` | 153 |
| `SLASH_EQ` | `"/="` | 154 |
| `PERCENT_EQ` | `"%="` | 155 |
| `TILDE_TILDE` | `"~~"` | 156 |
| `COLON_EQ` | `":="` | 157 |
| `BANG_BANG` | `"!!"` | 158 |
| `DOUBLE_L_BRACE` | `"{{"` | 159 |
| `DOUBLE_R_BRACE` | `"}}"` | 160 |
| `DOLLAR_L_BRACE` | `"${"` | 161 |
| `Trivia` | `HorizontalSpace \| LineTerminator \| LineComment \| NestedBlockComment \| DocLineComment \| DocBlockComment \| WordComment` | 166 |
| `EOF_TOKEN` | `EOF` | 169 |
| `NAME_TOKEN` | `ScannerEscapedNameToken` | 171 |
| `EOF` | `ScannerEndOfInput` | 172 |

## `STABLE` 프로파일 — 540개

| 문법 production | 정확한 EBNF 오른쪽 항 | 원천 줄 |
|---|---|---:|
| `Identifier` | `IDENTIFIER` | 180 |
| `QualifiedPath` | `Identifier ("::" Identifier)*` | 183 |
| `TopLevelVisibility` | `"public" \| "private" \| "common"` | 185 |
| `MemberVisibility` | `"+" \| "-" \| "#"` | 194 |
| `ClassDispatchMarker` | `"." \| "+" \| "*." \| "*+"` | 195 |
| `TraitWitnessMarker` | `"." \| "+" \| "*." \| "*+"` | 196 |
| `VarianceMarker` | `"out" \| "in"` | 197 |
| `AnnotationAttachment` | `Annotation+` | 199 |
| `Annotation` | `"@" Identifier ArgumentList? LineBreakBoundary` | 200 |
| `RoleWord` | `Identifier \| HARD_KEYWORD` | 205 |
| `HashTag` | `"#" RoleWord` | 206 |
| `TypeParameterList` | `"<" TypeParameter ("," TypeParameter)* ","? ">"` | 209 |
| `TypeParameter` | `VarianceMarker? Identifier TypeParameterKindAnnotation?` | 210 |
| `TypeParameterKindAnnotation` | `":" TypeParameterKind` | 211 |
| `TypeParameterKind` | `"type" \| "StaticInt" \| "EffectRow" \| "ErrorSet"` | 212 |
| `TypeArgumentList` | `"<" TypeArgument ("," TypeArgument)* ","? ">"` | 214 |
| `TypeArgument` | `TypeRef \| StaticIntLiteral \| ErrorTypeArgument` | 215 |
| `ErrorTypeArgument` | `"error" TypeRef` | 216 |
| `TraitReferenceList` | `QualifiedTypeReference ("," QualifiedTypeReference)*` | 218 |
| `AssociatedTypeConstraintList` | `"where" AssociatedTypeConstraint ("," AssociatedTypeConstraint)*` | 219 |
| `AssociatedTypeConstraint` | `Identifier "==" TypeRef \| Identifier "conforms" QualifiedTypeReference` | 220 |
| `WhereClause` | `"where" WherePredicate ("," WherePredicate)*` | 223 |
| `WherePredicate` | `TypeRef "conforms" QualifiedTypeReference \| TypeRef "==" TypeRef \| RowPredicate` | 224 |
| `RowPredicate` | `Identifier "<=" EffectRow` | 227 |
| `EffectRow` | `EffectRowTerm ("\|" EffectRowTerm)*` | 229 |
| `EffectRowTerm` | `Identifier \| QualifiedTypeReference \| EffectSetLiteral` | 230 |
| `ErrorSet` | `ErrorSetTerm ("\|" ErrorSetTerm)*` | 231 |
| `ErrorSetTerm` | `Identifier \| QualifiedTypeReference` | 232 |
| `EffectSetLiteral` | `"{" IdentifierList? "}"` | 233 |
| `TypeAnnotation` | `":" TypeRef RefinementSuffix?` | 235 |
| `RefinementSuffix` | `RefinementClause \| IntervalRefinementClause` | 236 |
| `RefinementClause` | `"where" (PredicateExpr \| ImplicitThisPredicate)` | 237 |
| `ImplicitThisPredicate` | `OrderedComparisonOperator RefinementComparisonOperand` | 241 |
| `RefinementComparisonOperand` | `Literal \| Identifier \| QualifiedStaticExpr` | 242 |
| `IntervalRefinementClause` | `"in" RefinementBound (".." \| "..<") RefinementBound` | 243 |
| `RefinementBound` | `Literal \| Identifier \| QualifiedStaticExpr` | 244 |
| `OrderedComparisonOperator` | `"<" \| "<=" \| ">" \| ">="` | 245 |
| `Initializer` | `"=" Expr` | 246 |
| `NameAliasClause` | `"as" Identifier` | 247 |
| `ReturnClause` | `"->" ReturnTypeSurface` | 251 |
| `ReturnTypeSurface` | `NonFunctionTypeRef \| BareTupleTypeSurface` | 252 |
| `BareTupleTypeSurface` | `NonFunctionTypeRef "," NonFunctionTypeRef ("," NonFunctionTypeRef)*` | 253 |
| `ThrowsClause` | `"throws" ErrorSetTerm` | 258 |
| `EffectsClause` | `"effects" CallableEffectTerm` | 259 |
| `CallableEffectTerm` | `Identifier \| QualifiedTypeReference \| EmptyEffectSet` | 260 |
| `EmptyEffectSet` | `"{" "}"` | 261 |
| `ContractClause` | `RequiresClause \| EnsuresClause` | 262 |
| `RequiresClause` | `"requires" PredicateExpr` | 263 |
| `EnsuresClause` | `"ensures" PredicateExpr` | 264 |
| `LineBreakBoundary` | `LINE_BREAK_IN_TRIVIA` | 269 |
| `StatementBoundary` | `STATEMENT_BOUNDARY_BY_CONTEXT` | 270 |
| `IdentifierList` | `Identifier ("," Identifier)* ","?` | 272 |
| `ExpressionList` | `Expr ("," Expr)* ","?` | 273 |
| `PatternList` | `Pattern ("," Pattern)* ","?` | 274 |
| `StaticIntLiteral` | `DECIMAL_INTEGER` | 276 |
| `UnitSyntax` | `"(" ")"` | 279 |
| `SignedStaticInt` | `("+" \| "-")? StaticIntLiteral` | 280 |
| `LawDecl` | `"law" Identifier LawBody? StatementBoundary` | 282 |
| `LawBody` | `"{" LawBodyItem* "}"` | 285 |
| `LawBodyItem` | `LawAssertion StatementBoundary` | 286 |
| `LawAssertion` | `("requires" \| "ensures" \| "invariant")? PredicateExpr` | 287 |
| `Deeplus` | `LibrarySourceFile \| ExecutableSourceFile \| ScriptSourceFile` | 295 |
| `LibrarySourceFile` | `ModuleDecl? LibrarySourceItem* EOF_TOKEN` | 297 |
| `ExecutableSourceFile` | `ModuleDecl? ExecutableSourceItem* EOF_TOKEN` | 298 |
| `ScriptSourceFile` | `Shebang? ModuleDecl? ScriptSourceItem* EOF_TOKEN` | 299 |
| `LibrarySourceItem` | `AnnotationAttachment LibraryAnnotatableDecl \| ImportOrUseDecl \| TopLevelDecl` | 301 |
| `ExecutableSourceItem` | `AnnotationAttachment ExecutableAnnotatableDecl \| ImportOrUseDecl \| NonBindingTopLevelDecl \| EntryFunctionDecl` | 304 |
| `ScriptSourceItem` | `AnnotationAttachment ScriptAnnotatableDecl \| ImportOrUseDecl \| NonBindingTopLevelDecl \| Stmt` | 308 |
| `LibraryAnnotatableDecl` | `ImportOrUseDecl \| TopLevelDecl` | 313 |
| `ExecutableAnnotatableDecl` | `ImportOrUseDecl \| NonBindingTopLevelDecl \| EntryFunctionDecl` | 314 |
| `ScriptAnnotatableDecl` | `ImportOrUseDecl \| NonBindingTopLevelDecl` | 315 |
| `ModuleDecl` | `"module" QualifiedPath StatementBoundary` | 317 |
| `ImportOrUseDecl` | `ImportDecl \| UseDecl \| UseExportDecl` | 319 |
| `ImportDecl` | `"import" QualifiedPath ImportTail? StatementBoundary` | 320 |
| `ImportTail` | `ImportAlias \| ImportSelection` | 321 |
| `ImportAlias` | `NameAliasClause` | 322 |
| `ImportSelection` | `"::" "{" IdentifierList "}"` | 323 |
| `UseDecl` | `"use" QualifiedPath StatementBoundary` | 324 |
| `UseExportDecl` | `"use" "export" QualifiedPath StatementBoundary` | 325 |
| `ExportDecl` | `"export" ExportItem StatementBoundary?` | 328 |
| `ExportItem` | `ExportableModuleFunctionDecl \| TypeDecl \| Identifier` | 329 |
| `ExportableModuleFunctionDecl` | `TopLevelVisibility? "def" Identifier FunctionRest` | 330 |
| `TopLevelDecl` | `NonBindingTopLevelDecl \| TopLevelBindingDecl` | 338 |
| `NonBindingTopLevelDecl` | `TypeDecl \| ModuleFunctionDecl \| ExtensionFunctionDecl \| ActorDecl \| ActorProtocolDecl \| TypestateResourceDecl \| NamedEffectCapabilityDecl \| ExtensionSetDecl \| ExtensionPackDecl \| UnitCatalogDecl \| ModuleInterfaceDecl \| ConformanceDecl \| SchemaDecl \| BitfieldDecl` | 339 |
| `TypeDecl` | `ClassDecl \| TraitDecl \| EnumDecl \| TypeAliasDecl` | 354 |
| `DefIntroducer` | `"def" HashTag*` | 358 |
| `ModuleFunctionDecl` | `TopLevelVisibility? DefIntroducer Identifier FunctionRest` | 360 |
| `EntryFunctionDecl` | `DefIntroducer Identifier EntryFunctionRest` | 361 |
| `ExtensionFunctionDecl` | `TopLevelVisibility? DefIntroducer TypeRef ExtensionFunctionTarget Identifier FunctionRest` | 362 |
| `ExtensionFunctionTarget` | `"~" \| "::"` | 363 |
| `LocalFunctionDecl` | `CaptureList? DefIntroducer Identifier FunctionRest` | 364 |
| `FunctionRest` | `TypeParameterList? ParameterList FunctionTail` | 366 |
| `EntryFunctionRest` | `ParameterList ReturnClause? ThrowsClause* EffectsClause* ContractClause* FunctionBody` | 367 |
| `FunctionTail` | `ReturnClause? ThrowsClause* EffectsClause* ContractClause* WhereClause? FunctionBody` | 368 |
| `TraitFunctionTail` | `ReturnClause? ThrowsClause* EffectsClause* ContractClause* WhereClause? (FunctionBody \| StatementBoundary)` | 369 |
| `FunctionBody` | `"=" FunctionBodyContent` | 371 |
| `FunctionBodyContent` | `CallableBlock \| ReturnShorthand \| ClauseFunctionBody` | 372 |
| `CallableBlock` | `"{" BlockPrologue? FunctionStaticActivation? BlockSequence "}"` | 378 |
| `FunctionStaticActivation` | `"static" Block` | 379 |
| `ReturnShorthand` | `"return" ReturnValueSurface StatementBoundary` | 380 |
| `ClauseFunctionBody` | `"{{" LineBreakBoundary? MatchArmSequence "}}"` | 381 |
| `MemberFunctionDecl` | `MemberVisibility? DefIntroducer Identifier ClassDispatchMarker FunctionRest` | 383 |
| `TypeSideMemberFunctionDecl` | `MemberVisibility? "def" "::" Identifier FunctionRest` | 384 |
| `ConstructorDecl` | `MemberVisibility? "def" "!" Identifier ParameterList ConstructorSignatureTail? ConstructorDelegationClause? "=" Block` | 386 |
| `ConstructorSignatureTail` | `ThrowsClause+ EffectsClause* ContractClause* WhereClause? \| EffectsClause+ ContractClause* WhereClause? \| ContractClause+ WhereClause? \| WhereClause` | 388 |
| `ConstructorDelegationClause` | `":" ConstructorDelegationArm+` | 392 |
| `ConstructorDelegationArm` | `ConstructorDelegationTarget PositiveGuard?` | 393 |
| `ConstructorDelegationTarget` | `Identifier ArgumentList \| "super" "!" Identifier? ArgumentList` | 394 |
| `CleanupDecl` | `DefIntroducer "(" ")" ThrowsClause* EffectsClause* FunctionBody` | 397 |
| `ParameterList` | `"(" ParameterSequence? ")"` | 401 |
| `ParameterSequence` | `CommaParameterSequence \| LayoutParameterSequence` | 402 |
| `CommaParameterSequence` | `Parameter ("," Parameter)* ","?` | 403 |
| `LayoutParameterSequence` | `LineBreakBoundary Parameter (LineBreakBoundary Parameter)* LineBreakBoundary?` | 404 |
| `Parameter` | `StoredParameter \| ContextParameter \| WitnessParameter \| RepeatedParameter \| NamedRestParameter \| ValueParameter` | 406 |
| `ValueParameter` | `ParameterMode? ParameterPatternSlot TypeAnnotation` | 412 |
| `ParameterPatternSlot` | `Identifier IrrefutableParameterPattern?` | 417 |
| `IrrefutableParameterPattern` | `TuplePattern \| ListPattern \| RecordPattern \| NominalPattern` | 418 |
| `ParameterMode` | `"borrow" \| "mut" \| "move" \| "inout"` | 422 |
| `ContextParameter` | `"context" Identifier ":" TypeRef` | 423 |
| `WitnessParameter` | `"using" Identifier ":" "witness" TypeRef` | 424 |
| `RepeatedParameter` | `Identifier "..." TypeAnnotation` | 425 |
| `NamedRestParameter` | `Identifier "***" TypeAnnotation` | 426 |
| `StoredParameter` | `MemberVisibility? ("let" \| "var") Identifier TypeAnnotation?` | 430 |
| `ClassDecl` | `OrdinaryClassDecl \| DataClassDecl` | 434 |
| `OrdinaryClassDecl` | `TopLevelVisibility? ClassFlavor? ClassModifierSequence? "class" Identifier TypeParameterList? ParameterList? WhereClause? ClassDerivesClause? NominalConformanceClause* CleanupBudgetClause? ClassBody` | 435 |
| `DataClassDecl` | `TopLevelVisibility? "data" "class" Identifier TypeParameterList? ParameterList? WhereClause? NominalConformanceClause* CleanupBudgetClause? ClassBody?` | 439 |
| `ClassFlavor` | `"value" \| "resource"` | 441 |
| `ClassModifierSequence` | `"final" \| "open" \| "abstract" \| "sealed" \| "abstract" "sealed"` | 442 |
| `ClassDerivesClause` | `LineBreakBoundary "derives" TypeRef` | 446 |
| `NominalConformanceClause` | `LineBreakBoundary "conforms" QualifiedTypeReference NominalConformanceRoute? WhereClause?` | 447 |
| `NominalConformanceRoute` | `ConformanceViaClause \| ConformanceAutoClause` | 449 |
| `ClassBody` | `"{" MemberDecl* "}"` | 450 |
| `MemberDecl` | `FieldDecl \| MemberFunctionDecl \| ConstructorDecl \| CleanupDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| ConformBlockDecl \| ForwardDecl` | 452 |
| `FieldDecl` | `MemberVisibility? ("let" \| "var") Identifier TypeAnnotation? Initializer? StatementBoundary` | 462 |
| `TypeSideFieldDecl` | `MemberVisibility? "let" "::" Identifier TypeAnnotation? Initializer? StatementBoundary` | 464 |
| `AccessorPropertyDecl` | `("let" \| "var") Identifier TypeAnnotation ":=" AccessorSpec` | 466 |
| `AccessorSpec` | `AccessorDecl \| "{" AccessorDecl+ "}"` | 467 |
| `AccessorDecl` | `MemberVisibility? "get" Block \| MemberVisibility? "set" "(" Identifier ")" Block` | 468 |
| `ForwardDecl` | `MemberVisibility? "forward" ForwardMemberSpec "to" Expr StatementBoundary` | 470 |
| `ForwardMemberSpec` | `Identifier \| "{" Identifier ("," Identifier)* ","? "}"` | 471 |
| `TraitDecl` | `TopLevelVisibility? "trait" Identifier TypeParameterList? TraitDerivesClause* TraitAutoSupportClause? TraitBody?` | 475 |
| `TraitDerivesClause` | `LineBreakBoundary "derives" QualifiedTypeReference` | 477 |
| `TraitAutoSupportClause` | `LineBreakBoundary "supports" "auto"` | 478 |
| `TraitBody` | `"{" TraitItem* "}"` | 479 |
| `TraitItem` | `TraitMethodDecl \| AssociatedRequirementDecl \| LawDecl` | 480 |
| `TraitMethodDecl` | `MemberVisibility? DefIntroducer Identifier TraitWitnessMarker TypeParameterList? ParameterList TraitFunctionTail` | 482 |
| `AssociatedRequirementDecl` | `AssociatedTypeRequirementDecl \| AssociatedValueRequirementDecl \| AssociatedFunctionRequirementDecl` | 484 |
| `AssociatedTypeRequirementDecl` | `"type" Identifier AssociatedTypeConstraintList? StatementBoundary` | 487 |
| `AssociatedValueRequirementDecl` | `"let" "::" Identifier TypeAnnotation StatementBoundary` | 488 |
| `AssociatedFunctionRequirementDecl` | `"def" "::" Identifier ParameterList ReturnClause? ThrowsClause* EffectsClause* StatementBoundary` | 489 |
| `ConformanceDecl` | `ExplicitConformanceDecl \| AutomaticConformanceDecl` | 492 |
| `ExplicitConformanceDecl` | `TopLevelVisibility? "type" TypeRef "conforms" QualifiedTypeReference NameAliasClause? ConformanceViaClause? WhereClause? (ConformanceBody \| StatementBoundary)` | 493 |
| `AutomaticConformanceDecl` | `TopLevelVisibility? "type" TypeRef "conforms" QualifiedTypeReference NameAliasClause? ConformanceAutoClause WhereClause? StatementBoundary` | 496 |
| `ConformanceViaClause` | `"via" QualifiedPath` | 498 |
| `ConformanceAutoClause` | `"by" "auto"` | 499 |
| `ConformanceBody` | `"{" ConformanceItem* "}"` | 500 |
| `ConformanceMethodDecl` | `MemberVisibility? DefIntroducer ConformanceMethodName TraitWitnessMarker FunctionRest` | 501 |
| `ConformanceMethodName` | `Identifier \| QualifiedTypeReference "::" Identifier` | 503 |
| `ConformBlockDecl` | `"conform" QualifiedTypeReference ConformanceBody` | 509 |
| `ConformanceItem` | `ConformanceMethodDecl \| TypeSideMemberFunctionDecl \| AssociatedRequirementBinding \| ExtensionDelegationDecl \| LawDecl` | 510 |
| `AssociatedRequirementBinding` | `"type" Identifier "=" TypeRef StatementBoundary \| "let" "::" Identifier "=" Expr StatementBoundary` | 515 |
| `ExtensionDelegationDecl` | `"delegate" Identifier "to" QualifiedExtensionSelector StatementBoundary` | 517 |
| `ExtensionSetDecl` | `TopLevelVisibility? "extension" TypeRef "as" Identifier ExtensionSetBody` | 521 |
| `ExtensionSetBody` | `"{" ExtensionSetItem* "}"` | 522 |
| `ExtensionSetItem` | `ExtensionSetFunctionDecl \| TypeSideMemberFunctionDecl` | 523 |
| `ExtensionSetFunctionDecl` | `MemberVisibility? "def" Identifier ParameterList? ReturnClause? ThrowsClause* EffectsClause* WhereClause? FunctionBody` | 524 |
| `ExtensionPackDecl` | `"extension" "pack" QualifiedPath ExtensionPackBody` | 526 |
| `ExtensionPackBody` | `"{" UseExportDecl* "}"` | 527 |
| `EnumDecl` | `TopLevelVisibility? "enum" EnumOrderRole? Identifier TypeParameterList? NominalConformanceClause* EnumBody` | 531 |
| `EnumOrderRole` | `"#" ("increasing" \| "decreasing")` | 533 |
| `EnumBody` | `"{" (EnumCommaCaseSequence \| EnumLayoutBody)? "}"` | 534 |
| `EnumCommaCaseSequence` | `EnumCaseCore ("," EnumCaseCore)+ ","?` | 535 |
| `EnumLayoutBody` | `EnumCaseDecl* EnumMemberDecl*` | 536 |
| `EnumCaseDecl` | `EnumCaseCore StatementBoundary?` | 537 |
| `EnumCaseCore` | `Identifier EnumCasePayload? EnumCaseDisplayMapping?` | 538 |
| `EnumCasePayload` | `"(" EnumCaseFieldList? ")"` | 539 |
| `EnumCaseFieldList` | `EnumCaseField ("," EnumCaseField)* ","?` | 540 |
| `EnumCaseField` | `Identifier TypeAnnotation \| TypeRef` | 541 |
| `EnumMemberDecl` | `MemberFunctionDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| ConformBlockDecl \| EnumVariantSubsetAliasDecl` | 542 |
| `EnumCaseDisplayMapping` | `"~>" RestrictedEnumDisplayTemplate` | 548 |
| `RestrictedEnumDisplayTemplate` | `PLAIN_STRING_LITERAL \| MULTILINE_STRING_LITERAL \| InterpolatedString` | 549 |
| `EnumVariantSubsetAliasDecl` | `"+" "type" Identifier "=" EnumVariantSubsetRhs StatementBoundary?` | 552 |
| `EnumVariantSubsetRhs` | `Identifier ("\|" Identifier)*` | 554 |
| `SchemaDecl` | `TopLevelVisibility? "schema" Identifier TypeParameterList? SchemaBody` | 558 |
| `SchemaBody` | `"{" SchemaFieldSequence? "}"` | 559 |
| `SchemaFieldSequence` | `CommaSchemaFields \| LayoutSchemaFields` | 560 |
| `CommaSchemaFields` | `SchemaFieldDecl ("," SchemaFieldDecl)* ","?` | 561 |
| `LayoutSchemaFields` | `LineBreakBoundary LayoutSchemaFieldDecl (LineBreakBoundary LayoutSchemaFieldDecl)* LineBreakBoundary?` | 562 |
| `SchemaFieldDecl` | `Identifier TypeAnnotation Initializer? SchemaConstraint* StatementBoundary?` | 563 |
| `LayoutSchemaFieldDecl` | `Identifier TypeAnnotation Initializer? SchemaConstraint*` | 564 |
| `SchemaConstraint` | `"where" Expr` | 565 |
| `TypeAliasDecl` | `TopLevelVisibility? "type" Identifier TypeParameterList? "=" TypeAliasRhs StatementBoundary` | 567 |
| `TypeAliasRhs` | `TypeRef RefinementSuffix? \| StaticRangeType` | 568 |
| `StaticRangeType` | `StaticIntLiteral ".." StaticIntLiteral` | 569 |
| `TopLevelBindingDecl` | `TopLevelVisibility? ("let" \| "var") Identifier TypeAnnotation? "=" Expr StatementBoundary` | 571 |
| `NamedEffectCapabilityDecl` | `TopLevelVisibility? "capability" Identifier "for" EffectRow StatementBoundary` | 572 |
| `ActorDecl` | `TopLevelVisibility? "actor" MailboxClause? Identifier ActorProtocolConformanceClause* ActorBody` | 576 |
| `MailboxClause` | `HashTag "(" "capacity" ":" StaticIntLiteral ")"` | 578 |
| `ActorBody` | `"{" ActorItem* "}"` | 579 |
| `ActorProtocolConformanceClause` | `LineBreakBoundary "conforms" QualifiedTypeReference WhereClause?` | 580 |
| `ActorItem` | `ActorOnDecl \| ActorRequestDecl \| ActorMemberDecl \| ActorProtocolConformBlock` | 582 |
| `ActorMemberDecl` | `FieldDecl \| MemberFunctionDecl \| ConstructorDecl \| CleanupDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| ForwardDecl` | 586 |
| `ActorOnDecl` | `MemberVisibility? "on" Identifier ParameterList? ThrowsClause* EffectsClause* FunctionBody` | 594 |
| `ActorRequestDecl` | `MemberVisibility? "request" Identifier ParameterList? ReturnClause ThrowsClause* EffectsClause* FunctionBody` | 595 |
| `ActorProtocolConformBlock` | `"conform" QualifiedTypeReference ActorProtocolConformanceBody` | 601 |
| `ActorProtocolConformanceBody` | `"{" ActorProtocolConformanceItem* "}"` | 602 |
| `ActorProtocolConformanceItem` | `ActorOnDecl \| ActorRequestDecl` | 603 |
| `ActorProtocolDecl` | `TopLevelVisibility? "protocol" Identifier ActorProtocolBody` | 605 |
| `ActorProtocolBody` | `"{" ActorProtocolItem* "}"` | 606 |
| `ActorProtocolItem` | `ActorProtocolSendRequirement \| ActorProtocolRequestRequirement` | 607 |
| `ActorProtocolSendRequirement` | `"send" Identifier ParameterList? ThrowsClause* EffectsClause* StatementBoundary` | 608 |
| `ActorProtocolRequestRequirement` | `"request" Identifier ParameterList? ReturnClause ThrowsClause* EffectsClause* StatementBoundary` | 609 |
| `TypestateResourceDecl` | `TopLevelVisibility? "typestate" Identifier TypeParameterList? TypestateBody` | 613 |
| `TypestateBody` | `"{" TypestateTransitionDecl* "}"` | 614 |
| `TypestateTransitionDecl` | `Identifier "->" Identifier FunctionBody?` | 615 |
| `UnitCatalogDecl` | `TopLevelVisibility? "unit" "catalog" Identifier UnitCatalogBody` | 617 |
| `UnitCatalogBody` | `"{" UnitCatalogEntry* "}"` | 618 |
| `UnitCatalogEntry` | `ExactRatioUnitConversionDecl \| Identifier "=" UnitExpr StatementBoundary` | 619 |
| `ExactRatioUnitConversionDecl` | `"unit" Identifier "equalsRatio" MeasureLiteralExpr "/" StaticIntLiteral StatementBoundary` | 620 |
| `ModuleInterfaceDecl` | `ModuleSignatureDecl \| OpaqueModuleFacadeDecl` | 622 |
| `ModuleSignatureDecl` | `TopLevelVisibility? "module" "signature" QualifiedPath ModuleInterfaceBody` | 623 |
| `OpaqueModuleFacadeDecl` | `TopLevelVisibility? "opaque" "module" QualifiedPath ModuleInterfaceBody` | 624 |
| `ModuleInterfaceBody` | `"{" ModuleInterfaceItem* "}"` | 625 |
| `ModuleInterfaceItem` | `ExportDecl \| UseExportDecl \| OpaqueModuleFacadeDecl` | 626 |
| `CleanupBudgetClause` | `"cleanup" "budget" "{" CleanupBudgetItem* "}"` | 630 |
| `CleanupBudgetItem` | `EffectsBudget \| ErrorsBudget` | 631 |
| `EffectsBudget` | `"effects" "{" IdentifierList? "}"` | 632 |
| `ErrorsBudget` | `"errors" TypeRef` | 633 |
| `BitfieldDecl` | `TopLevelVisibility? BitfieldIntroducer Identifier BitfieldBackingClause BitfieldOrderClause BitfieldBody` | 637 |
| `BitfieldIntroducer` | `"bitfield" HashTag?` | 639 |
| `BitfieldBackingClause` | `"backing" TypeRef` | 640 |
| `BitfieldOrderClause` | `"order" "::" "lsb0"` | 641 |
| `BitfieldBody` | `"{" BitfieldLayoutSection BitfieldMemberDecl* "}"` | 642 |
| `BitfieldLayoutSection` | `BitfieldSlotDecl+ \| FlagSlotDecl+` | 643 |
| `BitfieldSlotDecl` | `BitfieldNamedSlot StatementBoundary \| BitfieldReservedSlot StatementBoundary` | 644 |
| `FlagSlotDecl` | `FlagNamedSlot StatementBoundary \| BitfieldReservedSlot StatementBoundary` | 645 |
| `BitfieldNamedSlot` | `MemberVisibility? Identifier ":" StaticIntLiteral BitfieldDefault?` | 646 |
| `BitfieldReservedSlot` | `"_" ":" StaticIntLiteral` | 647 |
| `FlagNamedSlot` | `MemberVisibility? Identifier` | 648 |
| `BitfieldDefault` | `"=" Literal` | 649 |
| `BitfieldMemberDecl` | `MemberFunctionDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| LawDecl` | 650 |
| `TypeRef` | `PrattType` | 662 |
| `NonFunctionTypeRef` | `PrattNonFunctionType` | 663 |
| `TypePrimary` | `QualifiedTypeReference \| FacetType \| ParenTypeSyntax \| SharpShapeType \| ExistentialType \| OpaqueType \| TypeofType \| AssociatedProjection` | 666 |
| `TypePrefixParselet` | `OwnershipQualifier` | 674 |
| `TypePostfixParselet` | `"?"` | 675 |
| `TypeInfixOperator` | `"&" \| "\|"` | 676 |
| `QualifiedTypeReference` | `QualifiedPath TypeArgumentList?` | 678 |
| `FacetType` | `"Facet" "<" "borrow" "any" QualifiedTypeReference AssociatedTypeConstraintList? ">"` | 680 |
| `OwnershipQualifier` | `"owned" \| "borrowed" \| "mut" \| "inout"` | 681 |
| `ParenTypeSyntax` | `HashTag* "(" ParenTypeItemList? ")" FunctionTypeTail?` | 689 |
| `ParenTypeItemList` | `ParenTypeItem ("," ParenTypeItem)* ","?` | 690 |
| `ParenTypeItem` | `FunctionTypeModeItem \| TypeRef \| TypeRef "..." \| TypeRef "***"` | 691 |
| `FunctionTypeModeItem` | `ParameterMode TypeRef` | 692 |
| `FunctionTypeTail` | `"->" ReturnTypeSurface ThrowsClause* EffectsClause*` | 693 |
| `SharpShapeType` | `"#" StaticDimensionList "[" TypeRef "]"` | 695 |
| `StaticDimensionList` | `StaticIntLiteral ("," StaticIntLiteral)*` | 696 |
| `ExistentialType` | `"any" QualifiedTypeReference AssociatedTypeConstraintList?` | 698 |
| `OpaqueType` | `"some" QualifiedTypeReference AssociatedTypeConstraintList?` | 699 |
| `TypeofType` | `"typeof" TypeofStaticSampleOperand` | 700 |
| `AssociatedProjection` | `"<" TypeRef "as" QualifiedTypeReference ">" "::" Identifier` | 701 |
| `TypeofStaticSampleOperand` | `Literal \| ListLiteral \| StaticPrefixedCollectionSample \| NumericArrayLiteral \| MeasureLiteralExpr` | 704 |
| `StaticPrefixedCollectionSample` | `MapLiteral \| SetLiteral \| MutListLiteral` | 709 |
| `PrattType` | `TYPE_PRATT_ENTRY` | 712 |
| `PrattNonFunctionType` | `NON_FUNCTION_TYPE_PRATT_ENTRY` | 713 |
| `Pattern` | `OrPattern` | 721 |
| `OrPattern` | `AliasPattern ("\|" AliasPattern)*` | 722 |
| `AliasPattern` | `MovePattern ("as" Identifier)?` | 723 |
| `MovePattern` | `"move"? PatternPrimary` | 724 |
| `PatternPrimary` | `TypedBindingPattern \| Identifier \| PinPattern \| RangePattern \| RelationalPattern \| TuplePattern \| RecordPattern \| ListPattern \| MapPattern \| VariantPattern \| NominalPattern \| "_" \| UnitSyntax \| Literal \| ParenthesizedPattern` | 726 |
| `TypedBindingPattern` | `Identifier ":" TypeRef` | 742 |
| `ParenthesizedPattern` | `"(" Pattern ")"` | 743 |
| `PinPattern` | `"^" StablePatternValue` | 744 |
| `StablePatternValue` | `Identifier \| QualifiedStaticExpr \| Literal` | 745 |
| `RangePattern` | `PatternBound (".." \| "..<") PatternBound` | 746 |
| `RelationalPattern` | `("<" \| "<=" \| ">" \| ">=") PatternBound` | 747 |
| `PatternBound` | `Literal \| PinPattern` | 748 |
| `TuplePattern` | `"(" TuplePatternItems ")"` | 752 |
| `TuplePatternItems` | `Pattern "," \| Pattern "," Pattern ("," Pattern)* ","?` | 753 |
| `BindingPattern` | `BindingOrPattern TypeAnnotation?` | 765 |
| `BindingOrPattern` | `BindingAliasPattern ("\|" BindingAliasPattern)*` | 766 |
| `BindingAliasPattern` | `BindingMovePattern ("as" Identifier)?` | 767 |
| `BindingMovePattern` | `"move"? BindingPatternPrimary` | 768 |
| `BindingPatternPrimary` | `Identifier \| PinPattern \| RangePattern \| RelationalPattern \| TuplePattern \| RecordPattern \| ListPattern \| MapPattern \| VariantPattern \| NominalPattern \| "_" \| UnitSyntax \| Literal \| ParenthesizedPattern` | 769 |
| `RecordPattern` | `"${" RecordPatternEntries? "}"` | 788 |
| `RecordPatternEntries` | `RecordPatternEntry (PatternEntrySeparator RecordPatternEntry)* PatternEntrySeparator?` | 789 |
| `RecordPatternEntry` | `Identifier \| RecordDestination ":" Identifier \| RecordRestPattern` | 791 |
| `RecordDestination` | `Pattern` | 792 |
| `RecordRestPattern` | `".." RestBinder` | 793 |
| `MapPattern` | `"#" "map" "{" MapPatternEntries? "}"` | 795 |
| `MapPatternEntries` | `MapPatternEntry (PatternEntrySeparator MapPatternEntry)* PatternEntrySeparator?` | 796 |
| `MapPatternEntry` | `MapDestination ":" MapKeyPattern \| MapRestPattern` | 798 |
| `MapDestination` | `Pattern` | 799 |
| `MapKeyPattern` | `Literal \| PinPattern` | 800 |
| `MapRestPattern` | `".." RestBinder` | 801 |
| `PatternEntrySeparator` | `"," LineBreakBoundary? \| LineBreakBoundary` | 802 |
| `ListPattern` | `"[" ListPatternBody? "]"` | 808 |
| `ListPatternBody` | `IgnoredAllListRest \| ExactListPattern \| PrefixRestListPattern \| SuffixRestListPattern \| MiddleRestListPattern` | 809 |
| `ExactListPattern` | `Pattern ("," Pattern)* ","?` | 814 |
| `PrefixRestListPattern` | `PrefixListRest "," Pattern ("," Pattern)* ","?` | 815 |
| `SuffixRestListPattern` | `Pattern ("," Pattern)* "," SuffixListRest ","?` | 816 |
| `MiddleRestListPattern` | `Pattern ("," Pattern)* "," MiddleListRest "," Pattern ("," Pattern)* ","?` | 817 |
| `PrefixListRest` | `RestBinder ".."` | 819 |
| `SuffixListRest` | `".." RestBinder` | 820 |
| `MiddleListRest` | `".." RestBinder ".."` | 821 |
| `IgnoredAllListRest` | `".." "_" ","?` | 822 |
| `RestBinder` | `Identifier \| "_"` | 823 |
| `VariantPattern` | `VariantQualifier Identifier VariantPatternPayload?` | 825 |
| `VariantQualifier` | `TypeRef "::" \| "::"` | 826 |
| `VariantPatternPayload` | `VariantPositionalPatternPayload \| RecordPattern` | 827 |
| `VariantPositionalPatternPayload` | `"(" PatternList? ")"` | 828 |
| `NominalPattern` | `TypeRef RecordPattern` | 833 |
| `Stmt` | `ForLoop \| WhileLoop \| RepeatLoop \| AsyncForLoop \| MatchStatement \| IfStmt \| LocalBindingStmt \| AssertiveBindingStmt \| PatternAssignmentStmt \| ParallelAssignmentStmt \| ControlTransferStmt \| TryStmt \| DeferStmt \| ScopedUseStmt \| ExprStmt \| ScopedImportStmt` | 841 |
| `ExprStmt` | `Expr StatementBoundary` | 858 |
| `Block` | `"{" BlockPrologue? BlockSequence "}"` | 860 |
| `BlockPrologue` | `(UseDecl \| ImportDecl)+` | 861 |
| `BlockSequence` | `BlockItem* BlockFinalItem?` | 862 |
| `BlockItem` | `LocalFunctionDecl \| Stmt` | 863 |
| `BlockFinalItem` | `ControlTransfer \| BindingCore \| Expr` | 866 |
| `ValueBody` | `SingleExpressionValueBody \| ExplicitRetValueBody` | 869 |
| `SingleExpressionValueBody` | `"{" ReturnValueSurface "}"` | 870 |
| `ExplicitRetValueBody` | `"{" BlockItem* RetTransfer "}"` | 871 |
| `RetTransfer` | `"ret" ReturnValueSurface? GuardClause?` | 872 |
| `BindingCore` | `("let" \| "var") BindingHead "=" BindingValueSurface` | 877 |
| `BindingHead` | `BindingPattern \| BareTupleBindingSurface` | 878 |
| `BareTupleBindingSurface` | `BindingPattern "," BindingPattern ("," BindingPattern)*` | 879 |
| `BindingValueSurface` | `Expr \| BareTupleValueSurface` | 880 |
| `ReturnValueSurface` | `Expr \| BareTupleValueSurface` | 881 |
| `BareTupleValueSurface` | `Expr "," Expr ("," Expr)*` | 882 |
| `LocalBindingStmt` | `BindingCore StatementBoundary \| RightwardLocalBindingSurface \| LazyBindingStmt \| GuardedBindingStmt` | 883 |
| `LazyBindingStmt` | `"let" HashTag Identifier TypeAnnotation? "=" Expr StatementBoundary` | 884 |
| `GuardedBindingStmt` | `("let" \| "var") BindingPattern "=" Expr "else" GuardedBindingFailure StatementBoundary?` | 885 |
| `AssertiveBindingStmt` | `("let" \| "var") "!" BindingPattern "=" Expr StatementBoundary` | 886 |
| `GuardedBindingFailure` | `GuardedBindingExit \| Pattern "=>" GuardedBindingExit` | 888 |
| `GuardedBindingExit` | `GuardedReturnExit \| GuardedThrowExit \| GuardedBreakExit \| GuardedContinueExit` | 889 |
| `GuardedReturnExit` | `"return" Expr?` | 890 |
| `GuardedThrowExit` | `"throw" Expr` | 891 |
| `GuardedBreakExit` | `("break")+ Expr?` | 892 |
| `GuardedContinueExit` | `("break")* "continue"` | 893 |
| `ControlTransferStmt` | `ControlTransfer StatementBoundary` | 896 |
| `ControlTransfer` | `ReturnTransfer \| ThrowTransfer \| BreakTransfer \| ContinueTransfer \| YieldTransfer` | 897 |
| `ReturnTransfer` | `"return" ReturnValueSurface? GuardClause?` | 898 |
| `ThrowTransfer` | `"throw" Expr GuardClause?` | 899 |
| `BreakTransfer` | `("break")+ Expr? GuardClause?` | 900 |
| `ContinueTransfer` | `("break")* "continue" GuardClause?` | 901 |
| `YieldTransfer` | `"yield" Expr? (GuardClause \| YieldResponseBinding)?` | 902 |
| `YieldResponseBinding` | `"->" DollarLocalBinding` | 903 |
| `DollarLocalBinding` | `"$" Identifier TypeAnnotation? \| "$$" Identifier TypeAnnotation?` | 904 |
| `GuardClause` | `PositiveGuard \| NegativeGuard` | 906 |
| `PositiveGuard` | `"if" Expr` | 907 |
| `NegativeGuard` | `"!" "if" Expr` | 908 |
| `IfStmt` | `"if" PatternConditionChain Block ("else" (IfStmt \| Block))?` | 910 |
| `PatternConditionChain` | `PatternControlCondition ("and" "then" PatternControlCondition)*` | 913 |
| `PatternControlCondition` | `Expr \| "let" Pattern "=" Expr` | 915 |
| `ForLoop` | `"for" ("let" Pattern \| Pattern) "in" Expr GuardClause? Block MatchStatement?` | 919 |
| `WhileLoop` | `"while" PatternConditionChain Block MatchStatement?` | 920 |
| `RepeatLoop` | `"repeat" Block "while" Expr MatchStatement?` | 921 |
| `AsyncForLoop` | `"for" ForAwaitRole ("let" Pattern \| Pattern) "in" Expr GuardClause? Block` | 925 |
| `ForAwaitRole` | `"#" "await"` | 926 |
| `MatchStatement` | `"match" MatchCore` | 928 |
| `MatchCore` | `MatchSubjectSlot MatchBody` | 929 |
| `MatchSubjectSlot` | `MATCH_SUBJECT_BY_INPUT_SUPPLY_POLICY` | 930 |
| `MatchBody` | `"{" LineBreakBoundary? MatchArmSequence "}"` | 931 |
| `MatchArmSequence` | `MatchArm (MatchArmSeparator MatchArm)* MatchArmSeparator?` | 932 |
| `MatchArm` | `MatchHead GuardClause? "=>" MatchArmBodySlot` | 933 |
| `MatchHead` | `BoundedBinderPattern \| Pattern \| "otherwise"` | 934 |
| `BoundedBinderPattern` | `PatternBound OrderedComparisonOperator Identifier OrderedComparisonOperator PatternBound` | 940 |
| `MatchArmSeparator` | `MATCH_ARM_SEPARATOR_BY_CONTEXT` | 942 |
| `MatchArmBodySlot` | `MATCH_ARM_BODY_BY_CONTEXT` | 943 |
| `TryStmt` | `"try" Block (CatchClause+ FinallyClause? \| FinallyClause)` | 947 |
| `CatchClause` | `"catch" Pattern? GuardClause? Block` | 948 |
| `ValueCatchClause` | `"catch" Pattern? GuardClause? ValueBody` | 949 |
| `FinallyClause` | `"finally" Block` | 950 |
| `DeferStmt` | `"defer" DeferredCleanupInvocation StatementBoundary` | 952 |
| `DeferredCleanupInvocation` | `DeferredDirectCall \| DeferredMessageCall` | 955 |
| `DeferredDirectCall` | `DeferredReceiver ArgumentList` | 956 |
| `DeferredMessageCall` | `DeferredReceiver "~" MessageSelector TildeArgumentSequence?` | 957 |
| `DeferredReceiver` | `DeferredPrimary DeferTargetSuffix*` | 958 |
| `DeferredPrimary` | `Identifier \| QualifiedStaticExpr` | 959 |
| `DeferTargetSuffix` | `IndexSuffix \| MemberSuffix` | 960 |
| `RightwardLocalBindingSurface` | `Expr "->" DollarLocalBinding StatementBoundary` | 964 |
| `PatternAssignmentStmt` | `AssigneePattern "=" Expr StatementBoundary` | 968 |
| `AssigneePattern` | `AssigneeTuplePattern \| AssigneeListPattern \| AssigneeRecordPattern \| AssigneeNominalPattern` | 969 |
| `AssigneePrimary` | `Identifier \| "_"` | 973 |
| `AssigneeTuplePattern` | `"(" AssigneeTupleItems ")"` | 974 |
| `AssigneeTupleItems` | `AssigneePatternItem "," \| AssigneePatternItem "," AssigneePatternItem ("," AssigneePatternItem)* ","?` | 975 |
| `AssigneePatternItem` | `AssigneePrimary \| AssigneeTuplePattern \| AssigneeListPattern \| AssigneeRecordPattern` | 978 |
| `AssigneeListPattern` | `"[" AssigneeListBody? "]"` | 982 |
| `AssigneeListBody` | `AssigneeIgnoredAllRest \| AssigneeExactList \| AssigneePrefixRestList \| AssigneeSuffixRestList \| AssigneeMiddleRestList` | 983 |
| `AssigneeExactList` | `AssigneePatternItem ("," AssigneePatternItem)* ","?` | 988 |
| `AssigneePrefixRestList` | `Identifier ".." "," AssigneeExactList` | 989 |
| `AssigneeSuffixRestList` | `AssigneeExactList "," ".." Identifier ","?` | 990 |
| `AssigneeMiddleRestList` | `AssigneeExactList "," ".." Identifier ".." "," AssigneeExactList` | 991 |
| `AssigneeIgnoredAllRest` | `".." "_" ","?` | 993 |
| `AssigneeRestPattern` | `".." ("_" \| Identifier)` | 994 |
| `AssigneeRecordPattern` | `"${" AssigneeRecordEntries? "}"` | 995 |
| `AssigneeRecordEntries` | `AssigneeRecordEntry (PatternEntrySeparator AssigneeRecordEntry)* PatternEntrySeparator?` | 996 |
| `AssigneeRecordEntry` | `Identifier \| AssigneePrimary ":" Identifier \| AssigneeRestPattern` | 999 |
| `AssigneeNominalPattern` | `TypeRef AssigneeRecordPattern` | 1000 |
| `ParallelAssignmentStmt` | `BareTuplePlaceSurface "=" AssignmentValueSurface StatementBoundary` | 1001 |
| `BareTuplePlaceSurface` | `Identifier "," Identifier ("," Identifier)*` | 1002 |
| `AssignmentValueSurface` | `Expr \| BareTupleValueSurface` | 1003 |
| `ScopedUseStmt` | `"use" ScopedPathList "in" Block` | 1004 |
| `ScopedImportStmt` | `"import" ScopedPathList "in" Block` | 1005 |
| `ScopedPathList` | `QualifiedPath ("," QualifiedPath)*` | 1006 |
| `Expr` | `PrattExpr` | 1014 |
| `PredicateExpr` | `PrattPredicateExpr` | 1015 |
| `SliceIndexExpr` | `PrattSliceIndexExpr` | 1016 |
| `ExpressionPrefixParselet` | `"+" \| "-" \| "not" \| "~~" \| "move" \| "borrow" \| "&" \| "await"` | 1022 |
| `ExpressionPostfixParselet` | `CallSuffix \| TildeCallLed \| TupleOrdinalSuffix \| IndexSuffix \| MemberSuffix \| NumericArrayTransposeSuffix \| ConstructorCallSuffix \| NamedConstructorCallSuffix \| PrototypeDerivationSuffix \| CastSuffix` | 1024 |
| `PrimaryExpr` | `Literal \| Identifier \| ImplicitAtExpr \| ParenExprSyntax \| ListLiteral \| BoundedListLiteral \| ComprehensionExpr \| MaterializationBody \| TypedMaterializationExpr \| MapLiteral \| SetLiteral \| MutListLiteral \| MapComprehensionExpr \| SetComprehensionExpr \| NumericArrayLiteral \| MeasureLiteralExpr \| QualifiedStaticExpr \| ExpectedVariantExpr \| AtControlExpr \| MatchExpr \| ClosureExpr \| GeneratorExpr \| SpawnExpr \| ConcurExpr \| UnsafeBlockExpr \| FacetExpr` | 1035 |
| `ParenExprSyntax` | `"(" ParenExprContent? ")"` | 1063 |
| `ParenExprContent` | `Expr ParenExprTail?` | 1064 |
| `ParenExprTail` | `"," \| "," Expr ("," Expr)* ","?` | 1065 |
| `ImplicitAtExpr` | `"@"` | 1066 |
| `ExpectedVariantExpr` | `"::" Identifier` | 1067 |
| `CallSuffix` | `ArgumentList TrailingClosureGroup? \| AtomicCallArgument TrailingClosureGroup` | 1071 |
| `ArgumentList` | `"(" ")" \| "(" CommaArgumentSequence ")" \| "(" LayoutArgumentSequence ")"` | 1074 |
| `CommaArgumentSequence` | `Argument ("," Argument)* ","?` | 1077 |
| `LayoutArgumentSequence` | `LineBreakBoundary NamedLayoutArgument LineBreakBoundary NamedLayoutArgument (LineBreakBoundary NamedLayoutArgument)* LineBreakBoundary?` | 1079 |
| `NamedLayoutArgument` | `NamedArgument \| NamedUnfoldArgument` | 1081 |
| `Argument` | `ContextArgument \| WitnessArgument \| NamedArgument \| PositionalUnfoldArgument \| NamedUnfoldArgument \| Expr` | 1082 |
| `ContextArgument` | `"context" Expr` | 1088 |
| `WitnessArgument` | `"using" WitnessArgumentValue` | 1089 |
| `WitnessArgumentValue` | `Identifier \| ConformanceEvidenceSelector \| NamedConformanceEvidenceSelector` | 1090 |
| `NamedArgument` | `Identifier ":" Expr` | 1091 |
| `PositionalUnfoldArgument` | `"*" Expr` | 1092 |
| `NamedUnfoldArgument` | `"**" Expr` | 1093 |
| `AtomicCallArgument` | `Literal \| Identifier \| QualifiedStaticExpr \| ExpectedVariantExpr` | 1094 |
| `TrailingClosureGroup` | `TrailingClosureArgument+` | 1098 |
| `TrailingClosureArgument` | `ClosureExpr \| Identifier ":" ClosureExpr` | 1099 |
| `IndexSuffix` | `"[" SliceAxisList "]"` | 1103 |
| `SliceAxisList` | `SliceAxis (";" SliceAxis)*` | 1104 |
| `SliceAxis` | `SliceRange \| SliceIndexExpr \| AxisWildcard` | 1105 |
| `SliceRange` | `SliceBound (".." \| "..<") SliceBound` | 1108 |
| `SliceBound` | `SliceIndexExpr \| "^" \| "$" \| "^" OffsetExpr \| "$" OffsetExpr` | 1109 |
| `OffsetExpr` | `("+" \| "-") NumericLiteral` | 1110 |
| `AxisWildcard` | `"*"` | 1111 |
| `TupleOrdinalSuffix` | `"." StaticIntLiteral` | 1113 |
| `MemberSuffix` | `"." Identifier \| "." "\\\\" NAME_TOKEN` | 1114 |
| `TildeCallLed` | `TildeCallToken MessageSelector TildeArgumentSequence? TrailingClosureGroup?` | 1120 |
| `TildeCallToken` | `"~" \| ":~"` | 1122 |
| `MessageSelector` | `Identifier \| QualifiedMessageSelector` | 1123 |
| `QualifiedMessageSelector` | `TypeRef "::" Identifier ("::" Identifier)?` | 1124 |
| `QualifiedExtensionSelector` | `TypeRef "::" Identifier "::" Identifier` | 1125 |
| `TildeArgumentSequence` | `TildeArgument ("," TildeArgument)*` | 1126 |
| `TildeArgument` | `ContextArgument \| WitnessArgument \| NamedArgument \| PositionalUnfoldArgument \| NamedUnfoldArgument \| Expr` | 1127 |
| `NumericArrayTransposeSuffix` | `"^"` | 1134 |
| `ConstructorCallSuffix` | `"!" ArgumentList` | 1135 |
| `NamedConstructorCallSuffix` | `"!" Identifier ArgumentList` | 1136 |
| `PrototypeDerivationSuffix` | `("!" \| "!!") DerivationBody` | 1137 |
| `DerivationBody` | `"{" MaterializationEntryList? "}"` | 1138 |
| `CastSuffix` | `"as" "?" TypeRef \| "as" "!" TypeRef` | 1140 |
| `QualifiedStaticExpr` | `StaticQualifier "::" Identifier \| TraitQualifiedAssociatedSelector` | 1142 |
| `StaticQualifier` | `QualifiedTypeReference \| AssociatedProjection` | 1144 |
| `TraitQualifiedAssociatedSelector` | `"<" TypeRef "as" QualifiedTypeReference ">" "::" Identifier` | 1145 |
| `AtControlExpr` | `AtIfExpr \| AtTryExpr \| AtScopeExpr` | 1151 |
| `AtIfExpr` | `"@" "if" Expr ValueBody "else" ValueBody` | 1153 |
| `AtTryExpr` | `"@" "try" ValueBody (ValueCatchClause+ FinallyClause? \| FinallyClause)` | 1154 |
| `AtScopeExpr` | `"@" "scope" ScopeModifier* ValueBody` | 1155 |
| `ScopeModifier` | `"isolated" \| "cancellable" \| "shielded"` | 1156 |
| `MatchExpr` | `"@" "match" MatchCore` | 1158 |
| `ClosureExpr` | `CaptureList? HashTag* "{" ClosureContent "}"` | 1162 |
| `ClosureContent` | `ExplicitLambdaContent \| LambdaBody?` | 1167 |
| `ExplicitLambdaContent` | `LambdaParameterList? "=>" LambdaBody` | 1168 |
| `LambdaParameterList` | `LambdaParameter ("," LambdaParameter)* ","?` | 1169 |
| `LambdaParameter` | `ParameterMode? LambdaParameterPattern TypeAnnotation?` | 1170 |
| `LambdaParameterPattern` | `Identifier \| IrrefutableParameterPattern` | 1171 |
| `LambdaBody` | `ReturnValueSurface \| LineBreakBoundary LambdaBlockContent` | 1172 |
| `LambdaBlockContent` | `BlockItem* LambdaFinalItem?` | 1173 |
| `LambdaFinalItem` | `RetTransfer \| Expr` | 1174 |
| `CaptureList` | `"[" CaptureItemList? "]"` | 1176 |
| `CaptureItemList` | `CaptureItem ("," CaptureItem)* ","?` | 1177 |
| `CaptureItem` | `("let" \| "var") Identifier "=" Expr \| CaptureMode Identifier \| Identifier` | 1178 |
| `CaptureMode` | `"borrow" \| "inout" \| "move" \| "clone" \| "deep" \| "copy" \| "once"` | 1181 |
| `GeneratorExpr` | `CaptureList? GeneratorCore` | 1199 |
| `GeneratorCore` | `"@" "for" Pattern "in" Expr Block \| "@" "while" Expr Block \| "@" "repeat" Block "while" Expr` | 1200 |
| `SpawnExpr` | `"spawn" (SpawnBody \| SpawnOperandSlot)` | 1208 |
| `SpawnBody` | `"{" "=>" SpawnBodySequence "}"` | 1209 |
| `SpawnBodySequence` | `LineBreakBoundary? BlockSequence` | 1210 |
| `SpawnOperandSlot` | `SPAWN_OPERAND_BY_PREFIX_PARSER` | 1211 |
| `ConcurExpr` | `"concur" Block` | 1212 |
| `UnsafeBlockExpr` | `"unsafe" Block` | 1213 |
| `FacetExpr` | `"facet" "[" "borrow" Expr "as" QualifiedTypeReference AssociatedTypeConstraintList? "]"` | 1216 |
| `ConformanceEvidenceSelector` | `"conformance" "(" TypeRef "conforms" QualifiedTypeReference ")"` | 1218 |
| `NamedConformanceEvidenceSelector` | `ConformanceEvidenceSelector "::" Identifier` | 1219 |
| `PrattExpr` | `EXPRESSION_PRATT_ENTRY` | 1222 |
| `PrattPredicateExpr` | `PREDICATE_PRATT_ENTRY` | 1223 |
| `PrattSliceIndexExpr` | `SLICE_INDEX_PRATT_ENTRY` | 1224 |
| `Literal` | `BoolLiteral \| NumericLiteral \| ImaginaryLiteralExpr \| RationalLiteralExpr \| StringLiteralExpr \| CharLiteralExpr \| BytesLiteral` | 1232 |
| `BoolLiteral` | `"true" \| "false"` | 1239 |
| `NumericLiteral` | `NUMERIC_LITERAL` | 1240 |
| `ImaginaryLiteralExpr` | `IMAGINARY_LITERAL` | 1241 |
| `RationalLiteralExpr` | `RATIONAL_LITERAL` | 1242 |
| `CharLiteralExpr` | `CHAR_LITERAL` | 1243 |
| `BytesLiteral` | `BYTES_LITERAL` | 1244 |
| `StringLiteralExpr` | `PLAIN_STRING_LITERAL \| RAW_STRING_LITERAL \| MULTILINE_STRING_LITERAL \| InterpolatedString` | 1247 |
| `InterpolatedString` | `STRING_START InterpolatedStringPart* STRING_END` | 1248 |
| `InterpolatedStringPart` | `STRING_TEXT \| STRING_ESCAPE \| InterpolationExpr \| InterpolationPath` | 1249 |
| `InterpolationExpr` | `INTERPOLATION_OPEN Expr InterpolationFormat? INTERPOLATION_CLOSE` | 1253 |
| `InterpolationFormat` | `":" INTERPOLATION_FORMAT_TEXT` | 1254 |
| `InterpolationPath` | `"$" InterpolationPathRoot InterpolationPathSelector* INTERPOLATION_BOUNDARY?` | 1259 |
| `InterpolationPathRoot` | `Identifier \| "@"` | 1260 |
| `InterpolationPathSelector` | `"." Identifier \| "." StaticIntLiteral \| "[" InterpolationIndex "]"` | 1261 |
| `InterpolationIndex` | `StaticIntLiteral \| Identifier` | 1264 |
| `ListLiteral` | `"[" ExpressionList? "]"` | 1269 |
| `BoundedListLiteral` | `"[" StaticIntLiteral ".." StaticIntLiteral ":" ExpressionList? "]"` | 1270 |
| `ComprehensionExpr` | `"[" Expr ComprehensionClause+ "]"` | 1272 |
| `TypedMaterializationExpr` | `TypeRef MaterializationBody` | 1275 |
| `MaterializationBody` | `"${" MaterializationEntryList? "}"` | 1276 |
| `MaterializationEntryList` | `MaterializationEntry (MaterializationSeparator MaterializationEntry)* MaterializationSeparator?` | 1277 |
| `MaterializationEntry` | `Identifier \| Identifier ":" Expr \| StringLiteralExpr ":" Expr \| NamedUnfoldArgument` | 1278 |
| `MaterializationSeparator` | `"," LineBreakBoundary? \| LineBreakBoundary` | 1282 |
| `MapLiteral` | `"#" "map" "{" MapEntryList? "}"` | 1285 |
| `MapEntryList` | `MapEntry (MaterializationSeparator MapEntry)* MaterializationSeparator?` | 1286 |
| `MapEntry` | `Expr ":" Expr \| NamedUnfoldArgument` | 1287 |
| `SetLiteral` | `"#" "set" "{" ExpressionList? "}"` | 1288 |
| `MutListLiteral` | `"#" "mut" "[" ExpressionList? "]"` | 1289 |
| `MapComprehensionExpr` | `"#" "map" "{" MapEntry ComprehensionClause+ "}"` | 1290 |
| `SetComprehensionExpr` | `"#" "set" "{" Expr ComprehensionClause+ "}"` | 1291 |
| `ComprehensionClause` | `ForClause \| PositiveGuard \| IfLetClause \| UnfoldClause` | 1293 |
| `ForClause` | `"for" Pattern "in" Expr` | 1294 |
| `IfLetClause` | `"if" "let" Pattern "=" Expr` | 1295 |
| `UnfoldClause` | `"for" "..." Pattern "in" Expr` | 1296 |
| `NumericArrayLiteral` | `ShapeInferredArrayLiteral \| ShapeInferredColumnVectorLiteral \| ExactShapeArrayLiteral` | 1299 |
| `ShapeInferredArrayLiteral` | `"#" "[" Expr ("," Expr)* ","? "]"` | 1302 |
| `ShapeInferredColumnVectorLiteral` | `"#" "[" Expr (";" Expr)+ "]"` | 1303 |
| `ExactShapeArrayLiteral` | `"#" StaticDimensionList "[" ArrayInitializer? "]"` | 1304 |
| `ArrayInitializer` | `ShapedRepeatInitializer \| ShapedGeneratorInitializer \| ShapedElementSequence` | 1305 |
| `ShapedRepeatInitializer` | `"repeat" ":" Expr` | 1308 |
| `ShapedGeneratorInitializer` | `"generate" ":" Expr` | 1309 |
| `ShapedElementSequence` | `Expr (ShapedElementSeparator Expr)* ShapedElementSeparator?` | 1310 |
| `ShapedElementSeparator` | `"," \| ShapedAxisBoundary` | 1311 |
| `ShapedAxisBoundary` | `";" ";"*` | 1312 |
| `MeasureLiteralExpr` | `NumericLiteral "[" UnitExpr "]"` | 1315 |
| `UnitExpr` | `PrattUnitExpr` | 1316 |
| `UnitPrimary` | `Identifier \| QualifiedPath \| "(" UnitExpr ")"` | 1317 |
| `UnitPostfixParselet` | `"^" SignedStaticInt` | 1318 |
| `UnitInfixOperator` | `"*" \| "/"` | 1319 |
| `PrattUnitExpr` | `UNIT_PRATT_ENTRY` | 1320 |

## `PREVIEW` 프로파일 — 13개

| 문법 production | 정확한 EBNF 오른쪽 항 | 원천 줄 |
|---|---|---:|
| `DeeplusPreview` | `PreviewLibrarySourceFile \| PreviewExecutableSourceFile \| PreviewScriptSourceFile` | 1329 |
| `PreviewLibrarySourceFile` | `PreviewGate ModuleDecl? PreviewLibraryItem* EOF_TOKEN` | 1330 |
| `PreviewExecutableSourceFile` | `PreviewGate ModuleDecl? PreviewExecutableItem* EOF_TOKEN` | 1331 |
| `PreviewScriptSourceFile` | `Shebang? PreviewGate ModuleDecl? PreviewScriptItem* EOF_TOKEN` | 1332 |
| `PreviewLibraryItem` | `LibrarySourceItem \| PreviewFfiDecl` | 1334 |
| `PreviewExecutableItem` | `ExecutableSourceItem \| PreviewFfiDecl` | 1335 |
| `PreviewScriptItem` | `ScriptSourceItem \| PreviewFfiDecl` | 1336 |
| `PreviewGate` | `"#" "preview" "(" PreviewFeatureList ")" LineBreakBoundary` | 1338 |
| `PreviewFeatureList` | `Identifier ("," Identifier)*` | 1339 |
| `PreviewFfiDecl` | `PreviewFfiFunctionDecl \| PreviewFfiBlockDecl` | 1342 |
| `PreviewFfiFunctionDecl` | `"extern" "#" "C" "def" "#" "unsafe" Identifier ParameterList ReturnClause? ThrowsClause* EffectsClause* StatementBoundary` | 1343 |
| `PreviewFfiBlockDecl` | `"extern" "c" "(" PLAIN_STRING_LITERAL ")" "{" PreviewFfiBlockMember* "}"` | 1345 |
| `PreviewFfiBlockMember` | `"unsafe" "def" Identifier ParameterList ReturnClause? ThrowsClause* EffectsClause* StatementBoundary` | 1347 |
