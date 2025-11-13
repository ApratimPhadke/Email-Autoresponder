"""RAG service for duplicate email detection using vector embeddings."""

from pathlib import Path
from typing import List, Tuple

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from config import Settings
from src.models import DuplicateEmailGroup, Email
from src.utils import get_logger

logger = get_logger(__name__)


class RAGService:
    """RAG service for email duplicate detection and similarity search."""

    def __init__(self, settings: Settings):
        """Initialize RAG service.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

        # Initialize ChromaDB
        persist_dir = Path(settings.chroma_persist_directory)
        persist_dir.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.Client(
            ChromaSettings(
                persist_directory=str(persist_dir),
                anonymized_telemetry=False,
            )
        )

        self.collection = self.client.get_or_create_collection(
            name="email_embeddings",
            metadata={"description": "Email content embeddings for duplicate detection"},
        )

        logger.info("RAG service initialized successfully")

    def add_email(self, email: Email) -> None:
        """Add email to vector store.

        Args:
            email: Email object to add
        """
        try:
            # Create embedding text from subject and body
            embedding_text = f"{email.subject}\n\n{email.body[:1000]}"

            # Generate embedding
            embedding = self.embedding_model.encode(embedding_text).tolist()

            # Add to collection
            self.collection.add(
                embeddings=[embedding],
                documents=[embedding_text],
                metadatas=[
                    {
                        "email_id": email.id,
                        "subject": email.subject,
                        "sender": email.sender,
                        "date": email.date.isoformat(),
                    }
                ],
                ids=[email.id],
            )

            logger.debug(f"Added email to vector store: {email.id}")

        except Exception as e:
            logger.error(f"Error adding email to RAG: {e}", exc_info=True)

    def find_similar_emails(
        self, email: Email, threshold: float = 0.85, limit: int = 10
    ) -> List[Tuple[str, float]]:
        """Find similar emails using vector similarity.

        Args:
            email: Email to find duplicates for
            threshold: Similarity threshold (0-1)
            limit: Maximum number of results

        Returns:
            List of (email_id, similarity_score) tuples
        """
        try:
            # Create embedding text
            embedding_text = f"{email.subject}\n\n{email.body[:1000]}"

            # Generate embedding
            embedding = self.embedding_model.encode(embedding_text).tolist()

            # Query similar emails
            results = self.collection.query(
                query_embeddings=[embedding], n_results=limit, include=["distances", "metadatas"]
            )

            similar_emails = []

            if results["ids"] and results["ids"][0]:
                for i, email_id in enumerate(results["ids"][0]):
                    # Skip self-match
                    if email_id == email.id:
                        continue

                    # Convert distance to similarity (1 - normalized distance)
                    distance = results["distances"][0][i]
                    similarity = 1 - (distance / 2)  # Normalize L2 distance to 0-1

                    if similarity >= threshold:
                        similar_emails.append((email_id, similarity))

            logger.debug(
                f"Found {len(similar_emails)} similar emails for {email.id}",
                threshold=threshold,
            )

            return similar_emails

        except Exception as e:
            logger.error(f"Error finding similar emails: {e}", exc_info=True)
            return []

    def detect_duplicates(
        self, emails: List[Email], threshold: float = 0.85
    ) -> List[DuplicateEmailGroup]:
        """Detect duplicate emails in a batch.

        Args:
            emails: List of emails to check
            threshold: Similarity threshold

        Returns:
            List of duplicate email groups
        """
        try:
            duplicate_groups = []
            processed_ids = set()

            for email in emails:
                if email.id in processed_ids:
                    continue

                # Find similar emails
                similar = self.find_similar_emails(email, threshold=threshold)

                if similar:
                    duplicate_ids = [eid for eid, _ in similar]
                    similarity_scores = [score for _, score in similar]

                    group = DuplicateEmailGroup(
                        primary_email_id=email.id,
                        duplicate_ids=duplicate_ids,
                        similarity_scores=similarity_scores,
                        subject=email.subject,
                        count=len(duplicate_ids) + 1,
                    )

                    duplicate_groups.append(group)

                    # Mark all as processed
                    processed_ids.add(email.id)
                    processed_ids.update(duplicate_ids)

            logger.info(f"Detected {len(duplicate_groups)} duplicate groups")
            return duplicate_groups

        except Exception as e:
            logger.error(f"Error detecting duplicates: {e}", exc_info=True)
            return []

    def get_email_count(self) -> int:
        """Get total number of emails in vector store.

        Returns:
            Number of emails
        """
        try:
            return self.collection.count()
        except Exception:
            return 0

    def clear_store(self) -> None:
        """Clear all emails from vector store."""
        try:
            self.client.delete_collection("email_embeddings")
            self.collection = self.client.create_collection(
                name="email_embeddings",
                metadata={"description": "Email content embeddings for duplicate detection"},
            )
            logger.info("Vector store cleared")
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
