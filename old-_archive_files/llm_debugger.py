#!/usr/bin/env python
# llm_debugger.py - Command-line debugger for ICMP LLM system

import os
import sys
import json
import argparse
import requests
from datetime import datetime
from tabulate import tabulate
from colorama import Fore, Style, init
import time

# Initialize colorama
init(autoreset=True)

# Default configuration
DEFAULT_API_BASE_URL = 'http://127.0.0.1:5000'
DEFAULT_BUSINESS_ID = '7ae167a0-d864-43b9-bdaf-fcba35b33f27'
DEFAULT_API_KEY = 'da828cae6a3e46228aa09d65ba9066e3'

class LLMDebugger:
    """Command-line debugger for ICMP LLM system"""
    
    def __init__(self, api_base_url, business_id, api_key, owner_id=None):
        """Initialize the debugger with API credentials"""
        self.api_base_url = api_base_url
        self.business_id = business_id
        self.api_key = api_key
        self.owner_id = owner_id
        self.is_logged_in = False
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'businessapikey': api_key
        })
    
    def login(self):
        """Login to the API using business ID and API key"""
        if not self.owner_id:
            print(f"{Fore.YELLOW}No owner ID provided. Attempting to look up owner...{Style.RESET_ALL}")
            self.lookup_owner()
        
        if not self.owner_id:
            print(f"{Fore.RED}Failed to get owner ID. Cannot login.{Style.RESET_ALL}")
            return False
        
        url = f"{self.api_base_url}/api/verify-owner"
        data = {
            "userId": self.owner_id,
            "businessId": self.business_id,
            "businessApiKey": self.api_key
        }
        
        try:
            response = self.session.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.is_logged_in = True
                    print(f"{Fore.GREEN}Login successful!{Style.RESET_ALL}")
                    return True
                else:
                    print(f"{Fore.RED}Login failed: {result.get('error', 'Unknown error')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Login failed with status code: {response.status_code}{Style.RESET_ALL}")
                try:
                    error_data = response.json()
                    print(f"{Fore.RED}Error: {error_data.get('error', 'Unknown error')}{Style.RESET_ALL}")
                except:
                    print(f"{Fore.RED}Error: {response.text}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Login error: {str(e)}{Style.RESET_ALL}")
        
        return False
    
    def lookup_owner(self):
        """Look up the owner ID for the business"""
        url = f"{self.api_base_url}/api/lookup-owner"
        data = {
            "businessId": self.business_id,
            "businessApiKey": self.api_key
        }
        
        try:
            response = self.session.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.owner_id = result.get('owner_id')
                    print(f"{Fore.GREEN}Owner ID found: {self.owner_id}{Style.RESET_ALL}")
                    return True
                else:
                    print(f"{Fore.RED}Lookup failed: {result.get('error', 'Unknown error')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Lookup failed with status code: {response.status_code}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Lookup error: {str(e)}{Style.RESET_ALL}")
        
        return False
    
    def make_llm_call(self, input_text, system_prompt=None, call_type="general"):
        """Make an LLM call to the API"""
        if not self.is_logged_in:
            print(f"{Fore.YELLOW}Not logged in. Attempting to login...{Style.RESET_ALL}")
            if not self.login():
                print(f"{Fore.RED}Login failed. Cannot make LLM call.{Style.RESET_ALL}")
                return None
        
        url = f"{self.api_base_url}/api/llm/generate"
        data = {
            "business_id": self.business_id,
            "input_text": input_text,
            "system_prompt": system_prompt,
            "call_type": call_type
        }
        
        try:
            print(f"{Fore.CYAN}Making LLM call...{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Input text: {input_text}{Style.RESET_ALL}")
            if system_prompt:
                print(f"{Fore.CYAN}System prompt: {system_prompt}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Call type: {call_type}{Style.RESET_ALL}")
            
            start_time = datetime.now()
            response = self.session.post(url, json=data)
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds() * 1000  # in milliseconds
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"{Fore.GREEN}LLM call successful!{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}Processing time: {processing_time:.2f} ms{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}Response:{Style.RESET_ALL}")
                    print(f"{Fore.WHITE}{result.get('response', '')}{Style.RESET_ALL}")
                    return result
                else:
                    print(f"{Fore.RED}LLM call failed: {result.get('error', 'Unknown error')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}LLM call failed with status code: {response.status_code}{Style.RESET_ALL}")
                try:
                    error_data = response.json()
                    print(f"{Fore.RED}Error: {error_data.get('error', 'Unknown error')}{Style.RESET_ALL}")
                except:
                    print(f"{Fore.RED}Error: {response.text}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}LLM call error: {str(e)}{Style.RESET_ALL}")
        
        return None
    
    def get_recent_calls(self, limit=10):
        """Get recent LLM calls"""
        if not self.is_logged_in:
            print(f"{Fore.YELLOW}Not logged in. Attempting to login...{Style.RESET_ALL}")
            if not self.login():
                print(f"{Fore.RED}Login failed. Cannot get recent calls.{Style.RESET_ALL}")
                return None
        
        url = f"{self.api_base_url}/api/llm/calls/recent?business_id={self.business_id}&limit={limit}"
        
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                calls = response.json()
                if calls:
                    print(f"{Fore.GREEN}Found {len(calls)} recent LLM calls:{Style.RESET_ALL}")
                    
                    # Prepare data for tabulate
                    table_data = []
                    for call in calls:
                        timestamp = datetime.fromisoformat(call.get('timestamp', '')).strftime('%Y-%m-%d %H:%M:%S') if call.get('timestamp') else 'N/A'
                        table_data.append([
                            call.get('call_id', 'N/A'),
                            call.get('call_type', 'general'),
                            timestamp,
                            call.get('input_text', '')[:50] + '...' if len(call.get('input_text', '')) > 50 else call.get('input_text', '')
                        ])
                    
                    # Print table
                    print(tabulate(table_data, headers=['Call ID', 'Type', 'Timestamp', 'Input Text'], tablefmt='grid'))
                    return calls
                else:
                    print(f"{Fore.YELLOW}No recent LLM calls found.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Failed to get recent calls with status code: {response.status_code}{Style.RESET_ALL}")
                try:
                    error_data = response.json()
                    print(f"{Fore.RED}Error: {error_data.get('error', 'Unknown error')}{Style.RESET_ALL}")
                except:
                    print(f"{Fore.RED}Error: {response.text}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error getting recent calls: {str(e)}{Style.RESET_ALL}")
        
        return None
    
    def get_call_details(self, call_id):
        """Get details for a specific LLM call"""
        if not self.is_logged_in:
            print(f"{Fore.YELLOW}Not logged in. Attempting to login...{Style.RESET_ALL}")
            if not self.login():
                print(f"{Fore.RED}Login failed. Cannot get call details.{Style.RESET_ALL}")
                return None
        
        url = f"{self.api_base_url}/api/llm/calls/{call_id}?business_id={self.business_id}"
        
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                call = response.json()
                if call:
                    print(f"{Fore.GREEN}Call details for ID: {call_id}{Style.RESET_ALL}")
                    
                    # Print call details
                    print(f"{Fore.CYAN}Call ID:{Style.RESET_ALL} {call.get('call_id', 'N/A')}")
                    print(f"{Fore.CYAN}Call Type:{Style.RESET_ALL} {call.get('call_type', 'general')}")
                    print(f"{Fore.CYAN}Timestamp:{Style.RESET_ALL} {call.get('timestamp', 'N/A')}")
                    
                    print(f"\n{Fore.CYAN}Input Text:{Style.RESET_ALL}")
                    print(f"{Fore.WHITE}{call.get('input_text', 'N/A')}{Style.RESET_ALL}")
                    
                    if call.get('system_prompt'):
                        print(f"\n{Fore.CYAN}System Prompt:{Style.RESET_ALL}")
                        print(f"{Fore.WHITE}{call.get('system_prompt')}{Style.RESET_ALL}")
                    
                    print(f"\n{Fore.CYAN}Response:{Style.RESET_ALL}")
                    print(f"{Fore.WHITE}{call.get('response', 'N/A')}{Style.RESET_ALL}")
                    
                    # Print performance metrics
                    print(f"\n{Fore.CYAN}Performance Metrics:{Style.RESET_ALL}")
                    print(f"{Fore.WHITE}Processing Time: {call.get('processing_time_ms', 'N/A')} ms{Style.RESET_ALL}")
                    print(f"{Fore.WHITE}Token Usage: {call.get('token_usage', 'N/A')} tokens{Style.RESET_ALL}")
                    print(f"{Fore.WHITE}Estimated Cost: ${call.get('estimated_cost', 'N/A')}{Style.RESET_ALL}")
                    
                    return call
                else:
                    print(f"{Fore.YELLOW}No call details found for ID: {call_id}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Failed to get call details with status code: {response.status_code}{Style.RESET_ALL}")
                try:
                    error_data = response.json()
                    print(f"{Fore.RED}Error: {error_data.get('error', 'Unknown error')}{Style.RESET_ALL}")
                except:
                    print(f"{Fore.RED}Error: {response.text}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error getting call details: {str(e)}{Style.RESET_ALL}")
        
        return None
    
    def check_api_health(self):
        """Check if the API server is running"""
        url = f"{self.api_base_url}/health"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                print(f"{Fore.GREEN}API server is running. Database: {data.get('database', 'Unknown')}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}API server returned status: {response.status_code}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}API server check failed: {str(e)}{Style.RESET_ALL}")
        
        return False
    
    def watch_calls(self, interval=5):
        """Continuously watch for new LLM calls"""
        if not self.is_logged_in:
            print(f"{Fore.YELLOW}Not logged in. Attempting to login...{Style.RESET_ALL}")
            if not self.login():
                print(f"{Fore.RED}Login failed. Cannot watch calls.{Style.RESET_ALL}")
                return
        
        print(f"{Fore.GREEN}Watching for new LLM calls (checking every {interval} seconds)...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Press Ctrl+C to stop watching{Style.RESET_ALL}")
        
        last_call_id = None
        try:
            while True:
                calls = self.get_recent_calls(limit=1)
                if calls and calls[0]['call_id'] != last_call_id:
                    last_call_id = calls[0]['call_id']
                    print(f"\n{Fore.CYAN}New LLM Call Detected:{Style.RESET_ALL}")
                    print(f"Call ID: {calls[0]['call_id']}")
                    print(f"Timestamp: {calls[0]['timestamp']}")
                    print(f"Type: {calls[0]['call_type']}")
                    print(f"Input: {calls[0]['input_text']}")
                    print(f"Response: {calls[0]['response']}")
                    print("-" * 80)
                
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Stopped watching LLM calls{Style.RESET_ALL}")

