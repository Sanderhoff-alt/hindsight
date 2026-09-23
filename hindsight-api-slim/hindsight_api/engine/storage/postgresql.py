"""PostgreSQL BYTEA-based file storage (default, zero-config)."""

import logging
from collections.abc import AsyncIterator, Callable
from typing import Any
from urllib.parse import quote

from pydantic import BaseModel

from ..db_utils import acquire_with_retry
from ..schema import fq_table_explicit as fq_table
from .base import FileStorage

logger = logging.getLogger(__name__)

PG_STREAM_CHUNK_SIZE = 4 * 1024 * 1024  # 4MB chunks for streaming storage
# 36-byte magic signature prepended to the manifest row for chunked files.
# A file starting with these exact bytes is treated as a chunked manifest.
# Collision probability with valid user binary documents or text is virtually zero.
_CHUNKED_MANIFEST_SIGNATURE = b"HINDSIGHT_STORAGE_CHUNK_MANIFEST_V1\n"


class ChunkedStorageManifest(BaseModel):
    """Manifest describing a chunked file storage stream in PostgreSQL."""

    format: str = "chunked_v1"
    chunks: int
    total_bytes: int
    chunk_size: int = PG_STREAM_CHUNK_SIZE


class PostgreSQLFileStorage(FileStorage):
    """
    PostgreSQL BYTEA-based file storage.

    Stores files directly in PostgreSQL using BYTEA columns.
    This is the default storage backend - zero configuration required!

    Pros:
    - Works out of the box (no external dependencies)
    - Transactional consistency with database
    - Simple backups (included in pg_dump)
    - Good performance for <10MB files

    Cons:
    - Database bloat for large/many files
    - Not ideal for distributed deployments
    - Higher cost than object storage at scale

    For production/scale, consider S3FileStorage instead.
    """

    def __init__(
        self,
        pool_getter: Callable[[], Any],
        schema: str | None = None,
        schema_getter: Callable[[], str] | None = None,
    ):
        """
        Initialize PostgreSQL file storage.

        Args:
            pool_getter: Function that returns asyncpg connection pool
            schema: Static database schema (fallback for single-tenant / tests)
            schema_getter: Callable returning current schema at query time (for multi-tenant)
        """
        self._pool_getter = pool_getter
        self._static_schema = schema
        self._schema_getter = schema_getter

    @property
    def _schema(self) -> str | None:
        """Resolve schema dynamically per-request when schema_getter is provided."""
        if self._schema_getter:
            return self._schema_getter()
        return self._static_schema

    async def store(
        self,
        file_data: bytes,
        key: str,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Store file in PostgreSQL."""
        pool = self._pool_getter()

        async with acquire_with_retry(pool) as conn:
            await conn.execute(
                f"""
                INSERT INTO {fq_table("file_storage", self._schema)}
                (storage_key, data)
                VALUES ($1, $2)
                ON CONFLICT (storage_key) DO UPDATE SET
                    data = EXCLUDED.data
                """,
                key,
                file_data,
            )

        logger.debug(f"Stored file {key} ({len(file_data)} bytes) in PostgreSQL")
        return key

    async def store_stream(
        self,
        key: str,
        stream: AsyncIterator[bytes],
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Store file from an async byte stream into PostgreSQL in chunks."""
        pool = self._pool_getter()
        chunk_idx = 0
        total_bytes = 0
        buffer = bytearray()

        try:
            async for chunk in stream:
                if not chunk:
                    continue
                buffer.extend(chunk)
                while len(buffer) >= PG_STREAM_CHUNK_SIZE:
                    chunk_data = bytes(buffer[:PG_STREAM_CHUNK_SIZE])
                    del buffer[:PG_STREAM_CHUNK_SIZE]
                    chunk_key = f"{key}#chunk={chunk_idx:06d}"
                    async with acquire_with_retry(pool) as conn:
                        await conn.execute(
                            f"""
                            INSERT INTO {fq_table("file_storage", self._schema)}
                            (storage_key, data)
                            VALUES ($1, $2)
                            ON CONFLICT (storage_key) DO UPDATE SET data = EXCLUDED.data
                            """,
                            chunk_key,
                            chunk_data,
                        )
                    total_bytes += len(chunk_data)
                    chunk_idx += 1

            if chunk_idx == 0:
                # Entire file fits in one chunk (< 4MB) - store as standard single row
                async with acquire_with_retry(pool) as conn:
                    await conn.execute(
                        f"""
                        INSERT INTO {fq_table("file_storage", self._schema)}
                        (storage_key, data)
                        VALUES ($1, $2)
                        ON CONFLICT (storage_key) DO UPDATE SET data = EXCLUDED.data
                        """,
                        key,
                        bytes(buffer),
                    )
                logger.debug(f"Stored stream {key} ({len(buffer)} bytes) in PostgreSQL as single row")
                return key

            if buffer:
                chunk_data = bytes(buffer)
                chunk_key = f"{key}#chunk={chunk_idx:06d}"
                async with acquire_with_retry(pool) as conn:
                    await conn.execute(
                        f"""
                        INSERT INTO {fq_table("file_storage", self._schema)}
                        (storage_key, data)
                        VALUES ($1, $2)
                        ON CONFLICT (storage_key) DO UPDATE SET data = EXCLUDED.data
                        """,
                        chunk_key,
                        chunk_data,
                    )
                total_bytes += len(chunk_data)
                chunk_idx += 1

            manifest = ChunkedStorageManifest(
                chunks=chunk_idx,
                total_bytes=total_bytes,
                chunk_size=PG_STREAM_CHUNK_SIZE,
            )
            manifest_bytes = _CHUNKED_MANIFEST_SIGNATURE + manifest.model_dump_json().encode("utf-8")
            async with acquire_with_retry(pool) as conn:
                await conn.execute(
                    f"""
                    INSERT INTO {fq_table("file_storage", self._schema)}
                    (storage_key, data)
                    VALUES ($1, $2)
                    ON CONFLICT (storage_key) DO UPDATE SET data = EXCLUDED.data
                    """,
                    key,
                    manifest_bytes,
                )
            logger.debug(f"Stored chunked stream {key} ({total_bytes} bytes in {chunk_idx} chunks) in PostgreSQL")
            return key
        except BaseException:
            try:
                chunk_keys = [key] + [f"{key}#chunk={i:06d}" for i in range(chunk_idx + 1)]
                async with acquire_with_retry(pool) as conn:
                    await conn.execute(
                        f"DELETE FROM {fq_table('file_storage', self._schema)} WHERE storage_key = ANY($1)",
                        chunk_keys,
                    )
            except Exception:
                pass
            raise

    async def retrieve(self, key: str) -> bytes:
        """Retrieve file from PostgreSQL."""
        pool = self._pool_getter()

        async with acquire_with_retry(pool) as conn:
            row = await conn.fetchrow(
                f"""
                SELECT data FROM {fq_table("file_storage", self._schema)}
                WHERE storage_key = $1
                """,
                key,
            )

        if not row:
            raise FileNotFoundError(f"File not found: {key}")

        data = bytes(row["data"])
        if data.startswith(_CHUNKED_MANIFEST_SIGNATURE):
            chunks = []
            async for chunk in self.retrieve_stream(key):
                chunks.append(chunk)
            return b"".join(chunks)

        return data

    async def retrieve_stream(self, key: str) -> AsyncIterator[bytes]:
        """Retrieve file as an async stream of bytes from PostgreSQL."""
        pool = self._pool_getter()
        async with acquire_with_retry(pool) as conn:
            row = await conn.fetchrow(
                f"""
                SELECT data FROM {fq_table("file_storage", self._schema)}
                WHERE storage_key = $1
                """,
                key,
            )

        if not row:
            raise FileNotFoundError(f"File not found: {key}")

        data = bytes(row["data"])
        if data.startswith(_CHUNKED_MANIFEST_SIGNATURE):
            try:
                manifest_json = data[len(_CHUNKED_MANIFEST_SIGNATURE) :]
                manifest = ChunkedStorageManifest.model_validate_json(manifest_json)
                chunk_count = manifest.chunks
            except Exception as e:
                logger.error(f"Corrupt chunk manifest for {key}: {e}")
                raise

            for i in range(chunk_count):
                chunk_key = f"{key}#chunk={i:06d}"
                async with acquire_with_retry(pool) as conn:
                    chunk_row = await conn.fetchrow(
                        f"""
                        SELECT data FROM {fq_table("file_storage", self._schema)}
                        WHERE storage_key = $1
                        """,
                        chunk_key,
                    )
                if not chunk_row:
                    raise FileNotFoundError(f"Missing chunk {i} for {key}")
                yield bytes(chunk_row["data"])
        else:
            yield data

    async def delete(self, key: str) -> None:
        """Delete file and any virtual chunks from PostgreSQL."""
        pool = self._pool_getter()
        sig_len = len(_CHUNKED_MANIFEST_SIGNATURE)

        async with acquire_with_retry(pool) as conn:
            backend = getattr(conn, "backend_type", "postgresql")
            if backend == "oracle":
                row = await conn.fetchrow(
                    f"""
                    SELECT DBMS_LOB.SUBSTR(data, {sig_len}, 1) as sig
                    FROM {fq_table("file_storage", self._schema)}
                    WHERE storage_key = $1
                    """,
                    key,
                )
            else:
                row = await conn.fetchrow(
                    f"""
                    SELECT substring(data from 1 for {sig_len}) as sig
                    FROM {fq_table("file_storage", self._schema)}
                    WHERE storage_key = $1
                    """,
                    key,
                )

            if not row:
                logger.warning(f"Attempted to delete non-existent file: {key}")
                return

            if row["sig"] == _CHUNKED_MANIFEST_SIGNATURE:
                manifest_row = await conn.fetchrow(
                    f"SELECT data FROM {fq_table('file_storage', self._schema)} WHERE storage_key = $1",
                    key,
                )
                chunk_keys = [key]
                if manifest_row:
                    try:
                        manifest_raw = bytes(manifest_row["data"])[sig_len:]
                        manifest = ChunkedStorageManifest.model_validate_json(manifest_raw)
                        chunk_keys.extend(f"{key}#chunk={i:06d}" for i in range(manifest.chunks))
                    except Exception as err:
                        logger.warning(f"Failed to parse manifest for {key} during delete: {err}")
                await conn.execute(
                    f"DELETE FROM {fq_table('file_storage', self._schema)} WHERE storage_key = ANY($1)",
                    chunk_keys,
                )
            else:
                await conn.execute(
                    f"DELETE FROM {fq_table('file_storage', self._schema)} WHERE storage_key = $1",
                    key,
                )

    async def delete_prefix(self, prefix: str) -> int:
        """Delete every file under ``prefix`` in PostgreSQL."""
        pool = self._pool_getter()
        # Escape LIKE's wildcards: keys carry percent-encoded segments.
        pattern = prefix.replace("!", "!!").replace("%", "!%").replace("_", "!_") + "%"
        async with acquire_with_retry(pool) as conn:
            result = await conn.execute(
                f"DELETE FROM {fq_table('file_storage', self._schema)} WHERE storage_key LIKE $1 ESCAPE '!'",
                pattern,
            )
        return int(result.split()[-1]) if isinstance(result, str) else 0

    async def exists(self, key: str) -> bool:
        """Check if file exists in PostgreSQL."""
        pool = self._pool_getter()

        async with acquire_with_retry(pool) as conn:
            row = await conn.fetchrow(
                f"""
                SELECT 1 FROM {fq_table("file_storage", self._schema)}
                WHERE storage_key = $1
                """,
                key,
            )

            return row is not None

    async def get_download_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Get download URL for PostgreSQL-stored file.

        Returns an API endpoint path (not a pre-signed URL since the file
        is stored in the database). The expires_in parameter is ignored
        for PostgreSQL storage.
        """
        # Return API path for download endpoint
        # (expires_in ignored for database storage - auth handled at API level)
        # Quoted so a key's own percent-encoded segments survive the server's
        # path decoding and arrive back as the stored key.
        return f"/v1/default/files/download/{quote(key)}"

    async def get_size(self, key: str) -> int | None:
        """Return the size of the file in bytes if known/supported, or None."""
        pool = self._pool_getter()
        sig_len = len(_CHUNKED_MANIFEST_SIGNATURE)
        async with acquire_with_retry(pool) as conn:
            backend = getattr(conn, "backend_type", "postgresql")
            if backend == "oracle":
                row = await conn.fetchrow(
                    f"""
                    SELECT DBMS_LOB.GETLENGTH(data) as len,
                           DBMS_LOB.SUBSTR(data, {sig_len}, 1) as sig
                    FROM {fq_table("file_storage", self._schema)}
                    WHERE storage_key = $1
                    """,
                    key,
                )
            else:
                row = await conn.fetchrow(
                    f"""
                    SELECT length(data) as len, substring(data from 1 for {sig_len}) as sig
                    FROM {fq_table("file_storage", self._schema)}
                    WHERE storage_key = $1
                    """,
                    key,
                )
            if not row:
                return None
            if row["sig"] == _CHUNKED_MANIFEST_SIGNATURE:
                manifest_row = await conn.fetchrow(
                    f"SELECT data FROM {fq_table('file_storage', self._schema)} WHERE storage_key = $1",
                    key,
                )
                if manifest_row:
                    try:
                        manifest_raw = bytes(manifest_row["data"])[sig_len:]
                        manifest = ChunkedStorageManifest.model_validate_json(manifest_raw)
                        return manifest.total_bytes
                    except Exception as err:
                        logger.warning(f"Failed to parse manifest for chunked file {key}: {err}")
                        return None
            return row["len"]
