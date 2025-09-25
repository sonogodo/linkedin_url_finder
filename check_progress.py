import json
import glob
import os
import pandas as pd
from datetime import datetime

def is_recent_graduate(graduation_date_str):
    """Check if graduate is from current year (2025) or previous year (2024)."""
    try:
        from datetime import datetime
        current_year = datetime.now().year
        
        # Parse the graduation date (DD/MM/YYYY format)
        graduation_date = datetime.strptime(graduation_date_str, '%d/%m/%Y')
        graduation_year = graduation_date.year
        
        # Only accept graduates from current year or previous year
        return graduation_year >= current_year - 1  # 2024 and 2025
        
    except Exception:
        return False

def check_progress():
    """Check current progress of LinkedIn searches (recent graduates only)."""
    print("📊 LinkedIn Search Progress Report (2024-2025 Graduates)")
    print("=" * 60)
    
    # Load CSV to get total count and filter recent graduates
    try:
        df = pd.read_csv('new_graduates.csv', encoding='utf-8')
        total_records = len(df)
        
        # Filter for recent graduates only
        recent_graduates = df[df['Data da Colação'].apply(is_recent_graduate)]
        recent_count = len(recent_graduates)
        
        print(f"📋 Total records in CSV: {total_records}")
        print(f"🎯 Recent graduates (2024-2025): {recent_count}")
        print(f"📊 Filtering to recent graduates: {recent_count/total_records*100:.1f}% of dataset")
        
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return
    
    # Check master success file
    master_file = 'linkedin_success_master.json'
    
    if not os.path.exists(master_file):
        print("📝 No master success file found yet")
        return
    
    try:
        with open(master_file, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        # Get file modification time
        mod_time = os.path.getmtime(master_file)
        mod_datetime = datetime.fromtimestamp(mod_time)
        
        print(f"\n📄 Master success file: {master_file}")
        print(f"🕒 Last updated: {mod_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Summary (based on recent graduates only)
        print(f"\n📈 PROGRESS (Recent Graduates 2024-2025):")
        print(f"   ✅ Unique profiles found: {len(master_data)}")
        print(f"   📊 Progress: {len(master_data)}/{recent_count} ({len(master_data)/recent_count*100:.1f}%)")
        print(f"   📋 Remaining recent graduates: {recent_count - len(master_data)} records")
        
        # Show sample of found profiles
        if master_data:
            print(f"\n🎯 Recent profiles found:")
            
            # Show last 10 added profiles
            recent_profiles = master_data[-10:] if len(master_data) >= 10 else master_data
            
            for i, record in enumerate(recent_profiles, 1):
                name = record.get('Nome', '')
                url = record.get('LinkedIn URL', '')
                updated = record.get('Last Updated', '')
                print(f"   {i:2d}. {name:<30} -> {url}")
                print(f"       Updated: {updated}")
            
            if len(master_data) > 10:
                print(f"   ... showing last 10 of {len(master_data)} total profiles")
        
        # Clean and simple - only show master file info
    
    except Exception as e:
        print(f"❌ Error reading master file: {e}")

if __name__ == "__main__":
    check_progress()