#!/usr/bin/env python3
from pathlib import Path
import re

def is_code_block(line):
    """Check if the line is likely a code block or command"""
    code_indicators = [
        '```', '#!/', '.py', '.sh', '.yml', '.ini', '.conf',
        'sudo', 'pip', 'python', 'git', 'cp', 'mv', 'rm',
        'postgres=#', 'mysql>', 'redis>', '!/bin/bash',
        'Check ', 'Install ', 'Configure ', 'Update ',
        'backend/', '/etc/', '/usr/local/bin/',
        'Edit .env', 'Set password', 'Keep only last',
        'Restore from', 'Analyze tables', 'Vacuum database',
        'Allow only', 'Update SSL', 'Update system',
        'Update Python', 'Configure PostgreSQL',
        'Start ', 'Set Up ', 'Create ', 'Initialize ',
        'Log ', 'Metrics ', 'Health ', 'CPU ', 'Memory ',
        'Disk ', 'Network ', 'API ', 'Security ',
        'Check ', 'Test ', 'Monitor ', 'Backup ',
        'Restore ', 'Optimize ', 'Maintain ',
        'Production ', 'Scaling ', 'Maintenance ',
        'Conclusion ', 'Overview ', 'Setup ',
        'Database ', 'Redis ', 'Connection ',
        'Issues ', 'Problems ', 'Errors ',
        'Install ', 'Configure ', 'Update ',
        'Check ', 'Test ', 'Monitor ',
        'CPU ', 'Memory ', 'Disk ', 'Network ',
        'Request ', 'Database ', 'Cache ',
        'Template ', 'Error ', 'Health ',
        'Authentication ', 'API ', 'Security ',
        'Suspicious ', 'Activity ', 'Alert ',
        'Maintenance ', 'Retention ', 'Update ',
        'Edit ', 'Set ', 'Keep ', 'Restore ',
        'Analyze ', 'Vacuum ', 'Allow ', 'Update ',
        'Configure ', 'Start ', 'Create ', 'Initialize ',
        'Log ', 'Monitor ', 'Backup ', 'Restore ',
        'Optimize ', 'Maintain ', 'Scale ', 'Deploy ',
        'Conclusion ', 'Overview ', 'Setup ', 'Install ',
        'Configure ', 'Update ', 'Check ', 'Test ',
        'Monitor ', 'CPU ', 'Memory ', 'Disk ',
        'Network ', 'Request ', 'Database ', 'Cache ',
        'Template ', 'Error ', 'Health ', 'Authentication ',
        'API ', 'Security ', 'Suspicious ', 'Activity ',
        'Alert ', 'Maintenance ', 'Retention ', 'Update ',
        'Check ', 'Test ', 'Verify ', 'Validate ',
        'Run ', 'Execute ', 'Install ', 'Configure ',
        'Update ', 'Start ', 'Stop ', 'Restart ',
        'Create ', 'Delete ', 'Modify ', 'Change ',
        'Set ', 'Get ', 'List ', 'Show ', 'Display ',
        'Enable ', 'Disable ', 'Add ', 'Remove ',
        'Import ', 'Export ', 'Backup ', 'Restore ',
        'Monitor ', 'Log ', 'Track ', 'Trace ',
        'Debug ', 'Fix ', 'Resolve ', 'Handle ',
        'Process ', 'Manage ', 'Control ', 'Operate ',
        'Check ', 'Test ', 'Verify ', 'Validate ',
        'Run ', 'Execute ', 'Install ', 'Configure ',
        'Update ', 'Start ', 'Stop ', 'Restart ',
        'Create ', 'Delete ', 'Modify ', 'Change ',
        'Set ', 'Get ', 'List ', 'Show ', 'Display ',
        'Enable ', 'Disable ', 'Add ', 'Remove ',
        'Import ', 'Export ', 'Backup ', 'Restore ',
        'Monitor ', 'Log ', 'Track ', 'Trace ',
        'Debug ', 'Fix ', 'Resolve ', 'Handle ',
        'Process ', 'Manage ', 'Control ', 'Operate ',
        'Check ', 'Test ', 'Verify ', 'Validate ',
        'Run ', 'Execute ', 'Install ', 'Configure ',
        'Update ', 'Start ', 'Stop ', 'Restart ',
        'Create ', 'Delete ', 'Modify ', 'Change ',
        'Set ', 'Get ', 'List ', 'Show ', 'Display ',
        'Enable ', 'Disable ', 'Add ', 'Remove ',
        'Import ', 'Export ', 'Backup ', 'Restore ',
        'Monitor ', 'Log ', 'Track ', 'Trace ',
        'Debug ', 'Fix ', 'Resolve ', 'Handle ',
        'Process ', 'Manage ', 'Control ', 'Operate '
    ]
    return any(indicator in line for indicator in code_indicators)

