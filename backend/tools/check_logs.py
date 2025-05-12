import os
import re
from datetime import datetime, timedelta

def main():
    """Search log files for template update entries in the last 24 hours"""
    # Default log locations
    log_paths = [
        'app.log',
        '../app.log',
        'logs/app.log',
        '../logs/app.log',
    ]
    
    # Try to find log files
    valid_log_files = [path for path in log_paths if os.path.exists(path)]
    
    if not valid_log_files:
        print("No log files found. Please specify the location of your log file.")
        log_path = input("Enter log file path: ")
        if os.path.exists(log_path):
            valid_log_files = [log_path]
        else:
            print(f"Log file not found at {log_path}")
            return
    
    # Time threshold - 24 hours ago
    time_threshold = datetime.now() - timedelta(hours=24)
    
    # Template update patterns
    update_patterns = [
        r"Received update for stage .+ with data: \{.*\}",
        r"Template fields in request: \[.*\]",
        r"Processing .+ -> .+ with template_id: .+",
        r"Updating template .+ with text: .+",
        r"Updated template .+ in .+ for stage .+, rows affected: \d+"
    ]
    
    print(f"Searching for template updates in logs...")
    
    for log_path in valid_log_files:
        print(f"\nChecking log file: {log_path}")
        try:
            with open(log_path, 'r') as f:
                log_content = f.readlines()
                
            # Extract relevant log entries
            update_entries = []
            for line in log_content:
                if any(re.search(pattern, line) for pattern in update_patterns):
                    # Try to extract timestamp
                    timestamp_match = re.search(r'^\[([^\]]+)\]', line)
                    if timestamp_match:
                        try:
                            # Parse timestamp, assuming ISO format
                            timestamp_str = timestamp_match.group(1)
                            timestamp = datetime.fromisoformat(timestamp_str)
                            
                            # Check if within time threshold
                            if timestamp >= time_threshold:
                                update_entries.append(line.strip())
                        except ValueError:
                            # If timestamp parsing fails, include the line anyway
                            update_entries.append(line.strip())
                    else:
                        # If no timestamp found, include the line anyway
                        update_entries.append(line.strip())
            
            if update_entries:
                print(f"Found {len(update_entries)} relevant log entries:")
                for i, entry in enumerate(update_entries[-20:], 1):  # Show last 20 entries
                    print(f"{i}. {entry}")
                print(f"\nShowing last 20 of {len(update_entries)} entries. Full logs in {log_path}")
            else:
                print("No template update log entries found.")
        except Exception as e:
            print(f"Error reading log file {log_path}: {str(e)}")
    
if __name__ == "__main__":
    main()