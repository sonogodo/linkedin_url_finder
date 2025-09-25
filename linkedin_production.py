import pandas as pd
import time
import json
import glob
import uuid
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import os
import random

def setup_driver():
    """Setup Chrome driver optimized for production."""
    chrome_options = Options()
    
    # Performance optimizations
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-images")  # Don't load images for speed
    chrome_options.add_argument("--disable-javascript")  # Disable JS for faster loading
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Stealth options
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Suppress logs
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    try:
        service = Service("./chromedriver.exe")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"❌ Error setting up driver: {e}")
        return None

def generate_unique_id(existing_ids):
    """Generate a unique ID that doesn't exist in the current dataset."""
    import uuid
    while True:
        new_id = str(uuid.uuid4())[:8]  # Use first 8 characters of UUID
        if new_id not in existing_ids:
            return new_id

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
        # If date parsing fails, exclude the record
        return False

def update_master_success_file(new_success_records, existing_data):
    """Update the master success file with new records and unique IDs (recent graduates only)."""
    master_file = 'linkedin_success_master.json'
    
    # Filter existing data to only include recent graduates
    recent_existing_data = [
        record for record in existing_data 
        if is_recent_graduate(record.get('Data da Colação', ''))
    ]
    
    # Get existing URLs and IDs from recent graduates only
    existing_urls = {record.get('LinkedIn URL', '') for record in recent_existing_data}
    existing_ids = {record.get('id', '') for record in recent_existing_data if record.get('id')}
    
    # Add new successful records with unique IDs (only recent graduates)
    added_count = 0
    for record in new_success_records:
        linkedin_url = record.get('LinkedIn URL', '')
        graduation_date = record.get('Data da Colação', '')
        
        # Only add if it's a recent graduate and URL is not already present
        if (linkedin_url and linkedin_url not in existing_urls and 
            is_recent_graduate(graduation_date)):
            
            # Generate unique ID for this profile
            unique_id = generate_unique_id(existing_ids)
            existing_ids.add(unique_id)
            
            recent_existing_data.append({
                'id': unique_id,
                'Nome': record['Nome'],
                'Curso': record['Curso'],
                'Faculdade': record['Faculdade'],
                'Data da Colação': graduation_date,
                'LinkedIn URL': linkedin_url,
                'Last Updated': record['Last Updated']
            })
            existing_urls.add(linkedin_url)
            added_count += 1
    
    # Save updated master file (only recent graduates)
    try:
        with open(master_file, 'w', encoding='utf-8') as f:
            json.dump(recent_existing_data, f, ensure_ascii=False, indent=2)
        
        if added_count > 0:
            print(f"   📅 Added {added_count} recent graduates (2024-2025) to master file")
        
        return len(recent_existing_data)
    except Exception as e:
        print(f"❌ Error saving master file: {e}")
        return len(recent_existing_data)

def search_linkedin_profile(driver, name, university):
    """Search for LinkedIn profile with optimized query."""
    query = f"linkedin {name} {university}"
    
    try:
        # Navigate to DuckDuckGo
        driver.get("https://duckduckgo.com")
        
        # Find and use search box
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        
        search_box.clear()
        search_box.send_keys(query)
        search_box.submit()
        
        # Wait for results
        time.sleep(2)
        
        # Parse results
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract LinkedIn URLs
        linkedin_urls = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'linkedin.com/in/' in href:
                if '/l/?uddg=' in href:
                    try:
                        import urllib.parse
                        actual_url = urllib.parse.unquote(href.split('uddg=')[1])
                        if actual_url.startswith('http'):
                            linkedin_urls.append(actual_url)
                    except:
                        pass
                elif href.startswith('http'):
                    linkedin_urls.append(href)
        
        # Clean and return best result
        clean_urls = []
        for url in linkedin_urls:
            clean_url = url.split('?')[0].split('#')[0]
            if clean_url not in clean_urls and 'linkedin.com/in/' in clean_url:
                clean_urls.append(clean_url)
        
        return clean_urls[0] if clean_urls else None
        
    except Exception as e:
        print(f"      Search error: {e}")
        return None