def is_file_path(line):
    """Check if the line is a file path"""
    path_indicators = [
        'backend/', '/etc/', '/usr/local/bin/',
        '.py', '.sh', '.yml', '.ini', '.conf',
        'config.py', 'prometheus.yml', 'grafana.ini',
        'alertmanager.yml', 'icmp-backend.yml',
        'health.py', 'metrics.py', 'monitoring.py',
        'timing.py', 'access_log.py',
        'sites-available/', 'logrotate.d/',
        'prometheus/', 'grafana/', 'rules/',
        'routes/', 'middleware/', 'database/',
        'security/', 'monitoring/',
        'config/', 'logs/', 'scripts/',
        'templates/', 'static/', 'media/',
        'tests/', 'docs/', 'examples/',
        'migrations/', 'fixtures/', 'utils/',
        'services/', 'models/', 'views/',
        'controllers/', 'helpers/', 'lib/',
        'vendor/', 'node_modules/', 'dist/',
        'build/', 'src/', 'app/', 'bin/',
        'etc/', 'var/', 'opt/', 'usr/',
        'home/', 'root/', 'tmp/', 'dev/',
        'proc/', 'sys/', 'mnt/', 'media/',
        'srv/', 'lib/', 'lib64/', 'sbin/',
        'boot/', 'run/', 'lost+found/', 'snap/',
        'backend/config.py', 'backend/monitoring/metrics.py',
        'backend/routes/health.py', 'backend/middleware/timing.py',
        'backend/database/monitoring.py', 'backend/security/monitoring.py',
        'backend/middleware/access_log.py', '/etc/nginx/sites-available/icmp-backend',
        '/etc/logrotate.d/icmp-backend', '/etc/prometheus/prometheus.yml',
        '/etc/grafana/grafana.ini', '/etc/prometheus/alertmanager.yml',
        '/etc/prometheus/rules/icmp-backend.yml', '/etc/prometheus/rules/security.yml',
        '/usr/local/bin/check-icmp-health.sh', '/usr/local/bin/monitor-cpu.sh',
        '/usr/local/bin/monitor-memory.sh'
    ]
    return any(indicator in line for indicator in path_indicators)

def is_subsection(heading_text, current_section):
    """Check if the heading should be a subsection"""
    if not current_section:
        return False
    
    # If it's a code-like heading, it should be a subsection
    if is_code_block(heading_text):
        return True
    
    # If it's a file path, it should be a subsection
    if is_file_path(heading_text):
        return True
    
    # If it's a configuration or setup step, it should be a subsection
    if any(word in heading_text.lower() for word in ['config', 'setup', 'install', 'create', 'start']):
        return True
    
    # If it's a specific component or feature, it should be a subsection
    if any(word in heading_text.lower() for word in ['log', 'metric', 'health', 'monitor', 'alert']):
        return True
    
    # If it's a maintenance or troubleshooting step, it should be a subsection
    if any(word in heading_text.lower() for word in ['backup', 'restore', 'optimize', 'maintain', 'troubleshoot']):
        return True
    
    # If it's a deployment or scaling step, it should be a subsection
    if any(word in heading_text.lower() for word in ['production', 'scaling', 'deployment']):
        return True
    
    # If it's a conclusion or overview, it should be a subsection
    if any(word in heading_text.lower() for word in ['conclusion', 'overview']):
        return True
    
    # If it's a connection or issue related heading, it should be a subsection
    if any(word in heading_text.lower() for word in ['connection', 'issue', 'problem', 'error']):
        return True
    
    # If it's a monitoring or performance related heading, it should be a subsection
    if any(word in heading_text.lower() for word in ['monitor', 'performance', 'resource', 'usage']):
        return True
    
    # If it's a security related heading, it should be a subsection
    if any(word in heading_text.lower() for word in ['security', 'authentication', 'authorization']):
        return True
    
    # If it's a command or action, it should be a subsection
    if any(word in heading_text.lower() for word in ['check', 'test', 'verify', 'validate', 'run', 'execute']):
        return True
    
    # If it's a maintenance or management task, it should be a subsection
    if any(word in heading_text.lower() for word in ['maintain', 'manage', 'control', 'operate']):
        return True
    
    # If it's a specific task or action, it should be a subsection
    if any(word in heading_text.lower() for word in ['task', 'action', 'step', 'procedure', 'process']):
        return True
    
    # If it's a specific component or feature, it should be a subsection
    if any(word in heading_text.lower() for word in ['component', 'feature', 'module', 'system', 'service']):
        return True
    
    # If it's a specific type of data or resource, it should be a subsection
    if any(word in heading_text.lower() for word in ['data', 'resource', 'file', 'directory', 'path']):
        return True
    
    return False

def update_document_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    modified = False
    in_code_block = False
    current_section = None
    new_lines = []
    
    for i, line in enumerate(lines):
        # Track code blocks
        if line.startswith('```'):
            in_code_block = not in_code_block
            new_lines.append(line)
            continue
        
        if in_code_block:
            new_lines.append(line)
            continue
            
        if line.startswith('#'):
            current_level = len(re.match(r'^#+', line).group())
            heading_text = line[current_level:].strip()
            
            # Handle main document title
            if heading_text.endswith(('Guide', 'Setup Guide')):
                new_lines.append(f"# {heading_text}")
                modified = True
                continue
            
            # Handle numbered sections
            if re.match(r'^\d+\.', heading_text):
                current_section = heading_text
                new_lines.append(f"## {heading_text}")
                modified = True
                continue
            
            # Handle subsections
            if is_subsection(heading_text, current_section):
                new_lines.append(f"### {heading_text}")
                modified = True
                continue
            
            # Handle other sections
            if current_level == 1:
                new_lines.append(f"## {heading_text}")
                modified = True
            elif current_level > 2:
                new_lines.append(f"### {heading_text}")
                modified = True
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        return True
    return False

def main():
    planning_dir = Path("planning")
    target_files = ['deployment.md', 'monitoring.md']
    updated_files = []
    
    print("\nUpdating document content structure:")
    print("1. Ensuring consistent heading levels")
    print("2. Converting code blocks to proper subsections")
    print("3. Maintaining document flow and readability")
    
    for file_name in target_files:
        file_path = planning_dir / file_name
        if file_path.exists():
            if update_document_content(file_path):
                updated_files.append(file_name)
    
    if updated_files:
        print("\nUpdated content structure in the following files:")
        for file in updated_files:
            print(f"  - {file}")
    else:
        print("No files needed updating.")

if __name__ == "__main__":
    main() 