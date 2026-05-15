import unittest
import tempfile
import os
from unittest.mock import patch
import hashlib
from vtr_standard.poc.merkle import MerkleTree, AsyncFileStream

class TestMerkleTree(unittest.TestCase):

    def test_empty_file_edge_case(self):
        """Test that a 0-byte empty file correctly yields a prefixed leaf hash."""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.addCleanup(os.remove, temp_file.name)
        temp_file.close() # Create a 0-byte file and close it so MerkleTree can read it
        tree = MerkleTree(temp_file.name)
        expected_root = hashlib.sha256(b'\x00' + b'').hexdigest()
        self.assertEqual(tree.get_root(), expected_root)

    def test_one_byte_file_edge_case(self):
        """Test that a 1-byte file yields the correct prefixed leaf hash."""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.addCleanup(os.remove, temp_file.name)
        temp_file.write(b"a")
        temp_file.close()
        tree = MerkleTree(temp_file.name)
        expected_root = hashlib.sha256(b'\x00' + b"a").hexdigest()
        self.assertEqual(tree.get_root(), expected_root)

    def test_missing_file_raises_error(self):
        """Test that initializing a MerkleTree with a non-existent file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            MerkleTree("non_existent_file_path.txt")


class TestAsyncFileStream(unittest.TestCase):

    @patch('threading.Thread.start')
    def test_stream_yields_chunks(self, mock_start):
        """Test that stream() correctly yields enqueued chunks and stops at None."""
        streamer = AsyncFileStream("dummy_path", 1024)

        # Enqueue dummy data directly
        streamer.queue.put(b"chunk1")
        streamer.queue.put(b"chunk2")
        streamer.queue.put(None)  # Sentinel to stop iteration

        result = list(streamer.stream())

        self.assertEqual(result, [b"chunk1", b"chunk2"])
        mock_start.assert_called_once()

    @patch('threading.Thread.start')
    def test_stream_empty(self, mock_start):
        """Test that an empty file correctly yields an empty stream."""
        streamer = AsyncFileStream("dummy_path", 1024)

        # Enqueue only the EOF sentinel
        streamer.queue.put(None)

        result = list(streamer.stream())

        self.assertEqual(result, [])
        mock_start.assert_called_once()

    @patch('vtr_standard.poc.merkle.logger.error')
    @patch('threading.Thread.start')
    def test_stream_called_twice_raises_runtime_error(self, mock_start):
        """Test that calling stream() twice on the same instance raises RuntimeError due to thread constraints."""
        streamer = AsyncFileStream("dummy_path", 1024)

        # Simulate thread start behavior: first call succeeds, second raises RuntimeError
        mock_start.side_effect = [None, RuntimeError("threads can only be started once")]

        # Manually put sentinel to prevent the first stream() call from blocking
        streamer.queue.put(None)

        # First iteration exhausts the stream
        list(streamer.stream())

        # Second iteration attempts to start the thread again
        with self.assertRaises(RuntimeError):
            list(streamer.stream())

        self.assertEqual(mock_start.call_count, 2)


if __name__ == '__main__':
    unittest.main()