def process_batch(driver, df_batch, batch_num, total_batches, existing_names=None):
    """Process a batch of records with smart skipping."""
    print(f"\n📦 Batch {batch_num}/{total_batches} - Processing {len(df_batch)} records")
    print("-" * 60)
    
    results = []
    found_count = 0
    skipped_count = 0
    
    for idx, row in df_batch.iterrows():
        name = row.get('Nome', '').strip()
        course = row.get('Curso', '')
        university = row.get('Faculdade', '')
        graduation_date = row.get('Data da Colação', '')
        
        print(f"[{idx+1:3d}] {name[:35]:<35} ", end='', flush=True)
        
        if not name:
            print("❌ No name")
            continue
        
        # Skip if already processed (double-check for production mode)
        if existing_names and name in existing_names:
            print("⏭️  Already processed")
            skipped_count += 1
            continue
        
        # Search for LinkedIn profile
        linkedin_url = search_linkedin_profile(driver, name, university)
        
        # Prepare result
        result = {
            'Nome': name,
            'Curso': course,
            'Faculdade': university,
            'Data da Colação': graduation_date,
            'LinkedIn URL': linkedin_url or '',
            'Match Status': 'Found' if linkedin_url else 'Not Found',
            'Last Updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        results.append(result)
        
        if linkedin_url:
            print(f"✅ Found")
            found_count += 1
            # Add to existing names to avoid future duplicates in same session
            if existing_names is not None:
                existing_names.add(name)
        else:
            print(f"❌ Not found")
        
        # Random delay to avoid rate limiting
        delay = random.uniform(2, 4)
        time.sleep(delay)
    
    processed_count = len(df_batch) - skipped_count
    if skipped_count > 0:
        print(f"\nBatch {batch_num} complete: {found_count}/{processed_count} found ({found_count/processed_count*100:.1f}%), {skipped_count} skipped")
    else:
        print(f"\nBatch {batch_num} complete: {found_count}/{len(df_batch)} found ({found_count/len(df_batch)*100:.1f}%)")
    
    return results, found_count

def load_existing_results():
    """Load existing success results from the master file (recent graduates only)."""
    existing_names = set()
    existing_urls = set()
    existing_data = []
    
    master_file = 'linkedin_success_master.json'
    
    if os.path.exists(master_file):
        try:
            with open(master_file, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
            
            # Filter to only include recent graduates (2024-2025)
            recent_data = []
            for record in all_data:
                graduation_date = record.get('Data da Colação', '')
                if is_recent_graduate(graduation_date):
                    recent_data.append(record)
                    existing_names.add(record.get('Nome', '').strip())
                    existing_urls.add(record.get('LinkedIn URL', '').strip())
            
            existing_data = recent_data
            
            # If we filtered out old graduates, update the master file
            if len(recent_data) < len(all_data):
                filtered_count = len(all_data) - len(recent_data)
                print(f"🔄 Filtered out {filtered_count} older graduates (keeping only 2024-2025)")
                
                # Save the filtered data back to master file
                with open(master_file, 'w', encoding='utf-8') as f:
                    json.dump(recent_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Loaded {len(existing_data)} recent graduates (2024-2025) from {master_file}")
            
        except Exception as e:
            print(f"❌ Error loading {master_file}: {e}")
            existing_data = []
    else:
        print("📝 No existing master file found - starting fresh")
    
    return existing_names, existing_urls, existing_data

def main():
    print("🚀 LinkedIn Production Search")
    print("=" * 50)
    
    # Load CSV
    try:
        df = pd.read_csv('new_graduates.csv', encoding='utf-8')
        print(f"📊 Loaded {len(df)} records")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return
    
    # Load existing results to avoid duplicates
    existing_names, existing_urls, existing_data = load_existing_results()
    
    # Filter dataset to only include recent graduates (2024-2025)
    df['is_recent'] = df['Data da Colação'].apply(is_recent_graduate)
    recent_df = df[df['is_recent']].copy()
    total_recent = len(recent_df)
    
    print(f"🎯 Filtered to recent graduates (2024-2025): {total_recent}/{len(df)} records ({total_recent/len(df)*100:.1f}%)")
    
    # Get processing options based on recent graduates only
    remaining_count = total_recent - len(existing_names)
    print(f"\nProcessing options ({remaining_count} recent unprocessed records remaining):")
    print(f"1. Quick test (next 10 recent unprocessed)")
    print(f"2. Small batch (next 50 recent unprocessed)")
    print(f"3. Medium batch (next 200 recent unprocessed)")
    print(f"4. Large batch (next 500 recent unprocessed)")
    print(f"5. 🚀 PRODUCTION MODE - All remaining recent unprocessed records")
    print(f"6. Custom amount (specify how many recent unprocessed)")
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    # Helper function to get next unprocessed recent graduates
    def get_next_unprocessed(df, existing_names, max_count):
        """Get the next unprocessed recent graduates up to max_count."""
        unprocessed = df[~df['Nome'].str.strip().isin(existing_names)]
        
        if len(unprocessed) == 0:
            return unprocessed, 0
        
        actual_count = min(len(unprocessed), max_count)
        return unprocessed.head(actual_count), actual_count
    
    if choice == '1':
        df_to_process, actual_count = get_next_unprocessed(recent_df, existing_names, 10)
        skip_existing = True
        if actual_count == 0:
            print("✅ All recent graduates already processed! No new users to search.")
            return
        elif actual_count < 10:
            print(f"📊 Found {actual_count} remaining recent unprocessed records (less than 10 requested)")
        else:
            print(f"📊 Found next {actual_count} recent unprocessed records for quick test")
    elif choice == '2':
        df_to_process, actual_count = get_next_unprocessed(recent_df, existing_names, 50)
        skip_existing = True
        if actual_count == 0:
            print("✅ All recent graduates already processed! No new users to search.")
            return
        elif actual_count < 50:
            print(f"📊 Found {actual_count} remaining recent unprocessed records (less than 50 requested)")
        else:
            print(f"📊 Found next {actual_count} recent unprocessed records for small batch")
    elif choice == '3':
        df_to_process, actual_count = get_next_unprocessed(recent_df, existing_names, 200)
        skip_existing = True
        if actual_count == 0:
            print("✅ All recent graduates already processed! No new users to search.")
            return
        elif actual_count < 200:
            print(f"📊 Found {actual_count} remaining recent unprocessed records (less than 200 requested)")
        else:
            print(f"📊 Found next {actual_count} recent unprocessed records for medium batch")
    elif choice == '4':
        df_to_process, actual_count = get_next_unprocessed(recent_df, existing_names, 500)
        skip_existing = True
        if actual_count == 0:
            print("✅ All recent graduates already processed! No new users to search.")
            return
        elif actual_count < 500:
            print(f"📊 Found {actual_count} remaining recent unprocessed records (less than 500 requested)")
        else:
            print(f"📊 Found next {actual_count} recent unprocessed records for large batch")
    elif choice == '5':
        df_to_process = recent_df
        skip_existing = True
        print("🚀 PRODUCTION MODE ACTIVATED (Recent Graduates Only)")
        print("   - Will skip people already found")
        print("   - Will process all recent graduates (2024-2025) efficiently")
        print("   - Can be safely interrupted and resumed")
    elif choice == '6':
        try:
            count = int(input("How many recent unprocessed records to search: "))
            df_to_process, actual_count = get_next_unprocessed(recent_df, existing_names, count)
            skip_existing = True
            if actual_count == 0:
                print("✅ All recent graduates already processed! No new users to search.")
                return
            elif actual_count < count:
                print(f"📊 Found {actual_count} remaining recent unprocessed records (less than {count} requested)")
            else:
                print(f"📊 Found next {actual_count} recent unprocessed records for custom batch")
        except ValueError:
            print("❌ Invalid number entered. Using default 10 records.")
            df_to_process, actual_count = get_next_unprocessed(recent_df, existing_names, 10)
            skip_existing = True
            if actual_count == 0:
                print("✅ All recent graduates already processed! No new users to search.")
                return
    else:
        df_to_process, actual_count = get_next_unprocessed(recent_df, existing_names, 10)
        skip_existing = True
        if actual_count == 0:
            print("✅ All recent graduates already processed! No new users to search.")
            return
    
    # For production mode, still need to filter since we process the full recent dataset
    if choice == '5' and skip_existing and existing_names:
        original_count = len(df_to_process)
        df_to_process = df_to_process[~df_to_process['Nome'].str.strip().isin(existing_names)]
        skipped_count = original_count - len(df_to_process)
        
        print(f"\n📊 Production mode filtering (Recent Graduates):")
        print(f"   📋 Total recent graduates: {original_count}")
        print(f"   ⏭️  Already processed: {skipped_count}")
        print(f"   🎯 Remaining to process: {len(df_to_process)}")
        
        if len(df_to_process) == 0:
            print("✅ All recent graduates already processed! Nothing to do.")
            return
    
    print(f"\n🎯 Processing {len(df_to_process)} records")
    
    # Confirm before large runs
    if len(df_to_process) > 100:
        confirm = input(f"⚠️  This will process {len(df_to_process)} records and may take hours. Continue? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return
    
    # Setup driver
    driver = setup_driver()
    if not driver:
        return
    
    try:
        # Process in batches
        batch_size = 25
        total_records = len(df_to_process)
        total_batches = (total_records + batch_size - 1) // batch_size
        
        all_results = []
        total_found = 0
        
        for i in range(0, total_records, batch_size):
            batch_df = df_to_process.iloc[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            
            batch_results, batch_found = process_batch(
                driver, batch_df, batch_num, total_batches, 
                existing_names if skip_existing else None
            )
            all_results.extend(batch_results)
            total_found += batch_found
            
            # Save intermediate results every 5 batches
            if batch_num % 5 == 0 or batch_num == total_batches:
                # Update master success file with new finds
                new_success_records = [r for r in all_results if r['Match Status'] == 'Found' and r['LinkedIn URL']]
                
                if new_success_records:
                    # Reload existing data to get current state with IDs
                    try:
                        with open('linkedin_success_master.json', 'r', encoding='utf-8') as f:
                            current_existing_data = json.load(f)
                    except:
                        current_existing_data = existing_data
                    
                    total_in_master = update_master_success_file(new_success_records, current_existing_data)
                    print(f"💾 Updated master success file: {total_in_master} total profiles")
                else:
                    print(f"💾 No new successful profiles to add to master file")
            
            # Longer break between batches
            if batch_num < total_batches:
                print(f"⏳ Taking 30-second break before next batch...")
                time.sleep(30)
        
        # Final results
        print(f"\n" + "=" * 60)
        print("🎉 PROCESSING COMPLETE!")
        print("=" * 60)
        print(f"✅ Total found: {total_found}/{total_records} ({total_found/total_records*100:.1f}%)")
        
        # Final update to master success file (no session backup needed)
        new_success_records = [r for r in all_results if r['Match Status'] == 'Found' and r['LinkedIn URL']]
        if new_success_records:
            # Reload existing data to get current state with IDs
            try:
                with open('linkedin_success_master.json', 'r', encoding='utf-8') as f:
                    current_existing_data = json.load(f)
            except:
                current_existing_data = existing_data
            
            total_in_master = update_master_success_file(new_success_records, current_existing_data)
            print(f"💾 Master success file updated: {total_in_master} total unique profiles")
        else:
            print(f"💾 No new profiles found in this session")
        
        # Load and show current master file stats
        try:
            with open('linkedin_success_master.json', 'r', encoding='utf-8') as f:
                master_data = json.load(f)
            
            print(f"🎯 Master file contains {len(master_data)} unique LinkedIn profiles")
            
            # Show sample of found profiles
            if master_data:
                print(f"\n🎯 Sample from master file:")
                for i, result in enumerate(master_data[-10:], 1):  # Show last 10 added
                    print(f"   {i:2d}. {result['Nome']:<30} -> {result['LinkedIn URL']}")
                
                if len(master_data) > 10:
                    print(f"   ... total of {len(master_data)} profiles in master file")
        
        except Exception as e:
            print(f"❌ Error reading master file: {e}")
    
    except KeyboardInterrupt:
        print(f"\n⚠️  Process interrupted by user")
        # Save partial results to master file only
        if 'all_results' in locals() and all_results:
            new_success_records = [r for r in all_results if r['Match Status'] == 'Found' and r['LinkedIn URL']]
            
            if new_success_records:
                total_in_master = update_master_success_file(new_success_records, existing_data)
                print(f"💾 Progress saved to master file: {total_in_master} total profiles")
            else:
                print(f"💾 No new profiles found before interruption")
            
            print("🔄 You can resume by running the script again - it will skip completed work")
    
    except Exception as e:
        print(f"❌ Error during processing: {e}")
    
    finally:
        print("\n🔧 Closing browser...")
        driver.quit()

if __name__ == "__main__":
    main()