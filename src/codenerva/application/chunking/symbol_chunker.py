from codenerva.domain.chunk import Chunk
from codenerva.domain.source_file import SourceFile
from codenerva.domain.symbol import Symbol


class SymbolChunker:
    def chunk(
        self,
        *,
        source_file: SourceFile,
        symbols: tuple[Symbol, ...],
        source: str,
    ) -> tuple[Chunk, ...]:
        lines = source.splitlines()

        chunks: list[Chunk] = []

        for symbol in symbols:
            code = self._build_symbol_code(
                symbol=symbol,
                symbols=symbols,
                lines=lines,
            )

            if not code.strip():
                continue

            text = self._build_embedding_text(
                source_file=source_file,
                symbol=symbol,
                code=code,
            )

            chunks.append(
                Chunk.create(
                    snapshot_id=source_file.snapshot_id,
                    source_file_id=source_file.id,
                    symbol_id=symbol.id,
                    text=text,
                    relative_path=str(source_file.relative_path),
                    language=source_file.language.value,
                    qualified_name=symbol.qualified_name,
                    symbol_kind=symbol.kind.value,
                    start_line=symbol.start_line,
                    end_line=symbol.end_line,
                    code=code,
                )
            )

        return tuple(chunks)

    def _build_symbol_code(
        self,
        *,
        symbol: Symbol,
        symbols: tuple[Symbol, ...],
        lines: list[str],
    ) -> str:
        child_symbols = self._find_direct_children(
            symbol=symbol,
            symbols=symbols,
        )

        if not child_symbols:
            return self._slice_symbol(
                symbol=symbol,
                lines=lines,
            )

        result: list[str] = []

        current_line = symbol.start_line

        for child in child_symbols:
            if current_line < child.start_line:
                result.extend(lines[current_line - 1 : child.start_line - 1])

            indentation = self._line_indentation(
                lines=lines,
                line_number=child.start_line,
            )

            result.append(f"{indentation}[nested symbol: {child.qualified_name}]")

            current_line = child.end_line + 1

        if current_line <= symbol.end_line:
            result.extend(lines[current_line - 1 : symbol.end_line])

        return "\n".join(result)

    def _find_direct_children(
        self,
        *,
        symbol: Symbol,
        symbols: tuple[Symbol, ...],
    ) -> tuple[Symbol, ...]:
        contained = [
            candidate
            for candidate in symbols
            if candidate.id != symbol.id
            and candidate.start_line > symbol.start_line
            and candidate.end_line <= symbol.end_line
        ]

        direct_children: list[Symbol] = []

        for candidate in contained:
            is_nested_inside_another = any(
                other.id != candidate.id
                and other.start_line > symbol.start_line
                and other.start_line < candidate.start_line
                and candidate.end_line <= other.end_line
                for other in contained
            )

            if not is_nested_inside_another:
                direct_children.append(candidate)

        direct_children.sort(key=lambda child: child.start_line)

        return tuple(direct_children)

    def _slice_symbol(
        self,
        *,
        symbol: Symbol,
        lines: list[str],
    ) -> str:
        return "\n".join(lines[symbol.start_line - 1 : symbol.end_line])

    def _line_indentation(
        self,
        *,
        lines: list[str],
        line_number: int,
    ) -> str:
        line = lines[line_number - 1]

        return line[: len(line) - len(line.lstrip())]

    def _build_embedding_text(
        self,
        *,
        source_file: SourceFile,
        symbol: Symbol,
        code: str,
    ) -> str:
        return (
            f"Language: {source_file.language.value}\n"
            f"File: {source_file.relative_path}\n"
            f"Symbol: {symbol.qualified_name}\n"
            f"Kind: {symbol.kind.value}\n"
            "\n"
            "Code:\n"
            f"{code}"
        )
