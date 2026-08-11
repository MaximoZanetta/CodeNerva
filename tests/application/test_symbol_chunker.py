from pathlib import PurePosixPath
from uuid import uuid4

from codenerva.application.chunking.symbol_chunker import (
    SymbolChunker,
)
from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.source_file import SourceFile
from codenerva.domain.symbol import Symbol, SymbolKind


def test_chunk_symbol() -> None:
    source_file = SourceFile.create(
        snapshot_id=uuid4(),
        relative_path=PurePosixPath("services/auth.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="a" * 64,
    )

    symbol = Symbol.create(
        source_file_id=source_file.id,
        name="login",
        qualified_name="AuthService.login",
        kind=SymbolKind.METHOD,
        start_line=2,
        end_line=3,
    )

    source = """class AuthService:
    def login(self):
        return True
"""

    chunker = SymbolChunker()

    chunks = chunker.chunk(
        source_file=source_file,
        symbols=(symbol,),
        source=source,
    )

    assert len(chunks) == 1

    chunk = chunks[0]

    assert chunk.symbol_id == symbol.id
    assert chunk.relative_path == "services/auth.py"
    assert chunk.qualified_name == "AuthService.login"

    assert "Language: python" in chunk.text
    assert "File: services/auth.py" in chunk.text
    assert "Symbol: AuthService.login" in chunk.text
    assert "def login(self):" in chunk.text
    assert "return True" in chunk.text


def test_parent_chunk_replaces_nested_symbol_bodies() -> None:
    source_file = SourceFile.create(
        snapshot_id=uuid4(),
        relative_path=PurePosixPath("App.js"),
        language=ProgrammingLanguage.JAVASCRIPT,
        size_bytes=100,
        content_hash="a" * 64,
    )

    app = Symbol.create(
        source_file_id=source_file.id,
        name="App",
        qualified_name="App",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=11,
    )

    handle_click = Symbol.create(
        source_file_id=source_file.id,
        name="handleClick",
        qualified_name="handleClick",
        kind=SymbolKind.FUNCTION,
        start_line=4,
        end_line=6,
    )

    source = """function App() {
  const value = true;

  const handleClick = () => {
    console.log("click");
  };

  return value;
}
"""

    chunker = SymbolChunker()

    chunks = chunker.chunk(
        source_file=source_file,
        symbols=(
            app,
            handle_click,
        ),
        source=source,
    )

    assert len(chunks) == 2

    app_chunk = next(chunk for chunk in chunks if chunk.symbol_id == app.id)

    handle_click_chunk = next(
        chunk for chunk in chunks if chunk.symbol_id == handle_click.id
    )

    assert "[nested symbol: handleClick]" in app_chunk.text

    assert 'console.log("click")' not in app_chunk.text

    assert 'console.log("click")' in handle_click_chunk.text


def test_chunker_keeps_only_direct_children() -> None:
    source_file = SourceFile.create(
        snapshot_id=uuid4(),
        relative_path=PurePosixPath("App.js"),
        language=ProgrammingLanguage.JAVASCRIPT,
        size_bytes=100,
        content_hash="a" * 64,
    )

    app = Symbol.create(
        source_file_id=source_file.id,
        name="App",
        qualified_name="App",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=15,
    )

    parent = Symbol.create(
        source_file_id=source_file.id,
        name="parent",
        qualified_name="parent",
        kind=SymbolKind.FUNCTION,
        start_line=4,
        end_line=12,
    )

    child = Symbol.create(
        source_file_id=source_file.id,
        name="child",
        qualified_name="child",
        kind=SymbolKind.FUNCTION,
        start_line=7,
        end_line=9,
    )

    source = """function App() {
  const x = 1;

  function parent() {
    const y = 2;

    function child() {
      return true;
    }

    return y;
  }

  return x;
}
"""

    chunks = SymbolChunker().chunk(
        source_file=source_file,
        symbols=(
            app,
            parent,
            child,
        ),
        source=source,
    )

    app_chunk = next(chunk for chunk in chunks if chunk.symbol_id == app.id)

    parent_chunk = next(chunk for chunk in chunks if chunk.symbol_id == parent.id)

    assert "[nested symbol: parent]" in app_chunk.text
    assert "[nested symbol: child]" not in app_chunk.text

    assert "[nested symbol: child]" in parent_chunk.text
