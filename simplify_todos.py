import json
import re
import sys
from datetime import datetime, timedelta

def load_json_file(file_path):
    """Load JSON data from file with UTF-8-SIG encoding to handle BOM characters"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                if not content.strip().startswith('['):
                    content = '[' + content
                if not content.strip().endswith(']'):
                    content = content + ']'
                return json.loads(content)
        except Exception as e2:
            print(f"Failed to load JSON manually: {e2}")
            raise

def save_json_file(data, file_path):
    """Save JSON data to file with nice formatting"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def parse_date(date_str):
    """Parse a date string into a standardized ISO format and datetime object"""
    if not date_str or date_str == '{}' or date_str == '0001-01-01T00:00:00':
        return None, None
    
    # Parse DD-MMM-YY HH:MM:SS AM/PM format (26-Dec-24 11:52:18 AM)
    match = re.match(r'(\d{2})-(\w{3})-(\d{2})\s+(\d{1,2}):(\d{2}):(\d{2})\s+([AP]M)', str(date_str))
    if match:
        day, month_abbr, year, hour, minute, second, ampm = match.groups()
        
        # Convert month abbreviation to number
        months = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        month = months.get(month_abbr, 1)
        
        # Convert hour to 24-hour format
        hour = int(hour)
        if ampm == 'PM' and hour < 12:
            hour += 12
        elif ampm == 'AM' and hour == 12:
            hour = 0
        
        # Assume 20xx for two-digit years
        full_year = 2000 + int(year)
        
        # Create datetime object
        try:
            dt = datetime(full_year, month, int(day), hour, int(minute), int(second))
            iso_format = dt.isoformat(timespec='seconds').replace('+00:00', '').replace('Z', '')
            return iso_format, dt
        except ValueError:
            return None, None
    
    # Parse ISO format YYYY-MM-DDTHH:MM:SS
    match = re.match(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})', str(date_str))
    if match:
        year, month, day, hour, minute, second = match.groups()
        try:
            dt = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
            return date_str, dt
        except ValueError:
            return None, None
    
    return None, None

def are_dates_similar(date1, date2, threshold_minutes=2):
    """Check if two datetime objects are within a threshold of each other"""
    if date1 is None or date2 is None:
        return False
    
    time_diff = abs((date1 - date2).total_seconds())
    return time_diff <= threshold_minutes * 60

def format_day_of_date(dt):
    """Format a datetime object to YYYY-MM-DD format for day-only representation"""
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d')

def simplify_todo_item(item):
    """Simplify a todo item, keeping only essential fields and day-based date fields"""
    simplified = {}
    
    # Only keep these essential fields
    essential_fields = [
        "Subject", "Body", "IsComplete", "FolderName", "Creator"
    ]
    
    # Add essential fields if they exist
    for field in essential_fields:
        if field in item:
            simplified[field] = item[field]
    
    # Add Folder name if not already there
    if "FolderName" not in simplified:
        if "Folder" in item:
            simplified["FolderName"] = item["Folder"]
        elif "undocumented 0x0e05" in item:
            simplified["FolderName"] = item["undocumented 0x0e05"]
    
    # Add creator name if not already there
    if "Creator" not in simplified:
        if "CreatorName" in item:
            simplified["Creator"] = item["CreatorName"]
        elif "CreatorSimpleDisplayName" in item:
            simplified["Creator"] = item["CreatorSimpleDisplayName"]
    
    # List of specific date keys to check
    date_keys = [
        "CreationTime", 
        "LastModificationTime", 
        "ClientSubmitTime", 
        "MessageDeliveryTime", 
        "Last Modification Time", 
        "PSETID_Task: DoItTime"
    ]
    
    # Collect dates from specific keys only
    date_fields = {}
    all_date_objects = []  # Store all valid dates for determining oldest/newest
    
    for key in date_keys:
        if key in item and item[key] and item[key] != "{}" and item[key] != "0001-01-01T00:00:00":
            iso_format, dt_obj = parse_date(item[key])
            if iso_format and dt_obj:
                date_fields[key] = {
                    'original': item[key],
                    'iso': iso_format,
                    'datetime': dt_obj
                }
                all_date_objects.append(dt_obj)
    
    # Determine DateOfCreation and DateOfModification from all dates
    if all_date_objects:
        # Sort all dates from oldest to newest
        all_date_objects.sort()
        
        # Set DateOfCreation to the oldest date
        oldest_date = all_date_objects[0]
        simplified["DateOfCreation"] = oldest_date.isoformat(timespec='seconds')
        
        # Set DateOfModification to the newest date
        newest_date = all_date_objects[-1]
        simplified["DateOfModification"] = newest_date.isoformat(timespec='seconds')
    
    return simplified

def simplify_todos(data):
    """Convert full todo items to simplified versions"""
    simplified_data = []
    
    total_items = len(data)
    print(f"Simplifying {total_items} todo items...")
    
    for i, item in enumerate(data):
        simplified_item = simplify_todo_item(item)
        simplified_data.append(simplified_item)
        
        if (i+1) % 1000 == 0:
            print(f"Processed {i+1}/{total_items} items...")
    
    return simplified_data

def analyze_results(data):
    """Analyze the simplified data"""
    field_counts = {}
    
    for item in data:
        for field in item.keys():
            if field not in field_counts:
                field_counts[field] = 0
            field_counts[field] += 1
    
    total = len(data)
    print("\n--- SIMPLIFIED DATA ANALYSIS ---")
    print(f"Total items: {total}")
    print("\nFields preserved:")
    
    # Sort fields by frequency
    for field, count in sorted(field_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total) * 100
        print(f"  {field}: {count}/{total} items ({percentage:.2f}%)")
    
    # Show date fields analysis
    date_fields = ["DateOfCreation", "DateOfModification"]
    print("\n--- DATE FIELDS ANALYSIS ---")
    for field in date_fields:
        count = field_counts.get(field, 0)
        percentage = (count / total) * 100 if total > 0 else 0
        print(f"  {field}: {count}/{total} items ({percentage:.2f}%)")
    
    # Sample items
    print("\n--- SAMPLE SIMPLIFIED ITEMS ---")
    import random
    samples = random.sample(data, min(3, len(data)))
    
    for i, sample in enumerate(samples, 1):
        print(f"\nSample {i}:")
        for key, value in sorted(sample.items()):
            print(f"  {key}: {value}")

def main():
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "data/todos_full.json"
    
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = "data/todos_simple.json"
    
    # Load data
    data = load_json_file(input_file)
    
    # Simplify data
    simplified_data = simplify_todos(data)
    
    # Save simplified data
    save_json_file(simplified_data, output_file)
    print(f"\nSaved simplified data to {output_file}")
    
    # Analyze results
    analyze_results(simplified_data)

if __name__ == "__main__":
    main() 