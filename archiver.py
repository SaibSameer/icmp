import os
import json
import hashlib
from datetime import datetime
from collections import defaultdict
import argparse
import signal
import sys
import time

class FileArchiver:
    def __init__(self):
        # Supported file types and their processors
        self.file_types = {
            'json': {'extensions': ['.json'], 'processor': self._process_text},  # Treat as text
            'html': {'extensions': ['.html', '.htm'], 'processor': self._process_text}, # Treat as text
            'javascript': {'extensions': ['.js', '.jsx'], 'processor': self._process_text}, # Treat as text
            'python': {'extensions': ['.py'], 'processor': self._process_text}, # Treat as text
            'text': {'extensions': ['.txt', '.md'], 'processor': self._process_text} # Treat as text
        }

        # Initialize tracking variables
        self.stats = defaultdict(int)
        self.duplicates = []
        self.error_files = []
        self.total_size = 0
        self.interrupted = False

        # Default excluded directories (including node_modules)
        self.exclude_dirs = {
            'venv', '.venv', 'env', '.env',
            'archive_output', 'node_modules'
        }

        # Default excluded files
        self.exclude_files = ['restore.py']

        self.last_progress_time = time.time()
        self.progress_interval = 5  # seconds between progress updates

    def _process_text(self, content):  # Corrected: Removed extra self
        """Process any file type by preserving original content."""
        return content

    def _should_exclude(self, path):
        """Check if path should be excluded based on directory name."""
        path_parts = os.path.normpath(path).split(os.sep)
        return any(excluded_dir in path_parts for excluded_dir in self.exclude_dirs)

    def archive_files(self, input_dir, output_dir):
        """Main archiving function with directory and file exclusion."""
        start_time = datetime.now()
        print(f"Starting archive process at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Excluding directories: {', '.join(sorted(self.exclude_dirs))}")
        print(f"Excluding files: {', '.join(sorted(self.exclude_files))}")

        try:
            # Convert to absolute paths for reliable comparison
            abs_output_dir = os.path.abspath(output_dir)
            abs_input_dir = os.path.abspath(input_dir)

            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            files_by_type = defaultdict(list)
            hashes_seen = set()

            for root, dirs, files in os.walk(input_dir):
                if self.interrupted:
                    break

                # Modify dirs in-place to exclude unwanted directories
                dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

                # Skip the output directory and its contents
                abs_current_dir = os.path.abspath(root)
                if abs_current_dir.startswith(abs_output_dir):
                    continue

                # Skip any excluded directory paths
                if self._should_exclude(root):
                    continue

                for filename in files:
                    if self.interrupted:
                        break

                    file_path = os.path.join(root, filename)

                    # Skip the archiver script itself, package-lock.json and excluded files
                    if filename == os.path.basename(__file__) or filename == 'package-lock.json' or filename in self.exclude_files:
                        continue

                    # Determine file type
                    fileext = os.path.splitext(filename)[1].lower()
                    for file_type, type_info in self.file_types.items():
                        if fileext in type_info['extensions']:
                            # Process the file
                            content = self._safe_file_read(file_path)
                            if content is None:
                                continue

                            metadata = self._get_file_metadata(file_path)
                            if not metadata:
                                continue

                            processed_content = type_info['processor'](content)

                            # Add to archive if not a duplicate
                            if metadata['hash'] not in hashes_seen:
                                hashes_seen.add(metadata['hash'])
                                files_by_type[file_type].append({
                                    'path': file_path,
                                    'metadata': metadata,
                                    'content': processed_content # Store processed content directly
                                })
                                self.stats['files_processed'] += 1
                                self._show_progress()
                            break

            # Finalize the archive
            if not self.interrupted:
                print("\nFinalizing archive...")
                for file_type, files_data in files_by_type.items():
                    self._check_duplicates(files_data) #Keep track of duplicates
                    if self._write_output_file(file_type, files_data, output_dir):
                        self.stats[file_type] = len(files_data)
                        self.stats['output_files'] += 1

            # Generate reports
            self._generate_summary_report(output_dir, start_time)
            duration = datetime.now() - start_time

            if self.interrupted:
                print(f"\nArchive process interrupted after {duration}. Partial results saved.")
            else:
                print(f"\nArchive process completed in {duration}.")

            self._print_statistics()

        except Exception as e:
            print(f"\nFatal error during archiving: {str(e)}")
            sys.exit(1)

    def _safe_file_read(self, file_path):
        """Safely read file content with error handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.total_size += os.path.getsize(file_path)
            return content
        except Exception as e:
            self.error_files.append(file_path)
            print(f"Error reading {file_path}: {str(e)}")
            return None

    def _get_file_metadata(self, file_path):
        """Extract file metadata."""
        try:
            stat_info = os.stat(file_path)
            file_size = stat_info.st_size
            modified_time = datetime.fromtimestamp(stat_info.st_mtime)
            created_time = datetime.fromtimestamp(os.path.getctime(file_path))

            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            file_hash = hashlib.sha256(file_content.encode('utf-8')).hexdigest()

            num_lines = file_content.count('\n') + 1

            return {
                'size': file_size,
                'modified': modified_time.isoformat(),
                'created': created_time.isoformat(),
                'hash': file_hash,
                'lines': num_lines,
            }
        except Exception as e:
            self.error_files.append(file_path)
            print(f"Error getting metadata for {file_path}: {str(e)}")
            return None

    def _check_duplicates(self, files_data):
        """Check for duplicate files based on content hash."""
        hashes = defaultdict(list)
        for file_data in files_data:
            hash_value = file_data['metadata']['hash']
            hashes[hash_value].append(file_data['path'])

        for hash_value, paths in hashes.items():
            if len(paths) > 1:
                self.duplicates.extend(paths)
                self.stats['duplicate_files'] += len(paths) - 1  # Exclude original

    def _write_output_file(self, file_type, files_data, output_dir):
        """Write combined output file for a specific file type."""
        output_file = os.path.join(output_dir, f"archive_{file_type}.txt") # Modified output file name
        try:
            with open(output_file, 'w', encoding='utf-8') as outfile:
                for file_data in files_data:
                    # Write metadata
                    outfile.write("=" * 80 + "\n")
                    outfile.write(f"File: {os.path.basename(file_data['path'])}\n")
                    outfile.write(f"Path: {file_data['path']}\n")
                    for key, value in file_data['metadata'].items():
                        outfile.write(f"{key.capitalize()}: {value}\n")
                    outfile.write("=" * 80 + "\n")

                    # Write content
                    outfile.write(file_data['content'])
                    outfile.write("\n\n")  # Add extra spacing

            print(f"Created archive file: {output_file}")
            return True
        except Exception as e:
            print(f"Error writing to {output_file}: {str(e)}")
            self.error_files.append(output_file)
            return False

    def _generate_summary_report(self, output_dir, start_time):
        """Generate a summary report."""
        report_file = os.path.join(output_dir, "archive_summary.txt")
        end_time = datetime.now()
        duration = end_time - start_time
        try:
            with open(report_file, 'w', encoding='utf-8') as outfile:
                outfile.write("=== ARCHIVE SUMMARY REPORT ===\n\n")
                outfile.write(f"Archive created: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                outfile.write(f"Process started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                outfile.write(f"Duration: {duration}\n\n")

                outfile.write("=== STATISTICS ===\n\n")
                outfile.write(f"Files processed: {self.stats['files_processed']}\n")
                outfile.write(f"Output files created: {self.stats['output_files']}\n")
                outfile.write(f"Total size processed: {self._format_size(self.total_size)}\n\n")

                outfile.write("File Type Breakdown:\n")
                for file_type in self.file_types:
                    outfile.write(f"{file_type.capitalize()}: {self.stats[file_type]}\n")
                outfile.write("\n")

                if self.duplicates:
                    outfile.write("=== DUPLICATE FILES ===\n")
                    for duplicate in self.duplicates:
                        outfile.write(f"{duplicate}\n")
                    outfile.write("\n")

                if self.error_files:
                    outfile.write("=== FILES WITH ERRORS ===\n")
                    for error_file in self.error_files:
                        outfile.write(f"{error_file}\n")
                    outfile.write("\n")

        except Exception as e:
            print(f"Error writing summary report: {str(e)}")

    def _print_statistics(self):
        """Print statistics to the console."""
        print("\n=== STATISTICS ===")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Output files created: {self.stats['output_files']}")
        print(f"Total size processed: {self._format_size(self.total_size)}")
        print("File Type Breakdown:")
        for file_type in self.file_types:
            print(f"{file_type.capitalize()}: {self.stats[file_type]}")

        if self.duplicates:
            print(f"\nDuplicate files found: {len(self.duplicates)}")
        if self.error_files:
            print(f"\nFiles with errors: {len(self.error_files)}")

    def _format_size(self, num, suffix='B'):
        """Format file size into human-readable form."""
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return f"{num:3.1f} {unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f} Yi{suffix}"

    def _show_progress(self):
        """Display progress every few seconds."""
        current_time = time.time()
        if current_time - self.last_progress_time >= self.progress_interval:
            print(f"Files processed: {self.stats['files_processed']}", end='\r')
            self.last_progress_time = current_time

def main():
    parser = argparse.ArgumentParser(description='File Archiver that combines into text files and excludes package-lock.json')
    parser.add_argument('-i', '--input', default='.', help='Input directory (default: current)')
    parser.add_argument('-o', '--output', default='./archive_output',
                        help='Output directory (default: ./archive_output)')
    parser.add_argument('--exclude_dir', nargs='+', default=[],
                        help='Additional directories to exclude')
    parser.add_argument('--exclude_file', nargs='+', default=[],
                        help='Additional files to exclude')
    args = parser.parse_args()

    def handle_interrupt(sig, frame):
        print("\nReceived interrupt signal. Attempting graceful shutdown...")
        archiver.interrupted = True

    signal.signal(signal.SIGINT, handle_interrupt)

    try:
        archiver = FileArchiver()
        # Add any custom excluded directories from command line
        archiver.exclude_dirs.update(args.exclude_dir)
        # Add any custom excluded files from command line
        archiver.exclude_files.extend(args.exclude_file)

        # Ensure output directory name is excluded
        output_dir_name = os.path.basename(os.path.normpath(args.output))
        archiver.exclude_dirs.add(output_dir_name)

        archiver.archive_files(args.input, args.output)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()