"""
Pipeline Manager for Multi-Stage PDF Processing.

Manages the 6-stage pipeline for converting PDFs to Skills:
1. PDF Extraction
2. Content Classification
3. Content Chunking
4. AI Enhancement (chunked)
5. Skill Generation
6. SKILL.md Enhancement

Provides caching, resumability, and progress tracking.
"""

import hashlib
import json
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PipelineStage(str, Enum):
    """Pipeline stage identifiers."""
    EXTRACTION = "extraction"
    CLASSIFICATION = "classification"
    CHUNKING = "chunking"
    ENHANCEMENT = "enhancement"
    SKILL_GENERATION = "skill_generation"
    SKILL_ENHANCEMENT = "skill_enhancement"


class CacheManager:
    """
    Manages caching of intermediate pipeline results.

    Cache structure:
        backend/cache/
        ├── extraction_<hash>.json
        ├── classification_<hash>.json
        ├── chunks_<hash>.json
        └── enhanced_chunks_<hash>/
            ├── progress.json
            ├── chunk-001.json
            ├── chunk-002.json
            └── ...
    """

    def __init__(self, cache_dir: Path = None):
        """
        Initialize cache manager.

        Args:
            cache_dir: Cache directory path (default: backend/cache/)
        """
        if cache_dir is None:
            # Default to backend/cache/
            cache_dir = Path(__file__).parent.parent.parent / "cache"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"CacheManager initialized: {self.cache_dir}")

    def hash_file(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of a file.

        Args:
            file_path: Path to file

        Returns:
            First 16 chars of SHA256 hash
        """
        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            # Read in chunks for large files
            while chunk := f.read(8192):
                sha256.update(chunk)

        # Return first 16 chars for readability
        return sha256.hexdigest()[:16]

    def hash_content(self, content: str) -> str:
        """
        Calculate SHA256 hash of content string.

        Args:
            content: Content string

        Returns:
            First 16 chars of SHA256 hash
        """
        sha256 = hashlib.sha256()
        sha256.update(content.encode('utf-8'))
        return sha256.hexdigest()[:16]

    def get_cache_path(
        self,
        stage: PipelineStage,
        content_hash: str
    ) -> Path:
        """
        Get cache file path for a stage.

        Args:
            stage: Pipeline stage
            content_hash: Content hash identifier

        Returns:
            Cache file path
        """
        if stage == PipelineStage.ENHANCEMENT:
            # Enhancement uses a directory
            return self.cache_dir / f"enhanced_chunks_{content_hash}"
        else:
            # Other stages use single JSON files
            return self.cache_dir / f"{stage.value}_{content_hash}.json"

    def cache_exists(
        self,
        stage: PipelineStage,
        content_hash: str
    ) -> bool:
        """
        Check if cache exists for a stage.

        Args:
            stage: Pipeline stage
            content_hash: Content hash identifier

        Returns:
            True if cache exists
        """
        cache_path = self.get_cache_path(stage, content_hash)

        if stage == PipelineStage.ENHANCEMENT:
            # For enhancement, check if directory exists and has progress.json
            return cache_path.exists() and (cache_path / "progress.json").exists()
        else:
            return cache_path.exists()

    def save_cache(
        self,
        stage: PipelineStage,
        content_hash: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Save data to cache.

        Args:
            stage: Pipeline stage
            content_hash: Content hash identifier
            data: Data to save
            metadata: Optional metadata to include

        Returns:
            Path to saved cache file
        """
        cache_path = self.get_cache_path(stage, content_hash)

        # Add metadata
        cache_data = {
            "stage": stage.value,
            "content_hash": content_hash,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
            "data": data
        }

        # Save JSON
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved cache: {cache_path} ({cache_path.stat().st_size:,} bytes)")

        return cache_path

    def load_cache(
        self,
        stage: PipelineStage,
        content_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load data from cache.

        Args:
            stage: Pipeline stage
            content_hash: Content hash identifier

        Returns:
            Cached data dict, or None if not found
        """
        cache_path = self.get_cache_path(stage, content_hash)

        if not cache_path.exists():
            logger.debug(f"Cache not found: {cache_path}")
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            logger.info(f"Loaded cache: {cache_path}")
            return cache_data.get("data")

        except Exception as e:
            logger.error(f"Failed to load cache {cache_path}: {e}")
            return None

    def list_cached_pdfs(self) -> List[Dict[str, Any]]:
        """
        List all cached PDF extractions.

        Returns:
            List of cache info dicts
        """
        extraction_files = self.cache_dir.glob("extraction_*.json")

        cached_pdfs = []
        for cache_file in extraction_files:
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                cached_pdfs.append({
                    "content_hash": data.get("content_hash"),
                    "pdf_path": data.get("data", {}).get("pdf_path"),
                    "total_pages": data.get("data", {}).get("total_pages"),
                    "timestamp": data.get("timestamp"),
                    "cache_file": str(cache_file)
                })
            except Exception as e:
                logger.warning(f"Failed to read {cache_file}: {e}")

        return cached_pdfs

    def clean_cache(
        self,
        content_hash: Optional[str] = None,
        older_than_days: Optional[int] = None
    ) -> int:
        """
        Clean cache files.

        Args:
            content_hash: If provided, delete only this hash's caches
            older_than_days: If provided, delete caches older than N days

        Returns:
            Number of files deleted
        """
        deleted = 0

        if content_hash:
            # Delete specific hash
            for stage in PipelineStage:
                cache_path = self.get_cache_path(stage, content_hash)
                if cache_path.exists():
                    if cache_path.is_dir():
                        import shutil
                        shutil.rmtree(cache_path)
                    else:
                        cache_path.unlink()
                    deleted += 1
                    logger.info(f"Deleted cache: {cache_path}")

        elif older_than_days:
            # Delete old caches
            import time
            cutoff = time.time() - (older_than_days * 86400)

            for cache_file in self.cache_dir.glob("*"):
                if cache_file.stat().st_mtime < cutoff:
                    if cache_file.is_dir():
                        import shutil
                        shutil.rmtree(cache_file)
                    else:
                        cache_file.unlink()
                    deleted += 1
                    logger.info(f"Deleted old cache: {cache_file}")

        return deleted


class PipelineManager:
    """
    Manages the multi-stage PDF processing pipeline.

    Coordinates execution of pipeline stages and handles caching.
    """

    def __init__(self, cache_dir: Path = None):
        """
        Initialize pipeline manager.

        Args:
            cache_dir: Cache directory path
        """
        self.cache_manager = CacheManager(cache_dir)
        logger.info("PipelineManager initialized")

    def get_stage_status(
        self,
        content_hash: str
    ) -> Dict[PipelineStage, bool]:
        """
        Check which stages have completed (cached).

        Args:
            content_hash: Content hash identifier

        Returns:
            Dict mapping stage to completion status
        """
        status = {}

        for stage in PipelineStage:
            status[stage] = self.cache_manager.cache_exists(stage, content_hash)

        return status

    def get_enhancement_progress(
        self,
        content_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get enhancement progress for a content hash.

        Args:
            content_hash: Content hash identifier

        Returns:
            Progress dict, or None if not started
        """
        enhanced_dir = self.cache_manager.get_cache_path(
            PipelineStage.ENHANCEMENT,
            content_hash
        )
        progress_file = enhanced_dir / "progress.json"

        if not progress_file.exists():
            return None

        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read progress: {e}")
            return None

    def save_enhancement_progress(
        self,
        content_hash: str,
        progress: Dict[str, Any]
    ) -> None:
        """
        Save enhancement progress.

        Args:
            content_hash: Content hash identifier
            progress: Progress dict to save
        """
        enhanced_dir = self.cache_manager.get_cache_path(
            PipelineStage.ENHANCEMENT,
            content_hash
        )
        enhanced_dir.mkdir(parents=True, exist_ok=True)

        progress_file = enhanced_dir / "progress.json"

        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2)

        logger.debug(f"Saved progress: {progress_file}")

    def load_enhanced_chunks(
        self,
        content_hash: str
    ) -> List[Dict[str, Any]]:
        """
        Load all enhanced chunks for a content hash.

        Args:
            content_hash: Content hash identifier

        Returns:
            List of enhanced chunk dicts (sorted by chunk_id)
        """
        enhanced_dir = self.cache_manager.get_cache_path(
            PipelineStage.ENHANCEMENT,
            content_hash
        )

        if not enhanced_dir.exists():
            return []

        chunks = []
        for chunk_file in sorted(enhanced_dir.glob("chunk-*.json")):
            try:
                with open(chunk_file, 'r', encoding='utf-8') as f:
                    chunk_data = json.load(f)
                    chunks.append(chunk_data)
            except Exception as e:
                logger.error(f"Failed to load {chunk_file}: {e}")

        # Sort by chunk_id
        chunks.sort(key=lambda x: x.get("chunk_id", 0))

        return chunks

    def save_enhanced_chunk(
        self,
        content_hash: str,
        chunk_id: int,
        chunk_data: Dict[str, Any]
    ) -> Path:
        """
        Save a single enhanced chunk.

        Args:
            content_hash: Content hash identifier
            chunk_id: Chunk ID (1-indexed)
            chunk_data: Enhanced chunk data

        Returns:
            Path to saved chunk file
        """
        enhanced_dir = self.cache_manager.get_cache_path(
            PipelineStage.ENHANCEMENT,
            content_hash
        )
        enhanced_dir.mkdir(parents=True, exist_ok=True)

        chunk_file = enhanced_dir / f"chunk-{chunk_id:03d}.json"

        with open(chunk_file, 'w', encoding='utf-8') as f:
            json.dump(chunk_data, f, indent=2, ensure_ascii=False)

        logger.debug(f"Saved chunk: {chunk_file}")

        return chunk_file