def main():
    """Main function for the command-line interface"""
    parser = argparse.ArgumentParser(description='ICMP LLM API Debugger')
    parser.add_argument('--api-url', default=DEFAULT_API_BASE_URL, help='API base URL')
    parser.add_argument('--business-id', default=DEFAULT_BUSINESS_ID, help='Business ID')
    parser.add_argument('--api-key', default=DEFAULT_API_KEY, help='API Key')
    parser.add_argument('--owner-id', help='Owner ID (optional)')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Login command
    login_parser = subparsers.add_parser('login', help='Login to the API')
    
    # Make LLM call command
    call_parser = subparsers.add_parser('call', help='Make an LLM call')
    call_parser.add_argument('--input', required=True, help='Input text for the LLM')
    call_parser.add_argument('--system-prompt', help='System prompt (optional)')
    call_parser.add_argument('--type', default='general', choices=['general', 'stage_selection', 'data_extraction', 'response_generation'], 
                            help='Call type')
    
    # Get recent calls command
    recent_parser = subparsers.add_parser('recent', help='Get recent LLM calls')
    recent_parser.add_argument('--limit', type=int, default=10, help='Number of calls to retrieve')
    
    # Get call details command
    details_parser = subparsers.add_parser('details', help='Get details for a specific LLM call')
    details_parser.add_argument('--call-id', required=True, help='Call ID')
    
    # Health check command
    health_parser = subparsers.add_parser('health', help='Check API health')
    
    # Watch command for continuous monitoring
    watch_parser = subparsers.add_parser('watch', help='Continuously watch for new LLM calls')
    watch_parser.add_argument('--interval', type=int, default=5, help='Check interval in seconds')
    
    args = parser.parse_args()
    
    # Create debugger instance
    debugger = LLMDebugger(args.api_url, args.business_id, args.api_key, args.owner_id)
    
    # Check API health first
    if not debugger.check_api_health():
        print(f"{Fore.RED}API server is not running. Please start the server and try again.{Style.RESET_ALL}")
        return
    
    # Execute command
    if args.command == 'login':
        debugger.login()
    elif args.command == 'call':
        debugger.make_llm_call(args.input, args.system_prompt, args.type)
    elif args.command == 'recent':
        debugger.get_recent_calls(args.limit)
    elif args.command == 'details':
        debugger.get_call_details(args.call_id)
    elif args.command == 'health':
        debugger.check_api_health()
    elif args.command == 'watch':
        debugger.watch_calls(args.interval)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()