# frontend/compression_manager.py
import threading
import os
import file_handler

class CompressionManager:
    """Manages compression/decompression operations"""
    
    def __init__(self, progress_callback=None, log_callback=None):
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.is_running = False
    
    def compress(self, input_path, output_path):
        """Compress file in background thread"""
        if self.is_running:
            return False
        
        self.is_running = True
        
        def worker():
            try:
                if self.log_callback:
                    self.log_callback(f"Compressing: {os.path.basename(input_path)}")
                
                stats = file_handler.compress_file(
                    input_path, 
                    output_path,
                    progress_callback=self.progress_callback
                )
                
                if self.log_callback:
                    self.log_callback(f"✓ Compressed: {stats['ratio_percent']:.1f}% saved")
                    self.log_callback(f"  Original: {stats['original_size']:,} bytes")
                    self.log_callback(f"  Compressed: {stats['compressed_size']:,} bytes")
                    self.log_callback(f"  Time: {stats['seconds_taken']:.2f}s")
                
                return stats
                
            except Exception as e:
                if self.log_callback:
                    self.log_callback(f"✗ Error: {str(e)}")
                raise
            finally:
                self.is_running = False
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return True
    
    def decompress(self, input_path, output_path):
        """Decompress file in background thread"""
        if self.is_running:
            return False
        
        self.is_running = True
        
        def worker():
            try:
                if self.log_callback:
                    self.log_callback(f"Decompressing: {os.path.basename(input_path)}")
                
                stats = file_handler.decompress_file(
                    input_path,
                    output_path,
                    progress_callback=self.progress_callback
                )
                
                if self.log_callback:
                    self.log_callback(f"✓ Decompressed: {stats['decompressed_size']:,} bytes")
                    self.log_callback(f"  Time: {stats['seconds_taken']:.2f}s")
                
                return stats
                
            except Exception as e:
                if self.log_callback:
                    self.log_callback(f"✗ Error: {str(e)}")
                raise
            finally:
                self.is_running = False
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return True