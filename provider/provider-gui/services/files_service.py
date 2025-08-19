import os
import sys
import shutil
import tempfile
import logging
from pathlib import Path
from typing import Optional, List, Dict, Union, Any
from datetime import datetime
import json
import appdirs


class FilesServiceError(Exception):
    """Base exception for FilesService errors"""
    pass


class FileNotFoundError(FilesServiceError):
    """Raised when a requested file is not found"""
    pass


class FilePermissionError(FilesServiceError):
    """Raised when file permissions are insufficient"""
    pass


class FileValidationError(FilesServiceError):
    """Raised when file validation fails"""
    pass


class FilesService:
    """
    Production-ready file management service for Python GUI applications.
    
    Provides secure, cross-platform file operations with proper error handling,
    logging, and security measures for sensitive configuration files.
    """
    
    def __init__(self, app_name: str, app_author: str = "", enable_logging: bool = True):
        """
        Initialize the FilesService.
        
        Args:
            app_name: Name of the application (used for directory naming)
            app_author: Author/company name (optional, used on Windows)
            enable_logging: Whether to enable logging (default: True)
        """
        if not app_name or not isinstance(app_name, str):
            raise ValueError("app_name must be a non-empty string")
            
        self.app_name = app_name.strip()
        self.app_author = app_author.strip() if app_author else ""
        
        # Initialize directories
        self._setup_directories()
        
        # Setup logging
        if enable_logging:
            self._setup_logging()
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.addHandler(logging.NullHandler())
    
    def _setup_directories(self) -> None:
        """Setup application directories following OS conventions."""
        try:
            self.config_dir = Path(appdirs.user_config_dir(self.app_name, self.app_author))
            self.data_dir = Path(appdirs.user_data_dir(self.app_name, self.app_author))
            self.cache_dir = Path(appdirs.user_cache_dir(self.app_name, self.app_author))
            self.log_dir = Path(appdirs.user_log_dir(self.app_name, self.app_author))
            
            # Create directories with proper permissions
            for directory in [self.config_dir, self.data_dir, self.cache_dir, self.log_dir]:
                directory.mkdir(parents=True, exist_ok=True)
                self._set_directory_permissions(directory)
                
        except Exception as e:
            raise FilesServiceError(f"Failed to setup directories: {e}")
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        self.logger = logging.getLogger(f"{__name__}.{self.app_name}")
        
        if not self.logger.handlers:
            # Create log file path
            log_file = self.log_dir / f"{self.app_name.lower()}_files.log"
            
            # Create file handler with rotation-like behavior
            handler = logging.FileHandler(log_file, encoding='utf-8')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _set_directory_permissions(self, directory: Path) -> None:
        """Set secure permissions for directories (Unix-like systems only)."""
        if os.name != 'nt':  # Not Windows
            try:
                os.chmod(directory, 0o700)  # rwx------
            except OSError as e:
                self.logger.warning(f"Could not set permissions for {directory}: {e}")
    
    def _set_file_permissions(self, file_path: Path, secure: bool = True) -> None:
        """Set appropriate file permissions."""
        if os.name != 'nt':  # Not Windows
            try:
                if secure:
                    os.chmod(file_path, 0o600)  # rw-------
                else:
                    os.chmod(file_path, 0o644)  # rw-r--r--
            except OSError as e:
                self.logger.warning(f"Could not set permissions for {file_path}: {e}")
    
    def _validate_filename(self, filename: str) -> str:
        """
        Validate and sanitize filename.
        
        Args:
            filename: The filename to validate
            
        Returns:
            Sanitized filename
            
        Raises:
            FileValidationError: If filename is invalid
        """
        if not filename or not isinstance(filename, str):
            raise FileValidationError("Filename must be a non-empty string")
        
        filename = filename.strip()
        
        # Check for path traversal attempts
        if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
            raise FileValidationError("Invalid filename: path traversal detected")
        
        # Remove/replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Ensure filename is not too long
        if len(filename) > 255:
            raise FileValidationError("Filename too long (max 255 characters)")
        
        return filename
    
    def _backup_file(self, file_path: Path) -> Optional[Path]:
        """Create a backup of existing file."""
        if not file_path.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.with_suffix(f".backup_{timestamp}{file_path.suffix}")
        
        try:
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Failed to create backup of {file_path}: {e}")
            return None
    
    def save_config(self, filename: str, content: str, secure: bool = True, 
                   create_backup: bool = True) -> str:
        """
        Save configuration file with security measures.
        
        Args:
            filename: Name of the config file
            content: File content to save
            secure: Whether to apply secure permissions (default: True)
            create_backup: Whether to backup existing file (default: True)
            
        Returns:
            Full path to the saved file
            
        Raises:
            FilesServiceError: If save operation fails
            FileValidationError: If filename is invalid
        """
        try:
            filename = self._validate_filename(filename)
            file_path = self.config_dir / filename
            
            # Create backup if file exists and backup is requested
            if create_backup and file_path.exists():
                self._backup_file(file_path)
            
            # Create file with restrictive permissions first if secure
            if secure:
                file_path.touch(mode=0o600)
            
            # Write content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Set final permissions
            self._set_file_permissions(file_path, secure)
            
            self.logger.info(f"Config saved: {file_path} (secure: {secure})")
            return str(file_path)
            
        except Exception as e:
            # Clean up on failure
            if 'file_path' in locals():
                file_path.unlink(missing_ok=True)
            error_msg = f"Failed to save config '{filename}': {e}"
            self.logger.error(error_msg)
            raise FilesServiceError(error_msg)
    
    def load_config(self, filename: str) -> str:
        """
        Load configuration file content.
        
        Args:
            filename: Name of the config file
            
        Returns:
            File content as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
            FilesServiceError: If load operation fails
        """
        try:
            filename = self._validate_filename(filename)
            file_path = self.config_dir / filename
            
            if not file_path.exists():
                raise FileNotFoundError(f"Config file not found: {filename}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.logger.info(f"Config loaded: {file_path}")
            return content
            
        except FileNotFoundError:
            raise
        except Exception as e:
            error_msg = f"Failed to load config '{filename}': {e}"
            self.logger.error(error_msg)
            raise FilesServiceError(error_msg)
    
    def save_data(self, filename: str, data: Union[str, bytes, Dict, List], 
                 data_type: str = 'auto') -> str:
        """
        Save data file (text, binary, or JSON).
        
        Args:
            filename: Name of the data file
            data: Data to save
            data_type: Type of data ('text', 'binary', 'json', or 'auto')
            
        Returns:
            Full path to the saved file
            
        Raises:
            FilesServiceError: If save operation fails
        """
        try:
            filename = self._validate_filename(filename)
            file_path = self.data_dir / filename
            
            # Auto-detect data type
            if data_type == 'auto':
                if isinstance(data, bytes):
                    data_type = 'binary'
                elif isinstance(data, (dict, list)):
                    data_type = 'json'
                else:
                    data_type = 'text'
            
            # Save based on data type
            if data_type == 'binary':
                with open(file_path, 'wb') as f:
                    f.write(data)
            elif data_type == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:  # text
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(data))
            
            self._set_file_permissions(file_path, secure=False)
            
            self.logger.info(f"Data saved: {file_path} (type: {data_type})")
            return str(file_path)
            
        except Exception as e:
            error_msg = f"Failed to save data '{filename}': {e}"
            self.logger.error(error_msg)
            raise FilesServiceError(error_msg)
    
    def load_data(self, filename: str, data_type: str = 'auto') -> Union[str, bytes, Dict, List]:
        """
        Load data file content.
        
        Args:
            filename: Name of the data file
            data_type: Type of data to load ('text', 'binary', 'json', or 'auto')
            
        Returns:
            File content in appropriate format
            
        Raises:
            FileNotFoundError: If file doesn't exist
            FilesServiceError: If load operation fails
        """
        try:
            filename = self._validate_filename(filename)
            file_path = self.data_dir / filename
            
            if not file_path.exists():
                raise FileNotFoundError(f"Data file not found: {filename}")
            
            # Auto-detect data type from extension
            if data_type == 'auto':
                ext = file_path.suffix.lower()
                if ext == '.json':
                    data_type = 'json'
                elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip']:
                    data_type = 'binary'
                else:
                    data_type = 'text'
            
            # Load based on data type
            if data_type == 'binary':
                with open(file_path, 'rb') as f:
                    content = f.read()
            elif data_type == 'json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
            else:  # text
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            self.logger.info(f"Data loaded: {file_path} (type: {data_type})")
            return content
            
        except FileNotFoundError:
            raise
        except Exception as e:
            error_msg = f"Failed to load data '{filename}': {e}"
            self.logger.error(error_msg)
            raise FilesServiceError(error_msg)
    
    def delete_file(self, filename: str, file_type: str = 'config') -> bool:
        """
        Delete a file.
        
        Args:
            filename: Name of the file to delete
            file_type: Type of file ('config', 'data', 'cache')
            
        Returns:
            True if file was deleted, False if file didn't exist
            
        Raises:
            FilesServiceError: If delete operation fails
        """
        try:
            filename = self._validate_filename(filename)
            
            if file_type == 'config':
                file_path = self.config_dir / filename
            elif file_type == 'data':
                file_path = self.data_dir / filename
            elif file_type == 'cache':
                file_path = self.cache_dir / filename
            else:
                raise ValueError(f"Invalid file_type: {file_type}")
            
            if not file_path.exists():
                return False
            
            file_path.unlink()
            self.logger.info(f"File deleted: {file_path}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to delete file '{filename}': {e}"
            self.logger.error(error_msg)
            raise FilesServiceError(error_msg)
    
    def list_files(self, file_type: str = 'config', pattern: str = '*') -> List[str]:
        """
        List files in specified directory.
        
        Args:
            file_type: Type of files to list ('config', 'data', 'cache')
            pattern: Glob pattern to match (default: '*')
            
        Returns:
            List of filenames
            
        Raises:
            FilesServiceError: If operation fails
        """
        try:
            if file_type == 'config':
                directory = self.config_dir
            elif file_type == 'data':
                directory = self.data_dir
            elif file_type == 'cache':
                directory = self.cache_dir
            else:
                raise ValueError(f"Invalid file_type: {file_type}")
            
            files = [f.name for f in directory.glob(pattern) if f.is_file()]
            return sorted(files)
            
        except Exception as e:
            error_msg = f"Failed to list files: {e}"
            self.logger.error(error_msg)
            raise FilesServiceError(error_msg)
    
    def get_file_path(self, filename: str, file_type: str = 'config') -> str:
        """
        Get full path to a file.
        
        Args:
            filename: Name of the file
            file_type: Type of file ('config', 'data', 'cache')
            
        Returns:
            Full path to the file
            
        Raises:
            FileValidationError: If filename is invalid
        """
        filename = self._validate_filename(filename)
        
        if file_type == 'config':
            return str(self.config_dir / filename)
        elif file_type == 'data':
            return str(self.data_dir / filename)
        elif file_type == 'cache':
            return str(self.cache_dir / filename)
        else:
            raise ValueError(f"Invalid file_type: {file_type}")
    
    def get_config_path(self):
        return str(self.config_dir)
    
    def file_exists(self, filename: str, file_type: str = 'config') -> bool:
        """
        Check if a file exists.
        
        Args:
            filename: Name of the file
            file_type: Type of file ('config', 'data', 'cache')
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            filename = self._validate_filename(filename)
            
            if file_type == 'config':
                file_path = self.config_dir / filename
            elif file_type == 'data':
                file_path = self.data_dir / filename
            elif file_type == 'cache':
                file_path = self.cache_dir / filename
            else:
                return False
            
            return file_path.exists()
            
        except Exception:
            return False
    
    def get_file_info(self, filename: str, file_type: str = 'config') -> Dict[str, Any]:
        """
        Get file information.
        
        Args:
            filename: Name of the file
            file_type: Type of file ('config', 'data', 'cache')
            
        Returns:
            Dictionary with file information
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        filename = self._validate_filename(filename)
        
        if file_type == 'config':
            file_path = self.config_dir / filename
        elif file_type == 'data':
            file_path = self.data_dir / filename
        elif file_type == 'cache':
            file_path = self.cache_dir / filename
        else:
            raise ValueError(f"Invalid file_type: {file_type}")
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {filename}")
        
        stat = file_path.stat()
        return {
            'name': filename,
            'path': str(file_path),
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'is_file': file_path.is_file(),
            'permissions': oct(stat.st_mode)[-3:] if os.name != 'nt' else 'N/A'
        }
    
    def create_temp_file(self, content: str, suffix: str = '.tmp', 
                        secure: bool = True) -> str:
        """
        Create a temporary file.
        
        Args:
            content: Content to write to temporary file
            suffix: File suffix/extension
            secure: Whether to apply secure permissions
            
        Returns:
            Path to the temporary file
            
        Note:
            Caller is responsible for cleaning up temporary files
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, 
                                           delete=False, encoding='utf-8') as f:
                f.write(content)
                temp_path = f.name
            
            if secure:
                self._set_file_permissions(Path(temp_path), secure=True)
            
            self.logger.info(f"Temporary file created: {temp_path}")
            return temp_path
            
        except Exception as e:
            error_msg = f"Failed to create temporary file: {e}"
            self.logger.error(error_msg)
            raise FilesServiceError(error_msg)
    
    def cleanup_temp_file(self, temp_path: str) -> bool:
        """
        Clean up a temporary file.
        
        Args:
            temp_path: Path to the temporary file
            
        Returns:
            True if file was deleted, False otherwise
        """
        try:
            Path(temp_path).unlink(missing_ok=True)
            self.logger.info(f"Temporary file cleaned up: {temp_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to cleanup temporary file {temp_path}: {e}")
            return False
    
    def clear_cache(self) -> int:
        """
        Clear all cache files.
        
        Returns:
            Number of files deleted
        """
        deleted_count = 0
        try:
            for file_path in self.cache_dir.glob('*'):
                if file_path.is_file():
                    file_path.unlink()
                    deleted_count += 1
            
            self.logger.info(f"Cache cleared: {deleted_count} files deleted")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
            return deleted_count
    
    def get_directory_paths(self) -> Dict[str, str]:
        """
        Get all application directory paths.
        
        Returns:
            Dictionary mapping directory types to paths
        """
        return {
            'config': str(self.config_dir),
            'data': str(self.data_dir),
            'cache': str(self.cache_dir),
            'log': str(self.log_dir)
        }
    
    def __str__(self) -> str:
        return f"FilesService(app={self.app_name}, config={self.config_dir})"
    
    def __repr__(self) -> str:
        return (f"FilesService(app_name='{self.app_name}', "
                f"app_author='{self.app_author}')")


# Example usage and testing
if __name__ == "__main__":
    # Example WireGuard configuration
    wg_config = """[Interface]
PrivateKey = your_private_key_here
Address = 10.0.0.1/24
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = peer_public_key_here
Endpoint = vpn.example.com:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""

    try:
        # Initialize the service
        fs = FilesService("WireGuardManager", "MyCompany")
        
        print("FilesService initialized successfully")
        print("Directory paths:", fs.get_directory_paths())
        
        # Save a WireGuard config
        config_path = fs.save_config("wg0.conf", wg_config)
        print(f"Config saved to: {config_path}")
        
        # Load the config back
        loaded_config = fs.load_config("wg0.conf")
        print(f"Config loaded successfully ({len(loaded_config)} characters)")
        
        # Get file info
        file_info = fs.get_file_info("wg0.conf")
        print(f"File info: {file_info}")
        
        # List config files
        config_files = fs.list_files('config', '*.conf')
        print(f"Config files: {config_files}")
        
        # Save some JSON data
        data = {"version": "1.0", "created": datetime.now().isoformat()}
        fs.save_data("settings.json", data)
        print("JSON data saved")
        
        # Create temporary file
        temp_path = fs.create_temp_file("Temporary content", ".txt")
        print(f"Temporary file: {temp_path}")
        
        # Clean up temp file
        fs.cleanup_temp_file(temp_path)
        print("Temporary file cleaned up")
        
        print("\nFilesService test completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        sys.exit(1)